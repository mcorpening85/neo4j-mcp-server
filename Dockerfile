FROM python:3.11-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install the MCP server - specific version for stability
RUN pip install --no-cache-dir mcp-neo4j-cypher

# Expose port
EXPOSE 8080

# Health check (disabled for now as endpoint might vary)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
#     CMD curl -f http://localhost:8080/health || exit 1

# Run the server with verbose output for debugging
CMD sh -c 'echo "Starting with NEO4J_TRANSPORT=$NEO4J_TRANSPORT NEO4J_MCP_SERVER_HOST=$NEO4J_MCP_SERVER_HOST NEO4J_MCP_SERVER_PORT=$NEO4J_MCP_SERVER_PORT" && mcp-neo4j-cypher'
