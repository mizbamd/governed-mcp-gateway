# Audit argument redaction

Agent tool calls may include regulated data. Before any argument JSON is hashed into the
tamper-evident audit chain, the gateway applies the same rule sets as
[supplier-negotiation-observability](https://github.com/mizbamd/supplier-negotiation-observability):

| Rule set | Keys / patterns |
|---|---|
| `RETAIL` | `unitCost`, `rebatePct`, `lumpSumAmount`, … |
| `PCI` | `pan`, `cvv`, … + 13–19 digit sequences in strings |
| `HIPAA` | `patientName`, `mrn`, `ssn`, … + `###-##-####` in strings |

## Flow

```
tools/call arguments (raw)
  → redact_for_audit()  [RETAIL → PCI → HIPAA]
  → SHA-256(redacted JSON)
  → hash-chained AuditEntry
```

Raw sensitive values are **never** stored in the audit log — only the redacted hash.

## Verify

```bash
cd python-mcp-server && pytest -q tests/test_audit_redaction.py
cd java-mcp-server && mvn test -Dtest=PayloadRedactorTest,McpServiceTest#auditHashesRedactedArguments
```

## Portfolio link

| Repo | Redaction surface |
|---|---|
| supplier-negotiation-observability | Elasticsearch + structured logs |
| governed-mcp-gateway | MCP agent audit hash chain |

Same `RedactionRuleSet` enum and policy keys in both codebases.
