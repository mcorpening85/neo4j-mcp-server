# Neo4j MCP Server

A Model Context Protocol (MCP) server for Neo4j database integration with Claude AI, optimized for Render deployment.

## 🚀 Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Overview

This MCP server enables Claude to interact with Neo4j graph databases using natural language. It provides:

- **Schema exploration** - Understand your graph structure
- **Cypher query execution** - Run read and write queries
- **Natural language interface** - Ask questions about your data
- **HTTP transport** - Remote access via Render deployment
- **Built-in health checks** - Render-compatible health endpoint

## Deployment Instructions

### 1. Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect this GitHub repository
4. Render will auto-detect the `render.yaml` configuration
5. Add these **required environment variables** in Render dashboard:
   ```
   NEO4J_URI=bolt://your-neo4j-host:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-secure-password
   ```
6. Click **Create Web Service**
7. Wait for deployment (first deploy may take 2-3 minutes)

**Important:** The three required environment variables (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`) must be added in your Render dashboard under the "Environment" tab. The service will not start without them.

### 2. Verify Deployment

Check that your service is running:

```bash
# Health check endpoint
curl https://YOUR-APP-NAME.onrender.com/health
# Should return: OK

# Root endpoint (also returns health status)
curl https://YOUR-APP-NAME.onrender.com/
# Should return: MCP Server Running
```

### 3. Connect to Claude Desktop

After deployment, you'll get a URL like: `https://neo4j-mcp-server.onrender.com`

Add this to your Claude Desktop config:

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\\Claude\\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "neo4j-render": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://YOUR-APP-NAME.onrender.com/api/mcp/"
      ]
    }
  }
}
```

Restart Claude Desktop (Cmd/Ctrl + R).

## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|----------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` or `neo4j+s://xxxxx.databases.neo4j.io` |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `your-password` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `NEO4J_DATABASE` | Database name | `neo4j` |
| `NEO4J_READ_ONLY` | Enable read-only mode | `false` |
| `NEO4J_READ_TIMEOUT` | Query timeout (seconds) | `30` |
| `NEO4J_MCP_SERVER_ALLOW_ORIGINS` | CORS origins | `*` |

## How It Works

This deployment uses a Python wrapper script (`start.py`) that:
1. Runs a lightweight HTTP server for Render health checks on port 8080
2. Launches the MCP server alongside it
3. Responds to health checks at `/health` and `/` endpoints
4. Provides detailed logging for troubleshooting

This architecture ensures Render detects the service as "healthy" while the MCP server runs normally.

## Local Development

### Using Docker

```bash
# Build the image
docker build -t neo4j-mcp-server .

# Run with your Neo4j credentials
docker run -p 8080:8080 \
  -e NEO4J_URI=bolt://your-neo4j:7687 \
  -e NEO4J_USERNAME=neo4j \
  -e NEO4J_PASSWORD=password \
  neo4j-mcp-server
```

Test locally:
```bash
# Health check
curl http://localhost:8080/health

# View logs
docker logs <container-id>
```

### Direct Installation

```bash
# Install the package
pip install mcp-neo4j-cypher

# Run the wrapper script
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=password

python3 start.py
```

## Testing

### Health Check

```bash
# Simple health check
curl https://YOUR-APP-NAME.onrender.com/health

# Or check the root endpoint
curl https://YOUR-APP-NAME.onrender.com/
```

Both should return a 200 OK status.

### Test with Claude

Once connected, try these prompts in Claude:

- "What tools are available from my Neo4j MCP server?"
- "Show me the schema of my Neo4j database"
- "Find all Person nodes in the database"
- "How many nodes are in the database?"

## Render Free Tier Notes

⚠️ **Important:** Render's free tier spins down after 15 minutes of inactivity.

- First request after sleep: ~30-60 seconds
- Subsequent requests: Fast
- Health checks keep the service alive during active use

**Solutions:**
- Upgrade to Starter plan ($7/month) for always-on
- Use a keep-alive service like [Uptime Robot](https://uptimerobot.com/)
- Accept the cold start delay (only affects first request)

## Troubleshooting

### "No open ports detected" Error

**Fixed!** This repository now includes a health check wrapper that properly responds to Render's health checks. If you still see this error:

1. Ensure you've pulled the latest code with `start.py` and updated `Dockerfile`
2. Check that the container is building successfully in Render logs
3. Verify the `healthCheckPath: /health` is in your `render.yaml`

### Service won't start

**Check Render logs:**
1. Go to Render Dashboard → Your Service → Logs
2. Look for error messages

**Common issues:**
- ❌ Missing environment variables (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`)
- ❌ Neo4j URI not accessible from Render
- ❌ Incorrect Neo4j credentials
- ❌ Neo4j firewall blocking Render's IP addresses

**Solutions:**
```bash
# Verify your Neo4j connection locally first
python3 -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('YOUR_URI', auth=('USERNAME', 'PASSWORD'))
driver.verify_connectivity()
print('✓ Connection successful')
"
```

### Claude can't connect

```bash
# Test the MCP endpoint
curl https://YOUR-APP-NAME.onrender.com/api/mcp/

# Check service status
curl https://YOUR-APP-NAME.onrender.com/health
```

### Slow first request

This is normal on Render's free tier after 15 minutes of inactivity. The service spins down to save resources and needs 30-60 seconds to restart.

### Neo4j Connection Issues

If logs show "Failed to establish connection":

1. **Check Neo4j is running** and accessible
2. **Verify URI format:**
   - Local: `bolt://localhost:7687`
   - Neo4j Aura: `neo4j+s://xxxxx.databases.neo4j.io`
   - Cloud instance: `bolt://your-host:7687`
3. **Whitelist Render IPs** in Neo4j firewall (for Neo4j Aura/Cloud)
4. **Test connection** from command line first

## Documentation

- [Neo4j MCP Documentation](https://github.com/neo4j-contrib/mcp-neo4j)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Render Documentation](https://render.com/docs)
- [Claude Desktop MCP Setup](https://docs.anthropic.com/claude/docs/mcp)

## Architecture

```
┌─────────────────────────────────────┐
│   Render (Docker Container)         │
│  ┌──────────────────────────────┐   │
│  │  start.py wrapper            │   │
│  │  ├─ Health Server (port 8080)│   │
│  │  │  └─ /health endpoint      │   │
│  │  │  └─ / endpoint            │   │
│  │  └─ MCP Server               │   │
│  │     └─ /api/mcp/ endpoint    │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
           │
           ↓
    ┌──────────────┐
    │   Neo4j DB   │
    └──────────────┘
```

## License

MIT

## Credits

Built with:
- [mcp-neo4j-cypher](https://github.com/neo4j-contrib/mcp-neo4j) by Neo4j
- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic

## Contributing

Issues and pull requests are welcome! Please ensure:
- Health checks remain functional
- Environment variables are documented
- Render compatibility is maintained
