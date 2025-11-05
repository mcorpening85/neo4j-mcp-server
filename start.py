#!/usr/bin/env python3
"""
Wrapper script that runs MCP server with a reverse proxy for health checks.
This handles both HTTP health checks and MCP protocol requests.
"""
import os
import subprocess
import threading
import logging
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP server runs on 8081, health proxy on 8080
MCP_PORT = 8081
PROXY_PORT = 8080
MCP_BASE_URL = f"http://127.0.0.1:{MCP_PORT}"


class ProxyHandler(BaseHTTPRequestHandler):
    """
    Reverse proxy that:
    - Handles health checks at /health and / (GET/HEAD)
    - Forwards /api/mcp/* requests to MCP server at /*
    """
    
    def _send_health_response(self):
        """Send a healthy response."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def _proxy_to_mcp(self):
        """Forward request to MCP server."""
        try:
            # Strip /api/mcp prefix if present, forward to root of MCP server
            path = self.path
            if path.startswith('/api/mcp'):
                path = path[8:]  # Remove '/api/mcp'
                if not path or path[0] != '/':
                    path = '/' + path
            
            # Build target URL
            target_url = f"{MCP_BASE_URL}{path}"
            
            # Get request headers and fix the Host header for internal routing
            headers = {}
            for key, val in self.headers.items():
                # Don't forward hop-by-hop headers
                if key.lower() not in ['host', 'connection', 'keep-alive', 'proxy-authenticate', 
                                       'proxy-authorization', 'te', 'trailer', 'transfer-encoding', 'upgrade']:
                    headers[key] = val
            
            # Set the Host header to localhost for internal MCP server
            headers['Host'] = f'127.0.0.1:{MCP_PORT}'
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            logger.info(f"Proxying {self.command} {self.path} -> {path} to MCP server")
            
            # Forward the request
            if self.command == 'GET':
                response = requests.get(target_url, headers=headers, timeout=30)
            elif self.command == 'POST':
                response = requests.post(target_url, headers=headers, data=body, timeout=30)
            elif self.command == 'HEAD':
                response = requests.head(target_url, headers=headers, timeout=30)
            else:
                self.send_error(405, "Method Not Allowed")
                return
            
            # Send response back to client
            self.send_response(response.status_code)
            for key, val in response.headers.items():
                if key.lower() not in ['transfer-encoding', 'connection']:
                    self.send_header(key, val)
            self.end_headers()
            self.wfile.write(response.content)
            
            logger.info(f"Response: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Proxy error: {e}")
            self.send_error(503, f"MCP server unavailable: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path in ['/health', '/']:
            self._send_health_response()
        else:
            self._proxy_to_mcp()
    
    def do_POST(self):
        """Handle POST requests - forward to MCP."""
        self._proxy_to_mcp()
    
    def do_HEAD(self):
        """Handle HEAD requests."""
        if self.path in ['/health', '/']:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
        else:
            self._proxy_to_mcp()
    
    def log_message(self, format, *args):
        """Log all requests for debugging."""
        logger.info(f"{self.command} {self.path} - {format % args}")


def run_proxy_server(port=PROXY_PORT):
    """Run the reverse proxy server."""
    server = HTTPServer(('0.0.0.0', port), ProxyHandler)
    logger.info(f"Proxy server running on port {port}, forwarding to MCP on {MCP_PORT}")
    logger.info(f"Path rewriting: /api/mcp/* -> /* on internal MCP server")
    server.serve_forever()


def run_mcp_server():
    """Run the MCP server on internal port."""
    # Wait a moment for proxy to start
    time.sleep(2)
    
    # Set environment variables for MCP server
    env = os.environ.copy()
    env['NEO4J_MCP_SERVER_PORT'] = str(MCP_PORT)
    env['NEO4J_MCP_SERVER_HOST'] = '127.0.0.1'  # Only bind to localhost
    # Override ALLOWED_HOSTS to accept localhost
    env['NEO4J_MCP_SERVER_ALLOWED_HOSTS'] = '127.0.0.1,localhost,*'
    # Remove the path requirement - MCP server will run at root
    if 'NEO4J_MCP_SERVER_PATH' in env:
        del env['NEO4J_MCP_SERVER_PATH']
    
    # Log configuration
    logger.info("=" * 60)
    logger.info("Starting MCP server with configuration:")
    logger.info(f"  NEO4J_TRANSPORT: {env.get('NEO4J_TRANSPORT', 'not set')}")
    logger.info(f"  NEO4J_MCP_SERVER_HOST: {env.get('NEO4J_MCP_SERVER_HOST')}")
    logger.info(f"  NEO4J_MCP_SERVER_PORT: {env.get('NEO4J_MCP_SERVER_PORT')}")
    logger.info(f"  NEO4J_MCP_SERVER_ALLOWED_HOSTS: {env.get('NEO4J_MCP_SERVER_ALLOWED_HOSTS')}")
    logger.info(f"  NEO4J_URI: {env.get('NEO4J_URI', 'not set')}")
    logger.info("=" * 60)
    
    # Run the MCP server
    subprocess.run(['mcp-neo4j-cypher'], env=env)


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Neo4j MCP Server with Health Check Proxy")
    logger.info("=" * 60)
    
    # Start proxy server in background thread
    proxy_thread = threading.Thread(target=run_proxy_server, daemon=True)
    proxy_thread.start()
    
    logger.info("Wrapper started successfully")
    logger.info(f"Health checks available at: http://localhost:{PROXY_PORT}/health")
    logger.info(f"MCP endpoint (external): http://localhost:{PROXY_PORT}/api/mcp/")
    logger.info(f"MCP endpoint (internal): http://localhost:{MCP_PORT}/")
    
    # Run MCP server in main thread (blocking)
    run_mcp_server()
