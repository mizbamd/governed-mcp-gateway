# Non-Functional Requirements (NFR): agent-mcp

## 1. Security (primary quality attribute)
| ID | Requirement |
|---|---|
| NFR-SEC1 | Default-deny: only classified tools are callable. |
| NFR-SEC2 | Sensitive writes require human approval; no bypass path exists. |
| NFR-SEC3 | All requests, decisions, and outcomes are logged before/after execution. |
| NFR-SEC4 | Least-privilege service identities to backends; no shared god credentials. |

## 2. Auditability / integrity
| ID | Requirement | Target |
|---|---|---|
| NFR-AUD1 | Audit log is tamper-evident (hash-chained). | Any mutation detectable |
| NFR-AUD2 | Chain verification is independent and repeatable. | Verifiable on demand |
| NFR-AUD3 | Every executed action is traceable to agent + (if applicable) approver. | 100% coverage |

## 3. Performance
| ID | Requirement | Target |
|---|---|---|
| NFR-P1 | Policy decision overhead per call | < 5 ms |
| NFR-P2 | Read tool round-trip (excluding backend) | p99 < 50 ms |
| NFR-P3 | Audit append overhead | < 5 ms |

## 4. Availability / reliability
| ID | Requirement | Target |
|---|---|---|
| NFR-A1 | Server availability | 99.9% |
| NFR-A2 | Fail-closed behavior | On policy/audit failure, deny rather than execute |

## 5. Interoperability / portability
| ID | Requirement |
|---|---|
| NFR-I1 | Identical governance semantics across Java and Python servers. |
| NFR-I2 | MCP contract is transport-flexible (stdio / HTTP). |
| NFR-I3 | Tool backends are pluggable adapters. |

## 6. Observability
| ID | Requirement |
|---|---|
| NFR-O1 | Metrics: calls by decision (allow/pending/deny), approval latency, denial rate. |
| NFR-O2 | The audit log doubles as the action-level trace. |

## 7. Maintainability
| ID | Requirement |
|---|---|
| NFR-M1 | New tools added via registry + sensitivity classification, with a governance test. |
