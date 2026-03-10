"""Download a JIRA issue attachment tool."""
import os
import tempfile
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class DownloadAttachmentService(MCPTool):
    """Service to download an attachment from a JIRA issue."""

    @property
    def name(self) -> str:
        return "download_attachment"

    @property
    def description(self) -> str:
        return "Download an attachment from a JIRA issue by its attachment ID. Returns the local path where the file was saved. If no download path is provided, the file is saved to the system's temporary directory."

    async def execute(
        self,
        ctx: Context,
        attachment_id: str,
        download_path: Optional[str] = None,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Download an attachment from a JIRA issue.

        Args:
            ctx: FastMCP context
            attachment_id: The attachment ID (obtained via get_attachments)
            download_path: Local path where the file should be saved. If omitted,
                           saved to the system temp directory using the original filename.
            server: JIRA server URL override
            email: Email override
            token: API token override

        Returns:
            dict: Saved file path and attachment metadata, or error dictionary
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}

        if not attachment_id or not attachment_id.strip():
            return {"error": "Attachment ID is required"}

        client = self.get_client(creds)
        try:
            meta = await client.get(f"/attachment/{attachment_id.strip()}")
            if meta.get("error"):
                return meta

            filename = meta.get("filename") or f"attachment_{attachment_id.strip()}"
            content_url = meta.get("content")
            if not content_url:
                return {"error": "Attachment has no downloadable content URL"}

            if download_path:
                if os.path.isdir(download_path):
                    local_path = os.path.join(download_path, filename)
                else:
                    local_path = download_path
            else:
                local_path = os.path.join(tempfile.gettempdir(), filename)

            result = await client.download_file(content_url, local_path)
            if result.get("error"):
                return result

            return {
                "success": True,
                "path": result["path"],
                "filename": filename,
                "mime_type": meta.get("mimeType"),
                "size": meta.get("size"),
            }
        finally:
            await client.close()
