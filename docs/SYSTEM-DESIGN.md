# System Design: governed-mcp-gateway

## 1. Problem
Let LLM agents take actions against real enterprise systems (move money, change prices, query
records) without creating an uncontrolled blast radius. Agents are non-deterministic; the controls
around them must not be.

## 2. SLOs / control objectives
| Concern | Target |
|---|---|
| Unauthorized write execution | 0 (writes require approval or trusted role) |
| Auditability | 100% of tool calls logged, tamper-evident |
| Tool-call latency overhead (governance) | < 5 ms p99 |
| Availability | 99.9% |

## 3. Design
- **MCP** as the integration contract (`initialize`, `tools/list`, `tools/call`). Standard, so any
  MCP-capable agent runtime (Claude, Cursor, custom) can use these servers unchanged.
- **Sensitivity tagging**: every tool is READ or WRITE.
- **PolicyEngine**: READ allowed for known roles; WRITE requires human approval unless the caller
  holds a trusted role; unknown roles denied. Fail-closed by default.
- **Human-in-the-loop**: a WRITE returns `approvalRequired` + a one-time `approvalToken`. Execution
  only happens when the call is replayed with a valid token (a human/second-system approved it).
- **Audit log**: append-only, hash-chained (each entry binds the previous entry's hash). `verify()`
  detects tampering. This is the evidence trail regulators and security teams require.

## 4. Threat model and mitigations
| Threat | Mitigation |
|---|---|
| Prompt-injected agent triggers a harmful write | Write requires out-of-band human approval |
| Compromised/unknown caller | Role check, fail-closed deny |
| Repudiation ("the agent did it, not me") | Hash-chained audit ties role + args + decision |
| Replay of an approval | Approval tokens are single-use (removed on redemption) |
| Silent tampering of logs | Hash chain verification |

## 5. Polyglot proof
Identical governance is implemented in Python (stdio transport) and Java/Spring (HTTP transport),
demonstrating the model is independent of language and transport.

## 6. Production hardening (next steps)
mTLS between agent and server; OIDC-derived roles instead of a header; externalized policy (OPA/Rego);
durable audit sink (append to the lakehouse via Kafka); rate limiting; per-tool quotas.
