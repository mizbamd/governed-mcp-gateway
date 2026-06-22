# ADR-0003: Hash-chained, tamper-evident audit log

- Status: Accepted
- Date: 2026-06-22

## Context
Agent actions against regulated systems must be auditable and non-repudiable. A plain log can be
edited after the fact, undermining its evidentiary value.

## Decision
Append every tool call (allow / deny / approval) to an in-memory log where each entry includes the
hash of the previous entry (a hash chain). `verify()` walks the chain and fails if any historical
entry was altered. Arguments are stored as a hash, not in cleartext, to avoid leaking sensitive data.

## Consequences
- Positive: tamper-evident, privacy-preserving audit trail; trivial integrity check.
- Negative: in-memory only in this reference -- production must persist to an append-only/WORM sink
  (e.g. stream to the lakehouse) for durability and centralized retention.
