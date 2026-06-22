FROM python:3.12-slim
WORKDIR /app
COPY src ./src
ENV PYTHONPATH=/app/src
# MCP servers speak JSON-RPC over stdio; run interactively or wire to an agent runner.
ENTRYPOINT ["python", "-m", "agent_mcp.server"]
