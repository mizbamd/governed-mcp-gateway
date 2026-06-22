"""A governed Model Context Protocol (MCP) server.

Exposes enterprise tools (ledger, pricing, search) to an LLM agent over MCP's JSON-RPC interface,
wrapped in a governance layer: every tool call passes a policy check (read vs write sensitivity),
write actions require human-in-the-loop approval, and every decision is written to an audit log.
This is the pattern that makes agentic automation safe to run against real systems of record.
"""

__version__ = "1.0.0"
