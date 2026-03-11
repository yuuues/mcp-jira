"""Get field options tool."""
from typing import Any, Optional

from fastmcp import Context
from .base import MCPTool


class GetFieldOptionsService(MCPTool):
    """Service to retrieve allowed values for a Jira custom field dropdown."""

    @property
    def name(self) -> str:
        return "get_field_options"

    @property
    def description(self) -> str:
        return "Get the allowed values (options) for a Jira custom field dropdown. Useful for finding valid team IDs, custom field values, etc. Pass the field ID such as 'customfield_10029'."

    async def execute(
        self,
        ctx: Context,
        field_id: str,
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get allowed values for a Jira custom field.

        Args:
            ctx: FastMCP context
            field_id: The custom field ID (e.g., "customfield_10029")
            server: JIRA server URL override
            email: Email override
            token: API token override

        Returns:
            dict: Field options grouped by context, or error dictionary
        """
        creds = self.get_credentials(ctx, server, email, token)
        is_valid, error = self.validate_credentials(creds)
        if not is_valid:
            return {"error": error}

        if not field_id or not field_id.strip():
            return {"error": "field_id is required"}

        field_id = field_id.strip()
        client = self.get_client(creds)
        try:
            contexts_response = await client.get(f"/field/{field_id}/context")
            if contexts_response.get("error"):
                return contexts_response

            contexts = contexts_response.get("values", [])
            if not contexts:
                return {"field_id": field_id, "contexts": [], "options": []}

            all_options = []
            for context in contexts:
                context_id = context.get("id")
                options_response = await client.get(
                    f"/field/{field_id}/context/{context_id}/option",
                    params={"maxResults": 100}
                )
                if options_response.get("error"):
                    continue

                for option in options_response.get("values", []):
                    all_options.append({
                        "id": option.get("id"),
                        "value": option.get("value"),
                        "context_id": context_id,
                        "context_name": context.get("name"),
                    })

            return {
                "field_id": field_id,
                "options": all_options,
                "total": len(all_options),
            }
        finally:
            await client.close()
