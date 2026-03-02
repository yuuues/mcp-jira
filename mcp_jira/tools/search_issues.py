"""Search issues with JQL tool."""
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class SearchIssuesService(MCPTool):
    """Service to search JIRA issues using JQL."""
    
    @property
    def name(self) -> str:
        return "search_issues"
    
    @property
    def description(self) -> str:
        return "Search for JIRA issues using JQL (JIRA Query Language). Returns a list of issues matching the query with pagination support."
    
    async def execute(
        self,
        ctx: Context,
        jql: str,
        fields: Optional[str] = None,
        max_results: int = 50,
        next_page_token: Optional[str] = None,
        expand: Optional[str] = None,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Search for JIRA issues using JQL (enhanced search API).
        
        Args:
            ctx: FastMCP context
            jql: JQL query string (e.g., "project = PROJ AND status = Open")
            fields: Comma-separated list of fields to return (e.g., "summary,status,assignee")
            max_results: Maximum number of results to return (default 50, max 100)
            next_page_token: Token for pagination (returned in previous response)
            expand: Comma-separated list of fields to expand
            server: JIRA server URL override
            email: Email override
            token: API token override
            
        Returns:
            dict: Search results with issues array and pagination info (nextPageToken)
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}
        
        if not jql or not jql.strip():
            return {"error": "JQL query is required"}
        
        max_results = min(max(1, max_results), 100)
        
        client = self.get_client(creds)
        try:
            body = {
                "jql": jql,
                "maxResults": max_results,
            }
            
            if fields:
                body["fields"] = [f.strip() for f in fields.split(",")]
            
            if expand:
                body["expand"] = expand
            
            if next_page_token:
                body["nextPageToken"] = next_page_token
            
            result = await client.post("/search/jql", json_data=body)
            return result
        finally:
            await client.close()
