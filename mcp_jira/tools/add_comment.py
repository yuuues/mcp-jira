"""Add comment to issue tool."""
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class AddCommentService(MCPTool):
    """Service to add a comment to a JIRA issue."""
    
    @property
    def name(self) -> str:
        return "add_comment"
    
    @property
    def description(self) -> str:
        return "Add a comment to a JIRA issue. The comment body supports Atlassian Document Format (ADF) or can be provided as plain text."
    
    async def execute(
        self,
        ctx: Context,
        issue_key: str,
        body: str,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Add a comment to a JIRA issue.
        
        Args:
            ctx: FastMCP context
            issue_key: The issue key (e.g., PROJ-123) or ID
            body: Comment text (plain text, will be converted to ADF)
            server: JIRA server URL override
            email: Email override
            token: API token override
            
        Returns:
            dict: Created comment details or error dictionary
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}
        
        if not issue_key or not issue_key.strip():
            return {"error": "Issue key is required"}
        
        if not body or not body.strip():
            return {"error": "Comment body is required"}
        
        adf_body = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": body
                        }
                    ]
                }
            ]
        }
        
        client = self.get_client(creds)
        try:
            result = await client.post(
                f"/issue/{issue_key}/comment",
                json_data={"body": adf_body}
            )
            return result
        finally:
            await client.close()
