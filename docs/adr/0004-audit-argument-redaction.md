# ADR 0004: Redact tool-call arguments before audit hash chain

## Status
Accepted

## Context
The hash-chained audit log (ADR 0003) records a SHA-256 of tool arguments on every `tools/call`.
Agents may pass PCI (PAN, CVV) or HIPAA (PHI, SSN) fields — or retail commercial terms — in
tool arguments. Hashing raw values still risks offline dictionary attacks and violates the
defense-in-depth posture established in `supplier-negotiation-observability` (ADR 0004 there).

## Decision
Before computing `arguments_hash`, apply all `RedactionRuleSet` values in order:

1. `RETAIL` — negotiation/commercial keys
2. `PCI` — card data keys + PAN regex in strings
3. `HIPAA` — PHI keys + SSN regex in strings

Implementation is identical in Java (`AuditArgumentRedactor`) and Python (`redact_for_audit`).
The audit chain stores only the hash of the **redacted** JSON — never raw sensitive fields.

## Consequences
- **Positive:** Portfolio-wide HIPAA/PCI story: negotiation logs, MCP agent audit, same rule vocabulary.
- **Positive:** Two different PAN values hash identically after redaction (tested).
- **Negative:** Audit hash cannot prove the original argument value — by design.
