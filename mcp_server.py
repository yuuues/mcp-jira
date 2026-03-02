"""MCP JIRA Server - Entry point."""
import os
import argparse

from mcp_jira import MCPJiraServer


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Start MCP JIRA server")
    parser.add_argument("--server", dest="server", help="JIRA server URL (e.g., your-domain.atlassian.net)")
    parser.add_argument("--email", dest="email", help="Atlassian account email")
    parser.add_argument("--token", dest="token", help="JIRA API token")
    parser.add_argument("--port", dest="port", type=int, help="Port to bind")
    args = parser.parse_args()

    if args.server:
        os.environ["MCP_JIRA_SERVER"] = args.server
    if args.email:
        os.environ["MCP_JIRA_EMAIL"] = args.email
    if args.token:
        os.environ["MCP_JIRA_TOKEN"] = args.token

    if args.port is not None:
        port = args.port
    else:
        port_str = os.getenv("MCP_PORT") or os.getenv("PORT") or "3940"
        try:
            port = int(port_str)
        except ValueError:
            port = 3940

    server = MCPJiraServer()
    server.run(port)


if __name__ == "__main__":
    main()
