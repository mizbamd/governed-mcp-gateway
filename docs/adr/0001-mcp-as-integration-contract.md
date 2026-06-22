# ADR-0001: MCP as the agent-to-systems integration contract

- Status: Accepted
- Date: 2026-06-22

## Context
Agents need a standard way to discover and invoke tools across many backends and many agent runtimes.
Bespoke per-agent integrations do not scale and lock us to one vendor.

## Decision
Adopt the Model Context Protocol (JSON-RPC: `initialize`, `tools/list`, `tools/call`). Any
MCP-capable runtime can use our servers unchanged. We implement the wire protocol directly rather
than depend on a fast-moving SDK, keeping the servers small and testable.

## Consequences
- Positive: vendor-neutral, future-proof, simple to test.
- Negative: we track spec evolution manually; advanced MCP features (resources, prompts, streaming)
  are out of scope for this reference.
