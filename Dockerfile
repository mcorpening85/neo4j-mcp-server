FROM python:3.11-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install the MCP server
RUN pip install --no-cache-dir mcp-neo4j-cypher

# Expose port
EXPOSE 8080

# Set environment variables for HTTP transport
ENV NEO4J_TRANSPORT=http
ENV NEO4J_MCP_SERVER_HOST=0.0.0.0
ENV NEO4J_MCP_SERVER_PORT=8080
ENV NEO4J_MCP_SERVER_PATH=/api/mcp/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the server - it will use the environment variables above
CMD ["mcp-neo4j-cypher"]