"""Merchandising copilot demo — composes retail MCP tools without a live LLM."""
from __future__ import annotations

from agent_mcp.client import GovernedAgentClient
from agent_mcp.server import McpServer


def run_demo() -> None:
    server = McpServer()
    client = GovernedAgentClient(server, approver=lambda tool, args: True)

    club = 4701
    item = 10001

    location = client.call_tool("lookup_location", {"location_nbr": club})
    cost = client.call_tool("lookup_item_cost", {"club_nbr": club, "item_nbr": item})

    supplier_id = "88421"
    if cost["status"] == "executed" and "supplier_legacy_id" in cost["result"]:
        supplier_id = cost["result"]["supplier_legacy_id"]
    supplier = client.call_tool("lookup_supplier", {"legacy_supplier_id": supplier_id})

    print("=== Merchandising copilot (governed MCP) ===")
    print(f"Club:      {location['result']}")
    print(f"Item cost: {cost['result']}")
    print(f"Supplier:  {supplier['result']}")


if __name__ == "__main__":
    run_demo()
