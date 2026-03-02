# MCP JIRA Server

A Model Context Protocol (MCP) server for interacting with JIRA Cloud. This server provides tools to search issues, add comments, manage transitions, and more.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### JIRA API Token

1. Go to https://id.atlassian.com/manage/api-tokens
2. Create a new API token
3. Use your Atlassian email and the token for authentication

### Environment Variables

You can configure the server using environment variables:

```bash
export MCP_JIRA_SERVER=your-domain.atlassian.net
export MCP_JIRA_EMAIL=user@example.com
export MCP_JIRA_TOKEN=your-api-token
export MCP_PORT=35002
```

Or copy `.env.example` to `.env` and fill in your values.

## Usage

### Command Line

```bash
python mcp_server.py --server your-domain.atlassian.net --email user@example.com --token YOUR_API_TOKEN --port 35002
```

### Client Configuration (mcp.json)

```json
{
  "mcpServers": {
    "mcp-jira": {
      "url": "http://localhost:35002/mcp",
      "headers": {
        "X-MCP-JIRA-SERVER": "your-domain.atlassian.net",
        "X-MCP-JIRA-EMAIL": "user@example.com",
        "X-MCP-JIRA-TOKEN": "your-api-token"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `get_issue` | Get details of a single issue |
| `search_issues` | Search issues using JQL |
| `add_comment` | Add a comment to an issue |
| `get_transitions` | Get available transitions for an issue |
| `transition_issue` | Change the status of an issue |
| `get_projects` | List all accessible projects |
| `assign_issue` | Assign an issue to a user |
| `get_myself` | Get information about the authenticated user |

## Authentication

The server supports multiple credential sources with the following priority:

1. Function parameters (highest priority)
2. HTTP Headers (`X-MCP-JIRA-*`)
3. Environment variables (lowest priority)

### HTTP Headers

- `X-MCP-JIRA-SERVER`: JIRA server URL (e.g., `your-domain.atlassian.net`)
- `X-MCP-JIRA-EMAIL`: Atlassian account email
- `X-MCP-JIRA-TOKEN`: API token

---

## 📄 Licencia

Yuuu

MIT

---

**Última actualización:** Marzo 2026  
 
