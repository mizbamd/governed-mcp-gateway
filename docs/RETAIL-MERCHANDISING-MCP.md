# Retail merchandising MCP tools

The governed MCP gateway exposes a **thin vertical slice** for a merchandising/pricing copilot:
lookup supplier facts, club location context, and effective-dated item cost — the same three
questions a buyer asks before approving a deal.

## Integration contracts

| Tool | Sensitivity | Backend | Portfolio repo |
|---|---|---|---|
| `lookup_supplier` | READ | Supplier golden record API | `supplier-golden-record-platform` |
| `lookup_location` | READ | Location read-through cache | `location-reference-cache` |
| `lookup_item_cost` | READ | CQRS cost projection + Redis cache | `item-cost-ledger-platform` |

All three are **READ** tools — they flow through the existing policy engine without human approval.
Every call is hash-chained in the audit log like any other tool.

## Offline vs production

- **Offline (default):** `RetailCatalog` / `retail_catalog.py` return deterministic mock JSON shaped like the REST APIs.
- **Production:** replace handlers with HTTP clients pointed at the three services (env: `SUPPLIER_BASE_URL`, `LOCATION_BASE_URL`, `COST_BASE_URL`).

## Demo

```bash
cd python-mcp-server
pip install pytest
pytest -q
PYTHONPATH=src python -m agent_mcp.merchandising_demo
```

## Why not a fourth AI repo?

`agentic-rag-engine` already proves RAG depth; this slice proves **composition** — governed agents
acting on the retail keystone without duplicating retrieval infrastructure.
