# Neo4j MCP Server

A Model Context Protocol (MCP) server for Neo4j database integration with Claude AI.

## 🚀 Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Overview

This MCP server enables Claude to interact with Neo4j graph databases using natural language. It provides:

- **Schema exploration** - Understand your graph structure
- **Cypher query execution** - Run read and write queries
- **Natural language interface** - Ask questions about your data
- **HTTP transport** - Remote access via Render deployment

## Deployment Instructions

### 1. Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect this GitHub repository
4. Render will auto-detect the `render.yaml` configuration
5. Add these **required environment variables**:
   ```
   NEO4J_URI=bolt://your-neo4j-host:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-secure-password
   ```
6. Click **Create Web Service**

### 2. Connect to Claude Desktop

After deployment, you'll get a URL like: `https://neo4j-mcp-server.onrender.com`

Add this to your Claude Desktop config:

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

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
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `your-password` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `NEO4J_DATABASE` | Database name | `neo4j` |
| `NEO4J_READ_ONLY` | Enable read-only mode | `false` |
| `NEO4J_READ_TIMEOUT` | Query timeout (seconds) | `30` |
| `NEO4J_MCP_SERVER_ALLOW_ORIGINS` | CORS origins | `https://claude.ai,https://claude.com` |

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

### Direct Installation

```bash
# Install the package
pip install mcp-neo4j-cypher

# Run the server
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=password

mcp-neo4j-cypher --transport http --host 0.0.0.0 --port 8080
```

## Testing

### Health Check

```bash
curl https://YOUR-APP-NAME.onrender.com/health
```

### Test with Claude

Once connected, try these prompts in Claude:

- "What tools are available from my Neo4j MCP server?"
- "Show me the schema of my Neo4j database"
- "Find all Person nodes in the database"

## Render Free Tier Notes

⚠️ **Important:** Render's free tier spins down after 15 minutes of inactivity.

- First request after sleep: ~30-60 seconds
- Subsequent requests: Fast

**Solutions:**
- Upgrade to Starter plan ($7/month) for always-on
- Use a keep-alive service like [Uptime Robot](https://uptimerobot.com/)

## Troubleshooting

### Service won't start
- Check logs in Render dashboard
- Verify environment variables are set correctly
- Ensure Neo4j URI is accessible from Render

### Claude can't connect
```bash
# Test the endpoint
curl https://YOUR-APP-NAME.onrender.com/api/mcp/
```

### Slow first request
- Normal on free tier after inactivity
- Consider upgrading to Starter plan

## Documentation

- [Neo4j MCP Documentation](https://github.com/neo4j-contrib/mcp-neo4j)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Render Documentation](https://render.com/docs)
- [Claude Desktop MCP Setup](https://docs.anthropic.com/claude/docs/mcp)

## License

MIT

## Credits

Built with:
- [mcp-neo4j-cypher](https://github.com/neo4j-contrib/mcp-neo4j) by Neo4j
- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic