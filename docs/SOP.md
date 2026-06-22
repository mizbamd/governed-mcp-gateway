# Standard Operating Procedure (SOP): agent-mcp

Operational runbook for the governed MCP servers and agent client. Audience: platform / security ops.

## 1. Components
| Component | Detail |
|---|---|
| python-mcp-server | MCP over stdio/HTTP; policy + audit; mock tool backends |
| java-mcp-server | Spring Boot MCP over HTTP (port 8086); policy + audit |
| agent client | Governed client enforcing HITL on sensitive tools |

## 2. Bring-up
1. Java: `mvn spring-boot:run` (java-mcp-server) -> health on `/actuator/health`.
2. Python: install deps, run the server module (stdio or HTTP).
3. Full stack: `docker compose up --build` to run both servers.
4. Smoke test: list tools, call a read tool (auto-allow), call a sensitive write (must require approval).

## 3. Policy administration
- Each tool's sensitivity is declared in the tool registry. Changing a classification is a controlled
  change (record as an ADR).
- Default posture is deny; only explicitly classified tools are callable.

## 4. Approval workflow (HITL)
1. Agent requests a sensitive-write tool.
2. Policy engine returns `PENDING_APPROVAL`; the request is queued, not executed.
3. An authorized human approves/denies (maker-checker).
4. On approval, the action executes and the outcome is audited; on denial, it is recorded and dropped.

## 5. Audit operations
- Audit entries are hash-chained: each entry includes the prior entry's hash.
- **Verify integrity**: run the chain-verification routine/endpoint; any break indicates tampering.
- Export the audit log for compliance review on request; retain per policy.

## 6. Incident response
| Symptom | First action | Remediation |
|---|---|---|
| Sensitive write executed without approval | Verify audit chain | Treat as SEV; freeze tool; investigate policy config |
| Audit chain verification fails | Isolate the log | Engage security; preserve evidence |
| Tool backend errors | Check adapter health | Fail closed (deny) rather than bypass governance |

## 7. Change management
Adding a tool or changing its sensitivity requires: registry update, ADR, and a test proving the
governance decision (allow / pending / deny) is correct.
