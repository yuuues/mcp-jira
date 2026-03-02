"""Credential management for JIRA connections."""
import os
from dataclasses import dataclass
from typing import Optional

try:
    from fastmcp import Context
except ImportError:
    Context = None


@dataclass
class JiraCredentials:
    """Data class for JIRA credentials."""
    server: Optional[str] = None
    email: Optional[str] = None
    token: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if credentials have all required fields."""
        return bool(self.server and self.email and self.token)

    def get_base_url(self) -> str:
        """Get the base URL for JIRA API calls."""
        if not self.server:
            return ""
        server = self.server.rstrip("/")
        if not server.startswith("http"):
            server = f"https://{server}"
        return server

    def mask_token(self) -> str:
        """Return a masked version of the token for logging."""
        if not self.token or len(self.token) <= 6:
            return "***"
        return f"{self.token[:3]}...{self.token[-3:]}"


class CredentialsManager:
    """Manages credential retrieval from multiple sources with priority."""
    
    @staticmethod
    def get_from_context(
        ctx: Optional["Context"],
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> JiraCredentials:
        """
        Extract credentials with priority:
        1. Function parameters (highest)
        2. HTTP Headers (X-MCP-JIRA-*)
        3. Environment variables (lowest)
        """
        creds = JiraCredentials(server, email, token)
        
        creds = CredentialsManager._get_from_headers(ctx, creds)
        creds = CredentialsManager._get_from_environment(creds)
        
        return creds

    @staticmethod
    def _get_from_headers(ctx: Optional["Context"], creds: JiraCredentials) -> JiraCredentials:
        """Extract credentials from HTTP headers."""
        if not ctx or not hasattr(ctx, 'request_context'):
            return creds
            
        req_ctx = ctx.request_context
        if not hasattr(req_ctx, 'request'):
            return creds
            
        headers = req_ctx.request.headers
        
        creds.server = creds.server or headers.get('x-mcp-jira-server')
        creds.email = creds.email or headers.get('x-mcp-jira-email')
        creds.token = creds.token or headers.get('x-mcp-jira-token')
        
        if creds.server or creds.email or creds.token:
            print(f"[credentials] Loaded from HTTP headers (client: {headers.get('user-agent', 'unknown')})")
        
        return creds

    @staticmethod
    def _get_from_environment(creds: JiraCredentials) -> JiraCredentials:
        """Extract credentials from environment variables."""
        creds.server = creds.server or os.getenv('MCP_JIRA_SERVER')
        creds.email = creds.email or os.getenv('MCP_JIRA_EMAIL')
        creds.token = creds.token or os.getenv('MCP_JIRA_TOKEN')
        
        return creds
