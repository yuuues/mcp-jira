"""Get issue details tool."""
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class GetIssueService(MCPTool):
    """Service to get details of a single JIRA issue."""
    
    @property
    def name(self) -> str:
        return "get_issue"
    
    @property
    def description(self) -> str:
        return "Get details of a JIRA issue by its key (e.g., PROJ-123) or ID. Returns issue fields including summary, description, status, assignee, and more."
    
    async def execute(
        self,
        ctx: Context,
        issue_key: str,
        fields: Optional[str] = None,
        expand: Optional[str] = None,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get details of a JIRA issue.
        
        Args:
            ctx: FastMCP context
            issue_key: The issue key (e.g., PROJ-123) or ID
            fields: Comma-separated list of fields to return (e.g., "summary,status,assignee")
            expand: Comma-separated list of fields to expand (e.g., "renderedFields,changelog")
            server: JIRA server URL override
            email: Email override
            token: API token override
            
        Returns:
            dict: Issue details or error dictionary
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}
        
        if not issue_key or not issue_key.strip():
            return {"error": "Issue key is required"}
        
        client = self.get_client(creds)
        try:
            params = {}
            if fields:
                params["fields"] = fields
            if expand:
                params["expand"] = expand
            
            result = await client.get(f"/issue/{issue_key}", params=params if params else None)
            return result
        finally:
            await client.close()
