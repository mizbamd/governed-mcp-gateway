# Business Requirements Document (BRD): governed-mcp-gateway

| Field | Value |
|---|---|
| Document | Business Requirements Document |
| Product | governed-mcp-gateway (governed MCP tool servers + agent client) |
| Version | 1.0 |
| Status | Baselined |
| Owner | Platform Engineering / AI Governance |

## 1. Purpose
Define business requirements for exposing enterprise systems to AI agents through a governed Model
Context Protocol (MCP) layer, so agents can act with controls, human approval, and a tamper-evident
audit trail.

## 2. Background and problem statement
Agents are increasingly asked to take actions in real systems (read data, trigger workflows). Direct,
ungoverned access is unacceptable in a regulated enterprise: there is no consistent policy, no
approval for sensitive writes, and no defensible record of what an agent did. The business needs a
standard, auditable integration contract between agents and systems.

## 3. Business objectives
| ID | Objective | Measure of success |
|---|---|---|
| OBJ-1 | Standardize agent-to-system integration | One contract (MCP) across tools and languages |
| OBJ-2 | Enforce policy on every action | 100% of tool calls evaluated by the policy engine |
| OBJ-3 | Require human approval for sensitive writes | No high-sensitivity write executes without sign-off |
| OBJ-4 | Provide a defensible audit record | Tamper-evident (hash-chained) log of every decision |

## 4. Scope
### In scope
- MCP servers in Java and Python exposing typed tools.
- Policy engine classifying tools by sensitivity (read / low-risk write / sensitive write).
- Human-in-the-loop (HITL) approval for sensitive actions.
- Hash-chained audit log of requests, decisions, and outcomes.

### Out of scope
- The agent's reasoning/LLM itself (this governs its actions, not its thoughts).
- Identity provider (delegated to enterprise IAM).
- Business backends (mocked here; real adapters plug in).

## 5. Stakeholders
| Stakeholder | Interest |
|---|---|
| Security / Risk | Controls, least privilege, auditability |
| Compliance / Audit | Tamper-evident record of agent actions |
| Platform engineering | Reusable, polyglot integration contract |
| Business operations | Maker-checker approval fits existing controls |

## 6. Business requirements
| ID | Requirement | Priority |
|---|---|---|
| BR-1 | Every tool shall declare a sensitivity classification. | Must |
| BR-2 | Read/low-risk actions may auto-execute; sensitive writes shall require human approval. | Must |
| BR-3 | Every request, decision, and outcome shall be written to a tamper-evident audit log. | Must |
| BR-4 | The same governance model shall apply across Java and Python servers. | Must |
| BR-5 | Denied or pending actions shall never reach the backend. | Must |
| BR-6 | Audit entries shall be independently verifiable (chain integrity check). | Should |

## 7. Assumptions and constraints
- Agent identity and user identity are provided by the calling context (enterprise IAM).
- Approvals are issued by authorized humans through an existing maker-checker channel.

## 8. Risks
| Risk | Mitigation |
|---|---|
| Over-permissioned tools | Default-deny; explicit sensitivity per tool |
| Audit tampering | Hash-chained entries; periodic chain verification |
| Approval fatigue | Only sensitive writes gated; reads flow freely |
