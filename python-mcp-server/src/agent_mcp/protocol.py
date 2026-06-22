"""Minimal JSON-RPC 2.0 helpers following the MCP method names and shapes.

We implement the wire protocol directly (rather than depend on a fast-moving SDK) so the server is
dependency-free and fully testable. The method names and result shapes match the MCP spec:
`initialize`, `tools/list`, `tools/call`.
"""
from __future__ import annotations

from typing import Any

PROTOCOL_VERSION = "2024-11-05"

METHOD_INITIALIZE = "initialize"
METHOD_TOOLS_LIST = "tools/list"
METHOD_TOOLS_CALL = "tools/call"

# JSON-RPC error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


def success(request_id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error(request_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
