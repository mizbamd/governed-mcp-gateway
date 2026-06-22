"""The governed MCP server. Transport-agnostic: handle() takes/returns JSON-RPC dicts."""
from __future__ import annotations

import json
import sys
import uuid
from typing import Any

from . import protocol
from .audit import AuditLog
from .governance import Decision, PolicyEngine, Sensitivity
from .tools import ToolRegistry, default_registry


class McpServer:
    def __init__(
        self,
        registry: ToolRegistry | None = None,
        policy: PolicyEngine | None = None,
        audit: AuditLog | None = None,
    ) -> None:
        self.registry = registry or default_registry()
        self.policy = policy or PolicyEngine()
        self.audit = audit or AuditLog()
        self._pending_approvals: dict[str, dict] = {}

    def handle(self, message: dict) -> dict:
        method = message.get("method")
        request_id = message.get("id")
        params = message.get("params") or {}

        if method == protocol.METHOD_INITIALIZE:
            return protocol.success(request_id, {
                "protocolVersion": protocol.PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "agent-mcp-python", "version": "1.0.0"},
            })

        if method == protocol.METHOD_TOOLS_LIST:
            return protocol.success(request_id, {
                "tools": [tool.to_mcp() for tool in self.registry.list()]
            })

        if method == protocol.METHOD_TOOLS_CALL:
            return self._handle_tools_call(request_id, params)

        return protocol.error(request_id, protocol.METHOD_NOT_FOUND, f"unknown method: {method}")

    def _handle_tools_call(self, request_id: Any, params: dict) -> dict:
        name = params.get("name")
        arguments = params.get("arguments") or {}
        role = params.get("role", "agent")
        approval_token = params.get("approvalToken")

        tool = self.registry.get(name)
        if tool is None:
            return protocol.error(request_id, protocol.INVALID_PARAMS, f"unknown tool: {name}")

        # If this is the redemption of a previously granted approval, execute it.
        if approval_token and approval_token in self._pending_approvals:
            pending = self._pending_approvals.pop(approval_token)
            result = tool.handler(pending["arguments"])
            self.audit.record(role, name, pending["arguments"], "approved", "executed")
            return protocol.success(request_id, self._tool_result(result))

        decision = self.policy.evaluate(role, tool.sensitivity)

        if decision.decision is Decision.DENY:
            self.audit.record(role, name, arguments, "deny", "blocked")
            return protocol.error(request_id, protocol.INVALID_REQUEST, f"denied: {decision.reason}")

        if decision.decision is Decision.REQUIRE_APPROVAL:
            token = str(uuid.uuid4())
            self._pending_approvals[token] = {"arguments": arguments}
            self.audit.record(role, name, arguments, "require_approval", "pending")
            return protocol.success(request_id, {
                "content": [{"type": "text", "text": "approval_required"}],
                "approvalRequired": True,
                "approvalToken": token,
                "reason": decision.reason,
                "isError": False,
            })

        result = tool.handler(arguments)
        self.audit.record(role, name, arguments, "allow", "executed")
        return protocol.success(request_id, self._tool_result(result))

    @staticmethod
    def _tool_result(result: dict) -> dict:
        return {"content": [{"type": "text", "text": json.dumps(result)}], "isError": False}

    def serve_stdio(self) -> None:  # pragma: no cover
        """Line-delimited JSON-RPC over stdin/stdout (the common MCP transport)."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                sys.stdout.write(json.dumps(
                    protocol.error(None, protocol.PARSE_ERROR, "invalid JSON")) + "\n")
                sys.stdout.flush()
                continue
            response = self.handle(message)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":  # pragma: no cover
    McpServer().serve_stdio()
