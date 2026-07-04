"""Regulated payload redaction — mirrors supplier-negotiation-observability rule sets."""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class RedactionRuleSet(Enum):
    RETAIL = "RETAIL"
    PCI = "PCI"
    HIPAA = "HIPAA"


@dataclass(frozen=True)
class RedactionPolicy:
    sensitive_keys: frozenset[str]
    value_patterns: tuple[re.Pattern[str], ...]
    replacement: str

    @staticmethod
    def retail() -> RedactionPolicy:
        return RedactionPolicy(
            frozenset({"unitCost", "targetMarginPct", "rebatePct", "lumpSumAmount"}),
            (),
            "[REDACTED]",
        )

    @staticmethod
    def pci() -> RedactionPolicy:
        return RedactionPolicy(
            frozenset({
                "pan", "cardNumber", "creditCardNumber", "primaryAccountNumber",
                "cvv", "cvc", "cardSecurityCode", "expiryDate", "expirationDate",
            }),
            (re.compile(r"\b\d{13,19}\b"),),
            "[PCI_REDACTED]",
        )

    @staticmethod
    def hipaa() -> RedactionPolicy:
        return RedactionPolicy(
            frozenset({
                "patientName", "patientId", "mrn", "medicalRecordNumber",
                "ssn", "socialSecurityNumber", "dateOfBirth", "dob",
                "diagnosis", "diagnosisCode", "procedureCode", "phi",
            }),
            (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),),
            "[PHI_REDACTED]",
        )

    @classmethod
    def for_rule_set(cls, rule_set: RedactionRuleSet) -> RedactionPolicy:
        return {
            RedactionRuleSet.RETAIL: cls.retail,
            RedactionRuleSet.PCI: cls.pci,
            RedactionRuleSet.HIPAA: cls.hipaa,
        }[rule_set]()


class PayloadRedactor:
    def __init__(self, policy: RedactionPolicy) -> None:
        self._policy = policy

    @classmethod
    def for_rule_set(cls, rule_set: RedactionRuleSet) -> PayloadRedactor:
        return cls(RedactionPolicy.for_rule_set(rule_set))

    def redact(self, payload: dict[str, Any]) -> dict[str, Any]:
        copy: dict[str, Any] = {}
        for key, value in payload.items():
            if key in self._policy.sensitive_keys:
                copy[key] = self._policy.replacement
            elif isinstance(value, dict):
                copy[key] = self.redact(value)
            elif isinstance(value, list):
                copy[key] = [
                    self.redact(item) if isinstance(item, dict)
                    else self._redact_string(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            elif isinstance(value, str):
                copy[key] = self._redact_string(value)
            else:
                copy[key] = value
        return copy

    def _redact_string(self, text: str) -> str:
        result = text
        for pattern in self._policy.value_patterns:
            result = pattern.sub(self._policy.replacement, result)
        return result


def redact_for_audit(arguments: dict[str, Any]) -> dict[str, Any]:
    current = arguments
    for rule_set in RedactionRuleSet:
        current = PayloadRedactor.for_rule_set(rule_set).redact(current)
    return current
