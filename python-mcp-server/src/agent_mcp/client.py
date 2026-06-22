"""A governed agent client demonstrating the human-in-the-loop approval loop over MCP."""
from __future__ import annotations

import itertools
from collections.abc import Callable

from .server import McpServer

# Approver receives (tool_name, arguments) and returns True to approve a write action.
Approver = Callable[[str, dict], bool]


def always_deny(tool_name: str, arguments: dict) -> bool:
    return False


class GovernedAgentClient:
    def __init__(self, server: McpServer, approver: Approver) -> None:
        self.server = server
        self.approver = approver
        self._ids = itertools.count(1)

    def _rpc(self, method: str, params: dict | None = None) -> dict:
        return self.server.handle({
            "jsonrpc": "2.0", "id": next(self._ids), "method": method, "params": params or {}
        })

    def list_tools(self) -> list[dict]:
        return self._rpc("tools/list")["result"]["tools"]

    def call_tool(self, name: str, arguments: dict, role: str = "agent") -> dict:
        response = self._rpc("tools/call", {"name": name, "arguments": arguments, "role": role})

        if "error" in response:
            return {"status": "denied", "error": response["error"]["message"]}

        result = response["result"]
        if result.get("approvalRequired"):
            # Pause and ask a human (the defining property of human-in-the-loop).
            if not self.approver(name, arguments):
                return {"status": "approval_rejected"}
            approved = self._rpc("tools/call", {
                "name": name, "arguments": arguments, "role": role,
                "approvalToken": result["approvalToken"],
            })
            return {"status": "executed_after_approval", "result": approved["result"]}

        return {"status": "executed", "result": result}
