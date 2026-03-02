"""MCP JIRA - A Model Context Protocol server for JIRA Cloud."""

from .server import MCPJiraServer
from .credentials import JiraCredentials, CredentialsManager
from .client import JiraClient

__all__ = [
    'MCPJiraServer',
    'JiraCredentials',
    'CredentialsManager',
    'JiraClient',
]

__version__ = "1.0.0"
