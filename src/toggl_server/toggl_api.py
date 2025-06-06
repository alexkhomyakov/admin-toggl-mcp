"""
Toggl API client for time tracking operations.
"""

import os
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import httpx
from toggl_server.models import TimeEntry, Workspace, User
from toggl_server.utils import parse_time_entry_response

class TogglAPIError(Exception):
    """Custom exception for Toggl API errors."""
    pass

class TogglAPI:
    """Client for interacting with the Toggl Track API."""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("TOGGL_API_TOKEN")
        if not self.api_token:
            raise TogglAPIError("TOGGL_API_TOKEN environment variable is required")
        
        self.base_url = "https://api.track.toggl.com/api/v9"
        self.auth = (self.api_token, "api_token")
        
        # Create HTTP client with proper configuration
        self.client = httpx.AsyncClient(
            auth=self.auth,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Lazy Toggl MCP Server/0.1.0"
            },
            timeout=30.0
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an authenticated request to the Toggl API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.client.request(method, url, **kwargs)
            
            # Handle rate limiting
            if response.status_code == 429:
                raise TogglAPIError("Rate limit exceeded. Please wait before making more requests.")
            
            # Handle authentication errors
            if response.status_code == 403:
                raise TogglAPIError("Authentication failed. Please check your API token.")
            
            # Handle not found
            if response.status_code == 404:
                raise TogglAPIError("Resource not found.")
            
            # Handle other client errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", f"HTTP {response.status_code}")
                except:
                    error_msg = f"HTTP {response.status_code}"
                raise TogglAPIError(f"API error: {error_msg}")
            
            response.raise_for_status()
            
            # Handle empty responses
            if not response.content:
                return {}
            
            return response.json()
            
        except httpx.RequestError as e:
            raise TogglAPIError(f"Network error: {str(e)}")
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get current user information."""
        return await self._request("GET", "/me")
    
    async def get_workspaces(self) -> List[Workspace]:
        """Get all workspaces for the current user."""
        data = await self._request("GET", "/workspaces")
        return [Workspace(**workspace) for workspace in data]
    
    async def get_current_time_entry(self) -> Optional[TimeEntry]:
        """Get the currently running time entry, if any."""
        data = await self._request("GET", "/me/time_entries/current")
        
        if not data:
            return None
        
        entry_data = parse_time_entry_response(data)
        return TimeEntry(**entry_data)
    
    async def start_time_entry(
        self,
        title: str,
        workspace_id: int,
        project_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> TimeEntry:
        """Start a new time entry."""
        now = datetime.now(timezone.utc)
        
        payload = {
            "description": title,
            "tags": tags or [],
            "billable": False,
            "workspace_id": workspace_id,
            "duration": -1,  # Running entry
            "start": now.isoformat(),
            "stop": None,
            "created_with": "Lazy Toggl MCP Server"
        }
        
        if project_id:
            payload["project_id"] = project_id
        
        data = await self._request("POST", f"/workspaces/{workspace_id}/time_entries", json=payload)
        
        entry_data = parse_time_entry_response(data)
        return TimeEntry(**entry_data)
    
    async def stop_time_entry(self, workspace_id: int, time_entry_id: int) -> TimeEntry:
        """Stop a running time entry."""
        data = await self._request("PATCH", f"/workspaces/{workspace_id}/time_entries/{time_entry_id}/stop")
        
        entry_data = parse_time_entry_response(data)
        return TimeEntry(**entry_data)
