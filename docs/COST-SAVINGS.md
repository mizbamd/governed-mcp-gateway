# Cost Savings Analysis: agent-mcp

The value of this layer is primarily **risk-cost avoidance** and **integration reuse**, with some
direct automation savings. Figures are representative ranges, not a specific company's numbers.

## 1. Risk-cost avoidance (primary)
| Lever | Mechanism | Typical impact |
|---|---|---|
| Prevent unauthorized agent actions | Default-deny + HITL on sensitive writes | Avoids cost of a single bad automated action (can be very large) |
| Defensible audit trail | Hash-chained log of every decision | Lower audit/eDiscovery cost; faster regulatory response |
| Consistent controls | One policy model across languages/tools | Avoids per-integration security review cost |

## 2. Integration reuse (build cost)
| Lever | Mechanism | Typical impact |
|---|---|---|
| One contract, many tools | MCP servers expose typed tools uniformly | Avoids N bespoke agent-to-system integrations |
| Polyglot parity | Same governance in Java and Python | No duplicate governance implementations |

A common rule of thumb: each bespoke, ungoverned integration costs weeks of build plus a recurring
security-review burden. Standardizing on one governed contract converts that into a single reusable
layer.

## 3. Automation savings (direct)
| Lever | Mechanism | Typical impact |
|---|---|---|
| Safe agent automation of routine actions | Read + low-risk writes auto-execute | Staff time recovered on repetitive tasks |
| Maker-checker fits existing controls | HITL only where required | Automation without new control overhead |

## 4. Worked illustration
For an enterprise integrating agents with 10 systems:

| Approach | Build | Recurring security review | Audit readiness |
|---|---|---|---|
| 10 bespoke integrations | 10x effort | 10x review surface | Inconsistent |
| 1 governed MCP layer | 1x layer + thin adapters | 1x review surface | Built-in (hash-chained) |

## 5. Notes
The dominant return here is avoided incident cost and audit efficiency, which dwarf compute costs.
Calibrate with the organization's own incident-cost and integration-effort baselines.
