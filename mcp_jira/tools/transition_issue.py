"""Transition issue tool."""
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class TransitionIssueService(MCPTool):
    """Service to transition a JIRA issue to a new status."""
    
    @property
    def name(self) -> str:
        return "transition_issue"
    
    @property
    def description(self) -> str:
        return "Transition a JIRA issue to a new status. Use get_transitions first to get available transition IDs for the issue."
    
    async def execute(
        self,
        ctx: Context,
        issue_key: str,
        transition_id: str,
        comment: Optional[str] = None,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Transition a JIRA issue to a new status.
        
        Args:
            ctx: FastMCP context
            issue_key: The issue key (e.g., PROJ-123) or ID
            transition_id: The ID of the transition to perform (get from get_transitions)
            comment: Optional comment to add during transition
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
        
        if not transition_id or not str(transition_id).strip():
            return {"error": "Transition ID is required. Use get_transitions to get available transitions."}
        
        body: dict[str, Any] = {
            "transition": {
                "id": str(transition_id)
            }
        }
        
        if comment:
            adf_comment = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
            body["update"] = {
                "comment": [
                    {
                        "add": {
                            "body": adf_comment
                        }
                    }
                ]
            }
        
        client = self.get_client(creds)
        try:
            result = await client.post(
                f"/issue/{issue_key}/transitions",
                json_data=body
            )
            
            if result.get("success"):
                return {"success": True, "message": f"Issue {issue_key} transitioned successfully"}
            return result
        finally:
            await client.close()
