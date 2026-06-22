"""Governance: classify tools by sensitivity and decide allow / deny / approval-required."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Sensitivity(str, Enum):
    READ = "read"
    WRITE = "write"


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class PolicyDecision:
    decision: Decision
    reason: str


class PolicyEngine:
    """Role-based policy.

    - READ tools are allowed for any authenticated role.
    - WRITE tools require human approval unless the caller holds an explicitly trusted role.
    - Unknown roles are denied.
    """

    def __init__(self, trusted_roles: set[str] | None = None) -> None:
        self.trusted_roles = trusted_roles or {"system-operator"}
        self.known_roles = {"analyst", "agent", "system-operator"} | self.trusted_roles

    def evaluate(self, role: str, sensitivity: Sensitivity) -> PolicyDecision:
        if role not in self.known_roles:
            return PolicyDecision(Decision.DENY, f"unknown role '{role}'")
        if sensitivity is Sensitivity.READ:
            return PolicyDecision(Decision.ALLOW, "read access permitted")
        if role in self.trusted_roles:
            return PolicyDecision(Decision.ALLOW, f"role '{role}' trusted for writes")
        return PolicyDecision(Decision.REQUIRE_APPROVAL, "write requires human approval")
