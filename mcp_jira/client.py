"""JIRA HTTP Client wrapper."""
import base64
from typing import Any, Optional

import httpx

from .credentials import JiraCredentials


class JiraClient:
    """HTTP client for JIRA REST API v3."""
    
    def __init__(self, credentials: JiraCredentials, timeout: float = 30.0):
        """
        Initialize the JIRA client.
        
        Args:
            credentials: JIRA credentials
            timeout: Request timeout in seconds
        """
        self.credentials = credentials
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def base_url(self) -> str:
        """Get the base URL for API calls."""
        return f"{self.credentials.get_base_url()}/rest/api/3"
    
    def _get_auth_header(self) -> str:
        """Generate Basic auth header."""
        auth_string = f"{self.credentials.email}:{self.credentials.token}"
        encoded = base64.b64encode(auth_string.encode()).decode()
        return f"Basic {encoded}"
    
    def _get_headers(self) -> dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self._get_headers(),
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def get(self, endpoint: str, params: Optional[dict] = None) -> dict[str, Any]:
        """
        Make a GET request to the JIRA API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        client = await self._get_client()
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": True,
                "status_code": e.response.status_code,
                "message": self._parse_error_response(e.response),
            }
        except httpx.RequestError as e:
            return {
                "error": True,
                "message": str(e),
            }
    
    async def post(self, endpoint: str, json_data: Optional[dict] = None) -> dict[str, Any]:
        """
        Make a POST request to the JIRA API.
        
        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON body
            
        Returns:
            JSON response as dictionary
        """
        client = await self._get_client()
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await client.post(url, json=json_data)
            response.raise_for_status()
            if response.status_code == 204:
                return {"success": True}
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": True,
                "status_code": e.response.status_code,
                "message": self._parse_error_response(e.response),
            }
        except httpx.RequestError as e:
            return {
                "error": True,
                "message": str(e),
            }
    
    async def put(self, endpoint: str, json_data: Optional[dict] = None) -> dict[str, Any]:
        """
        Make a PUT request to the JIRA API.
        
        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON body
            
        Returns:
            JSON response as dictionary
        """
        client = await self._get_client()
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await client.put(url, json=json_data)
            response.raise_for_status()
            if response.status_code == 204:
                return {"success": True}
            if not response.content:
                return {"success": True}
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": True,
                "status_code": e.response.status_code,
                "message": self._parse_error_response(e.response),
            }
        except httpx.RequestError as e:
            return {
                "error": True,
                "message": str(e),
            }
    
    def _parse_error_response(self, response: httpx.Response) -> str:
        """Parse error message from JIRA error response."""
        try:
            data = response.json()
            if "errorMessages" in data and data["errorMessages"]:
                return "; ".join(data["errorMessages"])
            if "errors" in data and data["errors"]:
                return "; ".join(f"{k}: {v}" for k, v in data["errors"].items())
            if "message" in data:
                return data["message"]
            return response.text
        except Exception:
            return response.text
