"""Tamper-evident-ish audit log of every tool invocation and policy decision."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field


@dataclass
class AuditEntry:
    timestamp: float
    role: str
    tool: str
    arguments_hash: str
    decision: str
    outcome: str
    prev_hash: str
    entry_hash: str = ""


class AuditLog:
    """Append-only log where each entry chains the previous entry's hash (a mini hash chain), so
    any tampering with a historical record invalidates every subsequent entry."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def record(self, role: str, tool: str, arguments: dict, decision: str, outcome: str) -> AuditEntry:
        prev_hash = self._entries[-1].entry_hash if self._entries else "genesis"
        args_hash = hashlib.sha256(
            json.dumps(arguments, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        entry = AuditEntry(
            timestamp=time.time(),
            role=role,
            tool=tool,
            arguments_hash=args_hash,
            decision=decision,
            outcome=outcome,
            prev_hash=prev_hash,
        )
        entry.entry_hash = self._hash(entry)
        self._entries.append(entry)
        return entry

    @staticmethod
    def _hash(entry: AuditEntry) -> str:
        payload = {k: v for k, v in asdict(entry).items() if k != "entry_hash"}
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def verify(self) -> bool:
        prev = "genesis"
        for entry in self._entries:
            if entry.prev_hash != prev or entry.entry_hash != self._hash(entry):
                return False
            prev = entry.entry_hash
        return True

    @property
    def entries(self) -> list[AuditEntry]:
        return list(self._entries)
