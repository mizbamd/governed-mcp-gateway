from agent_mcp.audit import AuditLog
from agent_mcp.client import GovernedAgentClient
from agent_mcp.governance import Decision, PolicyEngine, Sensitivity
from agent_mcp.server import McpServer


def rpc(server, method, params=None, rid=1):
    return server.handle({"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}})


def test_initialize_and_tools_list():
    server = McpServer()
    assert rpc(server, "initialize")["result"]["protocolVersion"]
    tools = rpc(server, "tools/list")["result"]["tools"]
    names = {tool["name"] for tool in tools}
    assert {"get_account_balance", "post_payment", "search_docs", "propose_price_change",
            "lookup_supplier", "lookup_location", "lookup_item_cost"} <= names


def test_read_tool_executes_without_approval():
    server = McpServer()
    response = rpc(server, "tools/call",
                   {"name": "get_account_balance", "arguments": {"account_id": "merchant-1"}})
    assert response["result"]["isError"] is False
    assert "balance" in response["result"]["content"][0]["text"]


def test_write_tool_requires_approval_then_executes():
    server = McpServer()
    first = rpc(server, "tools/call", {
        "name": "post_payment",
        "arguments": {"debit_account": "funding-1", "credit_account": "merchant-1", "amount": 10},
    })["result"]
    assert first["approvalRequired"] is True
    token = first["approvalToken"]

    second = rpc(server, "tools/call", {
        "name": "post_payment",
        "arguments": {"debit_account": "funding-1", "credit_account": "merchant-1", "amount": 10},
        "approvalToken": token,
    })["result"]
    assert "posted" in second["content"][0]["text"]


def test_trusted_role_skips_approval():
    server = McpServer()
    response = rpc(server, "tools/call", {
        "name": "post_payment", "role": "system-operator",
        "arguments": {"debit_account": "funding-1", "credit_account": "merchant-1", "amount": 5},
    })["result"]
    assert "posted" in response["content"][0]["text"]


def test_unknown_role_is_denied():
    server = McpServer()
    response = rpc(server, "tools/call", {
        "name": "get_account_balance", "role": "intruder",
        "arguments": {"account_id": "merchant-1"},
    })
    assert "error" in response


def test_policy_engine_matrix():
    policy = PolicyEngine()
    assert policy.evaluate("analyst", Sensitivity.READ).decision is Decision.ALLOW
    assert policy.evaluate("agent", Sensitivity.WRITE).decision is Decision.REQUIRE_APPROVAL
    assert policy.evaluate("system-operator", Sensitivity.WRITE).decision is Decision.ALLOW
    assert policy.evaluate("ghost", Sensitivity.READ).decision is Decision.DENY


def test_audit_log_is_hash_chained_and_verifiable():
    audit = AuditLog()
    server = McpServer(audit=audit)
    rpc(server, "tools/call", {"name": "get_account_balance", "arguments": {"account_id": "merchant-1"}})
    rpc(server, "tools/call", {"name": "search_docs", "arguments": {"query": "settlement"}})
    assert len(audit.entries) == 2
    assert audit.verify() is True

    # Tampering breaks the chain.
    audit.entries  # snapshot
    audit._entries[0].outcome = "tampered"
    assert audit.verify() is False


def test_governed_client_human_in_the_loop():
    server = McpServer()
    approvals: list[tuple[str, dict]] = []

    def approver(tool_name, arguments):
        approvals.append((tool_name, arguments))
        return True

    client = GovernedAgentClient(server, approver)
    tools = client.list_tools()
    assert tools

    read_result = client.call_tool("get_account_balance", {"account_id": "merchant-1"})
    assert read_result["status"] == "executed"

    write_result = client.call_tool(
        "post_payment", {"debit_account": "funding-1", "credit_account": "merchant-1", "amount": 1})
    assert write_result["status"] == "executed_after_approval"
    assert approvals  # the human was consulted


def test_governed_client_rejection_blocks_write():
    server = McpServer()
    client = GovernedAgentClient(server, approver=lambda name, args: False)
    result = client.call_tool(
        "propose_price_change", {"sku": "SKU-1", "new_price": 9.99})
    assert result["status"] == "approval_rejected"
