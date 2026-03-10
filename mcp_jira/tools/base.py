"""Base class for MCP tools/services."""
import re
from abc import ABC, abstractmethod
from typing import Any, Optional

try:
    from fastmcp import Context
except ImportError:
    Context = None

from ..credentials import CredentialsManager, JiraCredentials
from ..client import JiraClient


class MCPTool(ABC):
    """Abstract base class for MCP tools."""
    
    def __init__(self, credentials_manager: CredentialsManager):
        """
        Initialize the tool.
        
        Args:
            credentials_manager: Manager for credential resolution
        """
        self.creds_manager = credentials_manager
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (used for registration)."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description (used in MCP metadata)."""
        pass
    
    @abstractmethod
    async def execute(self, ctx: "Context", *args, **kwargs) -> Any:
        """
        Execute the tool logic.
        
        Note: Implementations should define explicit parameters instead of **kwargs.
        FastMCP requires explicit parameter definitions for tool registration.
        """
        pass
    
    def get_credentials(
        self,
        ctx: "Context",
        server: Optional[str] = None,
        email: Optional[str] = None,
        token: Optional[str] = None
    ) -> JiraCredentials:
        """
        Get credentials from context and optional overrides.
        
        Args:
            ctx: FastMCP context
            server: Optional server override
            email: Optional email override
            token: Optional token override
            
        Returns:
            JiraCredentials instance
        """
        return self.creds_manager.get_from_context(ctx, server, email, token)
    
    def get_client(self, credentials: JiraCredentials) -> JiraClient:
        """
        Create a JIRA client with the given credentials.
        
        Args:
            credentials: JIRA credentials
            
        Returns:
            JiraClient instance
        """
        return JiraClient(credentials)
    
    @staticmethod
    def parse_time_estimate(value: str) -> tuple[Optional[int], Optional[str]]:
        """
        Parse a human-readable time estimate string into seconds.

        Accepts Jira-style notation (1w 2d 3h 30m) or a plain integer string
        interpreted as seconds. Assumptions: 1w = 5d, 1d = 8h.

        Args:
            value: Time string such as "2h 30m", "1d", "3600", "1w 2d 4h"

        Returns:
            tuple: (seconds: int | None, error_message: str | None)
        """
        value = value.strip()
        if not value:
            return None, "Time estimate cannot be empty"

        # Plain integer → treat as seconds directly
        if re.fullmatch(r"\d+", value):
            return int(value), None

        units = {"w": 5 * 8 * 3600, "d": 8 * 3600, "h": 3600, "m": 60}
        pattern = re.compile(r"(\d+)\s*([wdhm])", re.IGNORECASE)
        matches = pattern.findall(value)

        # Reject if nothing was parsed or there is unexpected text left over
        reconstructed = re.sub(r"\s+", "", "".join(f"{n}{u}" for n, u in matches))
        normalised = re.sub(r"\s+", "", value.lower())
        if not matches or reconstructed.lower() != normalised:
            return None, (
                f"Invalid time estimate format: '{value}'. "
                "Use Jira notation such as '2h 30m', '1d', '1w 2d 4h 30m', or a plain integer (seconds)."
            )

        seconds = sum(int(n) * units[u.lower()] for n, u in matches)
        return seconds, None

    def validate_credentials(self, credentials: JiraCredentials) -> tuple[bool, Optional[str]]:
        """
        Validate that credentials are complete.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not credentials.is_valid():
            missing = []
            if not credentials.server:
                missing.append("server")
            if not credentials.email:
                missing.append("email")
            if not credentials.token:
                missing.append("token")
            return False, f"Missing credentials: {', '.join(missing)}"
        return True, None
