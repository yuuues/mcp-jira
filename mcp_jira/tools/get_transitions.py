"""Get issue transitions tool."""
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class GetTransitionsService(MCPTool):
    """Service to get available transitions for a JIRA issue."""
    
    @property
    def name(self) -> str:
        return "get_transitions"
    
    @property
    def description(self) -> str:
        return "Get available workflow transitions for a JIRA issue. Returns the list of transitions that can be performed on the issue based on its current status and user permissions."
    
    async def execute(
        self,
        ctx: Context,
        issue_key: str,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get available transitions for a JIRA issue.
        
        Args:
            ctx: FastMCP context
            issue_key: The issue key (e.g., PROJ-123) or ID
            server: JIRA server URL override
            email: Email override
            token: API token override
            
        Returns:
            dict: Available transitions with id, name, and destination status
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}
        
        if not issue_key or not issue_key.strip():
            return {"error": "Issue key is required"}
        
        client = self.get_client(creds)
        try:
            result = await client.get(f"/issue/{issue_key}/transitions")
            return result
        finally:
            await client.close()
