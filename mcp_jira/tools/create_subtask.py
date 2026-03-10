"""Create subtask tool."""
from typing import Any, Optional

from fastmcp import Context
from .adf import markdown_to_adf
from .base import MCPTool


class CreateSubtaskService(MCPTool):
    """Service to create a new JIRA sub-task under a parent issue."""

    @property
    def name(self) -> str:
        return "create_subtask"

    @property
    def description(self) -> str:
        return "Create a new JIRA sub-task under an existing issue. Requires parent issue key and summary. Optionally accepts description, priority, assignee, and labels."

    async def execute(
        self,
        ctx: Context,
        parent_key: str,
        summary: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_account_id: Optional[str] = None,
        labels: Optional[str] = None,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Create a new JIRA sub-task.

        Args:
            ctx: FastMCP context
            parent_key: The parent issue key (e.g., PROJ-123)
            summary: Sub-task summary/title
            description: Sub-task description (plain text, converted to ADF)
            priority: Priority name (e.g., "High", "Medium", "Low")
            assignee_account_id: Account ID of the assignee
            labels: Comma-separated list of labels
            server: JIRA server URL override
            email: Email override
            token: API token override

        Returns:
            dict: Created sub-task details (key, id) or error dictionary
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}

        if not parent_key or not parent_key.strip():
            return {"error": "Parent issue key is required"}

        if not summary or not summary.strip():
            return {"error": "Summary is required"}

        client = self.get_client(creds)
        try:
            parent_result = await client.get(
                f"/issue/{parent_key.strip()}",
                params={"fields": "project"}
            )
            if parent_result.get("error"):
                return parent_result

            fields_data = parent_result.get("fields") or {}
            project = fields_data.get("project")
            if not project or not project.get("key"):
                return {"error": "Parent issue has no project"}

            project_key = project["key"]

            fields: dict[str, Any] = {
                "project": {"key": project_key},
                "parent": {"key": parent_key.strip()},
                "summary": summary.strip(),
                "issuetype": {"name": "Sub-task"},
            }

            if description:
                fields["description"] = markdown_to_adf(description)

            if priority:
                fields["priority"] = {"name": priority.strip()}

            if assignee_account_id:
                fields["assignee"] = {"accountId": assignee_account_id.strip()}

            if labels:
                fields["labels"] = [label.strip() for label in labels.split(",") if label.strip()]

            result = await client.post("/issue", json_data={"fields": fields})
            return result
        finally:
            await client.close()
