"""Edit issue tool."""
from typing import Any, Optional

from fastmcp import Context
from .adf import markdown_to_adf
from .base import MCPTool


class EditIssueService(MCPTool):
    """Service to edit an existing JIRA issue."""

    @property
    def name(self) -> str:
        return "edit_issue"

    @property
    def description(self) -> str:
        return "Edit an existing JIRA issue. Allows updating summary, description, priority, labels, assignee, components, epic, sprint, and time estimate. Only provided fields will be updated."

    async def execute(
        self,
        ctx: Context,
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_account_id: Optional[str] = None,
        labels: Optional[str] = None,
        components: Optional[str] = None,
        parent_key: Optional[str] = None,
        sprint_id: Optional[int] = None,
        time_estimate: Optional[str] = None,
        team_id: Optional[str] = None,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Edit a JIRA issue.

        Args:
            ctx: FastMCP context
            issue_key: The issue key (e.g., PROJ-123)
            summary: New issue summary/title
            description: New issue description (plain text, will be converted to ADF)
            priority: New priority name (e.g., "High", "Medium", "Low")
            assignee_account_id: New assignee account ID
            labels: New comma-separated list of labels (replaces existing ones)
            components: New comma-separated list of component names (replaces existing ones)
            parent_key: Key of the parent issue or Epic to assign to (e.g., PROJ-100). Pass empty string to remove.
            sprint_id: ID of the Sprint to assign to
            time_estimate: New original time estimate in Jira notation (e.g., "2h 30m", "1d", "1w 2d"). Pass "0" to clear.
            team_id: Team ID to assign (maps to customfield_10001). Pass empty string to clear.
            server: JIRA server URL override
            email: Email override
            token: API token override

        Returns:
            dict: Success status or error dictionary
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}

        if not issue_key or not issue_key.strip():
            return {"error": "Issue key is required"}

        fields: dict[str, Any] = {}

        if summary is not None:
            if not summary.strip():
                return {"error": "Summary cannot be empty if provided"}
            fields["summary"] = summary.strip()

        if description is not None:
            fields["description"] = markdown_to_adf(description)

        if priority is not None:
            fields["priority"] = {"name": priority.strip()}

        if assignee_account_id is not None:
            if not assignee_account_id.strip():
                # To unassign, typically we pass null or accountId: null, but Jira API usually accepts null for assignee
                fields["assignee"] = None
            else:
                fields["assignee"] = {"accountId": assignee_account_id.strip()}

        if labels is not None:
            if not labels.strip():
                fields["labels"] = []
            else:
                fields["labels"] = [label.strip() for label in labels.split(",") if label.strip()]

        if components is not None:
            if not components.strip():
                fields["components"] = []
            else:
                fields["components"] = [
                    {"name": comp.strip()} for comp in components.split(",") if comp.strip()
                ]

        if parent_key is not None:
            if not parent_key.strip():
                fields["parent"] = None
            else:
                fields["parent"] = {"key": parent_key.strip()}

        if time_estimate is not None:
            err = self.validate_time_estimate(time_estimate)
            if err:
                return {"error": err}
            if time_estimate.strip() == "0":
                fields["timetracking"] = {"originalEstimate": "0", "remainingEstimate": "0"}
            else:
                fields["timetracking"] = {"originalEstimate": time_estimate.strip()}

        if team_id is not None:
            if not team_id.strip():
                fields["customfield_10001"] = None
            else:
                fields["customfield_10001"] = {"id": team_id.strip()}

        client = self.get_client(creds)
        try:
            results = {}
            if fields:
                # Jira API sometimes doesn't accept null for parent in the same way, but let's try
                # If parent removal fails, the user might see an error.
                result_put = await client.put(f"/issue/{issue_key.strip()}", json_data={"fields": fields})
                results["edit"] = result_put
                if result_put.get("error"):
                    return result_put

            if sprint_id is not None:
                # Use Agile API for sprint assignment
                httpx_client = await client._get_client()
                agile_url = f"{creds.get_base_url()}/rest/agile/1.0/sprint/{sprint_id}/issue"
                import httpx
                try:
                    sprint_resp = await httpx_client.post(
                        agile_url,
                        json={"issues": [issue_key.strip()]}
                    )
                    sprint_resp.raise_for_status()
                    results["sprint"] = {"success": True}
                except httpx.HTTPStatusError as e:
                    results["sprint"] = {
                        "error": True,
                        "status_code": e.response.status_code,
                        "message": client._parse_error_response(e.response)
                    }
                except Exception as e:
                    results["sprint"] = {"error": True, "message": str(e)}

            if not fields and sprint_id is None:
                return {"error": "No fields provided to update"}

            return results
        finally:
            await client.close()
