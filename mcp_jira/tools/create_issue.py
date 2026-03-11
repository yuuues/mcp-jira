"""Create issue tool."""
from typing import Any, Optional

from fastmcp import Context
from .adf import markdown_to_adf
from .base import MCPTool


class CreateIssueService(MCPTool):
    """Service to create a new JIRA issue."""
    
    @property
    def name(self) -> str:
        return "create_issue"
    
    @property
    def description(self) -> str:
        return "Create a new JIRA issue. Requires project key, summary, and issue type. Optionally accepts description, priority, assignee, labels, time estimate, and custom fields."
    
    async def execute(
        self,
        ctx: Context,
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_account_id: Optional[str] = None,
        labels: Optional[str] = None,
        parent_key: Optional[str] = None,
        components: Optional[str] = None,
        time_estimate: Optional[str] = None,
        team_id: Optional[str] = None,
        sprint_id: Optional[int] = None,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Create a new JIRA issue.
        
        Args:
            ctx: FastMCP context
            project_key: The project key (e.g., PROJ)
            summary: Issue summary/title
            issue_type: Issue type name (e.g., "Task", "Bug", "Story", "Epic", "Sub-task")
            description: Issue description (plain text, will be converted to ADF)
            priority: Priority name (e.g., "High", "Medium", "Low")
            assignee_account_id: Account ID of the assignee
            labels: Comma-separated list of labels (e.g., "backend,urgent")
            parent_key: Parent issue key for sub-tasks or issues under an Epic (e.g., PROJ-123)
            components: Comma-separated list of component names
            time_estimate: Original time estimate in Jira notation (e.g., "2h 30m", "1d", "1w 2d")
            team_id: Team ID to assign (maps to customfield_10001)
            sprint_id: ID of the Sprint to assign the issue to after creation
            server: JIRA server URL override
            email: Email override
            token: API token override
            
        Returns:
            dict: Created issue details including key and id, or error dictionary
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}
        
        if not project_key or not project_key.strip():
            return {"error": "Project key is required"}
        
        if not summary or not summary.strip():
            return {"error": "Summary is required"}
        
        if not issue_type or not issue_type.strip():
            return {"error": "Issue type is required"}
        
        fields: dict[str, Any] = {
            "project": {"key": project_key.strip()},
            "summary": summary.strip(),
            "issuetype": {"name": issue_type.strip()},
        }
        
        if description:
            fields["description"] = markdown_to_adf(description)
        
        if priority:
            fields["priority"] = {"name": priority.strip()}
        
        if assignee_account_id:
            fields["assignee"] = {"accountId": assignee_account_id.strip()}
        
        if labels:
            fields["labels"] = [label.strip() for label in labels.split(",") if label.strip()]
        
        if parent_key:
            fields["parent"] = {"key": parent_key.strip()}
        
        if components:
            fields["components"] = [
                {"name": comp.strip()} for comp in components.split(",") if comp.strip()
            ]

        if time_estimate:
            err = self.validate_time_estimate(time_estimate)
            if err:
                return {"error": err}
            fields["timetracking"] = {"originalEstimate": time_estimate.strip()}

        if team_id:
            fields["customfield_10001"] = {"id": team_id.strip()}

        client = self.get_client(creds)
        try:
            result = await client.post("/issue", json_data={"fields": fields})
            if result.get("error"):
                return result

            if sprint_id is not None:
                issue_key = result.get("key")
                httpx_client = await client._get_client()
                import httpx
                agile_url = f"{creds.get_base_url()}/rest/agile/1.0/sprint/{sprint_id}/issue"
                try:
                    sprint_resp = await httpx_client.post(
                        agile_url,
                        json={"issues": [issue_key]}
                    )
                    sprint_resp.raise_for_status()
                    result["sprint"] = {"success": True}
                except httpx.HTTPStatusError as e:
                    result["sprint"] = {
                        "error": True,
                        "status_code": e.response.status_code,
                        "message": client._parse_error_response(e.response)
                    }
                except Exception as e:
                    result["sprint"] = {"error": True, "message": str(e)}

            return result
        finally:
            await client.close()
