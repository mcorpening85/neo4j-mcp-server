#!/usr/bin/env python3
"""
Wrapper script to run MCP server with health check endpoint for Render.
"""
import os
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple health check endpoint that responds to all requests."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            # For any other path, return 200 to satisfy Render's health checks
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'MCP Server Running')
    
    def do_HEAD(self):
        """Handle HEAD requests (Render uses these for health checks)."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging to reduce noise."""
        pass


def run_health_server(port=8080):
    """Run a simple HTTP server for health checks."""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health check server running on port {port}")
    server.serve_forever()


def run_mcp_server():
    """Run the MCP server."""
    # Get environment variables
    env = os.environ.copy()
    
    # Log configuration
    logger.info("Starting MCP server with configuration:")
    logger.info(f"  NEO4J_TRANSPORT: {env.get('NEO4J_TRANSPORT', 'not set')}")
    logger.info(f"  NEO4J_MCP_SERVER_HOST: {env.get('NEO4J_MCP_SERVER_HOST', 'not set')}")
    logger.info(f"  NEO4J_MCP_SERVER_PORT: {env.get('NEO4J_MCP_SERVER_PORT', 'not set')}")
    logger.info(f"  NEO4J_URI: {env.get('NEO4J_URI', 'not set')}")
    
    # Run the MCP server
    subprocess.run(['mcp-neo4j-cypher'], env=env)


if __name__ == '__main__':
    # Start health check server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    logger.info("Wrapper started successfully")
    
    # Run MCP server in main thread (blocking)
    run_mcp_server()
