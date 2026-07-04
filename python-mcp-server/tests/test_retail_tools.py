from agent_mcp.server import McpServer

from test_server_and_client import rpc


def test_retail_merchandising_tools():
    server = McpServer()
    supplier = rpc(server, "tools/call", {
        "name": "lookup_supplier", "arguments": {"legacy_supplier_id": "88421"},
    })["result"]
    assert supplier["isError"] is False
    assert "Pacific Fresh" in supplier["content"][0]["text"]

    location = rpc(server, "tools/call", {
        "name": "lookup_location", "arguments": {"location_nbr": 4701},
    })["result"]
    assert location["isError"] is False

    cost = rpc(server, "tools/call", {
        "name": "lookup_item_cost", "arguments": {"club_nbr": 4701, "item_nbr": 10001},
    })["result"]
    assert cost["isError"] is False
    assert "4.27" in cost["content"][0]["text"]
