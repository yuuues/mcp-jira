"""Clone issue tool."""
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class CloneIssueService(MCPTool):
    """Service to clone an existing JIRA issue into a new issue."""

    @property
    def name(self) -> str:
        return "clone_issue"

    @property
    def description(self) -> str:
        return (
            "Clone an existing JIRA issue. Creates a new issue in the same project with the same "
            "summary, description, issue type, priority, labels, story points, time estimate, and team. "
            "Does not copy assignee, status, or comments."
        )

    async def execute(
        self,
        ctx: Context,
        issue_key: str,
        copy_labels: bool = True,
        copy_priority: bool = True,
        copy_components: bool = False,
        copy_story_points: bool = True,
        copy_time_estimate: bool = True,
        copy_team: bool = True,
        story_points_field: str = "story_points",
        team_field: str = "customfield_10001",
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Clone a JIRA issue into a new issue.

        Args:
            ctx: FastMCP context
            issue_key: The issue key to clone (e.g., PROJ-123)
            copy_labels: Whether to copy labels to the new issue
            copy_priority: Whether to copy priority to the new issue
            copy_components: Whether to copy components to the new issue
            copy_story_points: Whether to copy story points estimation
            copy_time_estimate: Whether to copy original time estimate (timeoriginalestimate)
            copy_team: Whether to copy the team field
            story_points_field: Field name for story points (default "story_points"; use
                                 "customfield_10016" if your instance stores them there)
            team_field: Custom field name for the team (default "customfield_10001")
            server: JIRA server URL override
            email: Email override
            token: API token override

        Returns:
            dict: Created issue details (key, id) or error dictionary
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}

        if not issue_key or not issue_key.strip():
            return {"error": "Issue key is required"}

        # Build the fields list to fetch, including custom fields if needed
        fetch_fields = "summary,description,issuetype,project,priority,labels,components,timeoriginalestimate"
        if copy_story_points and story_points_field:
            fetch_fields += f",{story_points_field}"
        if copy_team and team_field:
            fetch_fields += f",{team_field}"

        client = self.get_client(creds)
        try:
            result = await client.get(
                f"/issue/{issue_key.strip()}",
                params={"fields": fetch_fields}
            )
            if result.get("error"):
                return result

            fields_data = result.get("fields") or {}
            project = fields_data.get("project")
            summary = fields_data.get("summary")
            issuetype = fields_data.get("issuetype")

            if not project or not project.get("key"):
                return {"error": "Source issue has no project"}
            if not summary:
                return {"error": "Source issue has no summary"}
            if not issuetype or not issuetype.get("name"):
                return {"error": "Source issue has no issue type"}

            new_fields: dict[str, Any] = {
                "project": {"key": project["key"]},
                "summary": summary,
                "issuetype": {"name": issuetype["name"]},
            }

            description = fields_data.get("description")
            if description and isinstance(description, dict):
                new_fields["description"] = description

            if copy_priority:
                priority = fields_data.get("priority")
                if priority and priority.get("name"):
                    new_fields["priority"] = {"name": priority["name"]}

            if copy_labels and fields_data.get("labels"):
                new_fields["labels"] = list(fields_data["labels"])

            if copy_components and fields_data.get("components"):
                new_fields["components"] = [
                    {"name": c.get("name")} for c in fields_data["components"] if c.get("name")
                ]

            if copy_story_points and story_points_field:
                sp_value = fields_data.get(story_points_field)
                if sp_value is not None:
                    new_fields[story_points_field] = sp_value

            if copy_time_estimate:
                time_estimate = fields_data.get("timeoriginalestimate")
                if time_estimate is not None:
                    new_fields["timeoriginalestimate"] = time_estimate

            if copy_team and team_field:
                team_value = fields_data.get(team_field)
                if team_value is not None:
                    new_fields[team_field] = team_value

            create_result = await client.post("/issue", json_data={"fields": new_fields})
            return create_result
        finally:
            await client.close()
