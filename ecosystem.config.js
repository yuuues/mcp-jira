const path = require("path");

module.exports = {
  apps: [
    {
      name: "mcp-jira",
      script: "mcp_server.py",
      interpreter: path.join(__dirname, "venv", "bin", "python"),
      cwd: __dirname,
      env: {
        //MCP_JIRA_SERVER: "your-domain.atlassian.net",
        //MCP_JIRA_EMAIL: "user@example.com",
        //MCP_JIRA_TOKEN: "your-api-token",
        MCP_PORT: 35002,
      },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 1000,
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      error_file: "logs/mcp-jira-error.log",
      out_file: "logs/mcp-jira-out.log",
      merge_logs: true,
    },
  ],
};
