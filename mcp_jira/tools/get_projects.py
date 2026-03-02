"""Get projects tool."""
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class GetProjectsService(MCPTool):
    """Service to list JIRA projects."""
    
    @property
    def name(self) -> str:
        return "get_projects"
    
    @property
    def description(self) -> str:
        return "Get a list of all JIRA projects accessible to the authenticated user. Returns project key, name, and basic details."
    
    async def execute(
        self,
        ctx: Context,
        expand: Optional[str] = None,
        recent: Optional[int] = None,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get list of JIRA projects.
        
        Args:
            ctx: FastMCP context
            expand: Comma-separated list of fields to expand (e.g., "description,lead")
            recent: Number of recent projects to return (if specified, returns recently accessed projects)
            server: JIRA server URL override
            email: Email override
            token: API token override
            
        Returns:
            dict: List of projects or error dictionary
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
            if recent is not None:
                params["recent"] = recent
            
            result = await client.get("/project", params=params if params else None)
            
            if isinstance(result, list):
                return {"projects": result, "total": len(result)}
            return result
        finally:
            await client.close()
