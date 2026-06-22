"""Tool definitions exposed over MCP. Each tool maps to an enterprise capability.

Backends are mocked in-memory here; in a real deployment these call the ledger-service,
pricing-orchestration, and agentic-rag-engine services from the wider reference architecture.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .governance import Sensitivity


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_schema: dict
    sensitivity: Sensitivity
    handler: Callable[[dict], dict]

    def to_mcp(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "annotations": {"sensitivity": self.sensitivity.value},
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list(self) -> list[Tool]:
        return list(self._tools.values())


# --- Mock backends standing in for the real services ---
_BALANCES = {"merchant-1": 1250.00, "funding-1": -1250.00}


def _get_account_balance(args: dict) -> dict:
    account = args["account_id"]
    return {"account_id": account, "balance": _BALANCES.get(account, 0.0)}


def _post_payment(args: dict) -> dict:
    debit, credit, amount = args["debit_account"], args["credit_account"], float(args["amount"])
    _BALANCES[debit] = _BALANCES.get(debit, 0.0) - amount
    _BALANCES[credit] = _BALANCES.get(credit, 0.0) + amount
    return {"status": "posted", "debit_account": debit, "credit_account": credit, "amount": amount}


def _search_docs(args: dict) -> dict:
    return {"query": args["query"], "results": ["payments-settlement.md", "rag-architecture.md"]}


def _propose_price_change(args: dict) -> dict:
    return {"status": "proposed", "sku": args["sku"], "new_price": float(args["new_price"])}


def default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(Tool(
        name="get_account_balance",
        description="Read the current balance of a ledger account.",
        input_schema={"type": "object", "properties": {"account_id": {"type": "string"}},
                      "required": ["account_id"]},
        sensitivity=Sensitivity.READ,
        handler=_get_account_balance,
    ))
    registry.register(Tool(
        name="search_docs",
        description="Hybrid search over the enterprise knowledge base.",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}},
                      "required": ["query"]},
        sensitivity=Sensitivity.READ,
        handler=_search_docs,
    ))
    registry.register(Tool(
        name="post_payment",
        description="Move funds between two ledger accounts. WRITE: requires approval.",
        input_schema={"type": "object", "properties": {
            "debit_account": {"type": "string"},
            "credit_account": {"type": "string"},
            "amount": {"type": "number"}},
            "required": ["debit_account", "credit_account", "amount"]},
        sensitivity=Sensitivity.WRITE,
        handler=_post_payment,
    ))
    registry.register(Tool(
        name="propose_price_change",
        description="Propose a price change for a SKU. WRITE: requires approval.",
        input_schema={"type": "object", "properties": {
            "sku": {"type": "string"}, "new_price": {"type": "number"}},
            "required": ["sku", "new_price"]},
        sensitivity=Sensitivity.WRITE,
        handler=_propose_price_change,
    ))
    return registry
