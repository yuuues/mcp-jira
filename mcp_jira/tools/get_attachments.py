"""Get attachments from a JIRA issue tool."""
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class GetAttachmentsService(MCPTool):
    """Service to list all attachments of a JIRA issue."""

    @property
    def name(self) -> str:
        return "get_attachments"

    @property
    def description(self) -> str:
        return "List all attachments of a JIRA issue. Returns attachment details including ID, filename, size, MIME type, creation date, and download URL."

    async def execute(
        self,
        ctx: Context,
        issue_key: str,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get all attachments of a JIRA issue.

        Args:
            ctx: FastMCP context
            issue_key: The issue key (e.g., PROJ-123)
            server: JIRA server URL override
            email: Email override
            token: API token override

        Returns:
            dict: List of attachments or error dictionary
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}

        if not issue_key or not issue_key.strip():
            return {"error": "Issue key is required"}

        client = self.get_client(creds)
        try:
            result = await client.get(
                f"/issue/{issue_key.strip()}",
                params={"fields": "attachment"}
            )
            if result.get("error"):
                return result

            attachments_raw = (result.get("fields") or {}).get("attachment") or []

            attachments = [
                {
                    "id": att.get("id"),
                    "filename": att.get("filename"),
                    "size": att.get("size"),
                    "mime_type": att.get("mimeType"),
                    "created": att.get("created"),
                    "content_url": att.get("content"),
                    "thumbnail_url": att.get("thumbnail"),
                    "author": (att.get("author") or {}).get("displayName"),
                }
                for att in attachments_raw
            ]

            return {
                "issue_key": issue_key.strip().upper(),
                "total": len(attachments),
                "attachments": attachments,
            }
        finally:
            await client.close()
