# Industry Applicability

Governed agentic access to systems of record is a universal enterprise need as AI agents move from
chat to action. The governance model is the product; the tools are domain-specific.

| Capability | Banking (Capital One, Citi) | Healthcare (UnitedHealth, McKesson) | Asset mgmt / PE (BlackRock, Blackstone) | Retail / Restaurant (CVS, Uline, McDonald's) |
|---|---|---|---|---|
| READ tools | Balance/transaction lookup | Eligibility / claim status | Position / NAV lookup | Inventory / price lookup |
| WRITE tools (HITL) | Initiate payment / adjustment | Submit claim adjustment | Place / amend order | Approve price / restock |
| Approval gating | Maker-checker on funds movement | Clinician/adjuster sign-off | Trader/PM sign-off | Manager approval on price |
| Audit chain | SOX / reg evidence | HIPAA action trail | SEC action trail | Change-control evidence |
| MCP standard | Reuse across agent vendors | Reuse across agent vendors | Reuse across agent vendors | Reuse across agent vendors |

## Why this is the hard, valuable part
Building an agent that *can* call an API is easy. Building the governance, approval, and audit
scaffolding that makes it *safe* to let an agent touch a system of record is the part enterprises
cannot skip -- and the part most demos ignore.
