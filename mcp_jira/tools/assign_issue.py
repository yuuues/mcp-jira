"""Assign issue tool."""
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class AssignIssueService(MCPTool):
    """Service to assign a JIRA issue to a user."""
    
    @property
    def name(self) -> str:
        return "assign_issue"
    
    @property
    def description(self) -> str:
        return "Assign a JIRA issue to a user. Use the accountId of the user to assign, or set to null/-1 to unassign."
    
    async def execute(
        self,
        ctx: Context,
        issue_key: str,
        account_id: Optional[str] = None,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Assign a JIRA issue to a user.
        
        Args:
            ctx: FastMCP context
            issue_key: The issue key (e.g., PROJ-123) or ID
            account_id: The accountId of the user to assign. Use "-1" or None to unassign.
            server: JIRA server URL override
            email: Email override
            token: API token override
            
        Returns:
            dict: Success confirmation or error dictionary
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}
        
        if not issue_key or not issue_key.strip():
            return {"error": "Issue key is required"}
        
        body: dict[str, Any] = {}
        if account_id is None or account_id == "-1":
            body["accountId"] = None
        else:
            body["accountId"] = account_id
        
        client = self.get_client(creds)
        try:
            result = await client.put(
                f"/issue/{issue_key}/assignee",
                json_data=body
            )
            
            if result.get("success"):
                if account_id and account_id != "-1":
                    return {"success": True, "message": f"Issue {issue_key} assigned to {account_id}"}
                else:
                    return {"success": True, "message": f"Issue {issue_key} unassigned"}
            return result
        finally:
            await client.close()
