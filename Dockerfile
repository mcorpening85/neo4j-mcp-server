FROM python:3.11-slim

WORKDIR /app

# Install curl for health checks (optional, for manual testing)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install the MCP server and required dependencies
RUN pip install --no-cache-dir mcp-neo4j-cypher requests

# Copy the wrapper script
COPY start.py /app/start.py
RUN chmod +x /app/start.py

# Expose port
EXPOSE 8080

# Longer start period for slower connections, more lenient health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the wrapper script which handles both health checks and MCP server
CMD ["python3", "-u", "/app/start.py"]
