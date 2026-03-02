"""Get current user info tool."""
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class GetMyselfService(MCPTool):
    """Service to get information about the authenticated user."""
    
    @property
    def name(self) -> str:
        return "get_myself"
    
    @property
    def description(self) -> str:
        return "Get information about the currently authenticated JIRA user. Returns account ID, email, display name, and other profile details."
    
    async def execute(
        self,
        ctx: Context,
        expand: Optional[str] = None,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get information about the authenticated user.
        
        Args:
            ctx: FastMCP context
            expand: Comma-separated list of fields to expand (e.g., "groups,applicationRoles")
            server: JIRA server URL override
            email: Email override
            token: API token override
            
        Returns:
            dict: User information or error dictionary
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}
        
        client = self.get_client(creds)
        try:
            params = {}
            if expand:
                params["expand"] = expand
            
            result = await client.get("/myself", params=params if params else None)
            return result
        finally:
            await client.close()
