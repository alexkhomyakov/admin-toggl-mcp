"""
Toggl Reports API v3 Client for admin-level reporting functionality
"""
import aiohttp
import ssl
import certifi
import base64
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class TogglReportsAPI:
    """Client for Toggl Reports API v3 - provides admin-level analytics and reporting"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.track.toggl.com/reports/api/v2"
        self.reports_v3_url = "https://api.track.toggl.com/reports/api/v3"
        self.api_v9_url = "https://api.track.toggl.com/api/v9"
        self.auth_header = self._get_auth_header()
        self.session = None
        
        # Create SSL context with proper certificate verification
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.ssl_context.check_hostname = True
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        
    def _get_auth_header(self) -> str:
        """Generate Basic Auth header for API requests"""
        credentials = f"{self.api_token}:api_token"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    async def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated request with rate limiting and error handling"""
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }
        
        try:
            if not self.session:
                connector = aiohttp.TCPConnector(ssl=self.ssl_context)
                self.session = aiohttp.ClientSession(connector=connector)
                
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 429:  # Rate limited
                    logger.warning("Rate limited, waiting 60 seconds...")
                    await asyncio.sleep(60)
                    return await self._make_request(url, params)
                
                if response.status == 402:  # Payment required
                    raise Exception("Feature requires Premium/Enterprise plan")
                
                if response.status == 403:  # Forbidden
                    raise Exception("Insufficient permissions - admin access required")
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            raise Exception(f"Reports API request failed: {str(e)}")
    
    async def get_summary_report(
        self, 
        workspace_id: int,
        start_date: str,
        end_date: str,
        grouping: Optional[str] = "projects",
        sub_grouping: Optional[str] = None,
        include_time_entry_ids: bool = False
    ) -> Dict[str, Any]:
        """
        Get aggregated summary data for workspace
        
        Args:
            workspace_id: Target workspace ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format  
            grouping: Group by 'projects', 'clients', 'users', 'tasks', 'tags'
            sub_grouping: Optional secondary grouping
            include_time_entry_ids: Include time entry IDs in response
        """
        url = f"{self.base_url}/summary"
        params = {
            "workspace_id": workspace_id,
            "since": start_date,
            "until": end_date,
            "grouping": grouping
        }
        
        if sub_grouping:
            params["sub_grouping"] = sub_grouping
        if include_time_entry_ids:
            params["include_time_entry_ids"] = "true"
            
        return await self._make_request(url, params)
    
    async def get_insights_profitability(
        self, 
        workspace_id: int,
        start_date: str,
        end_date: str,
        grouping: str = "projects"
    ) -> Dict[str, Any]:
        """
        Get project and employee profitability insights
        
        Args:
            workspace_id: Target workspace ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            grouping: Group by 'projects' or 'users'
        """
        # Use the summary endpoint since v2 API doesn't have separate profitability endpoint
        url = f"{self.base_url}/summary"
        params = {
            "workspace_id": workspace_id,
            "since": start_date,
            "until": end_date,
            "grouping": grouping
        }
        
        return await self._make_request(url, params)
    
    async def get_detailed_report_v3(
        self, 
        workspace_id: int,
        start_date: str,
        end_date: str,
        hide_amounts: bool = False
    ) -> Dict[str, Any]:
        """
        Get detailed time entries with cost data using Reports API v3
        
        Args:
            workspace_id: Target workspace ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            hide_amounts: Whether to hide monetary amounts (costs)
        """
        url = f"{self.reports_v3_url}/workspace/{workspace_id}/search/time_entries"
        
        # This is a POST request with JSON body
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }
        
        body = {
            "start_date": start_date,
            "end_date": end_date,
            "hide_amounts": hide_amounts
        }
        
        try:
            if not self.session:
                connector = aiohttp.TCPConnector(ssl=self.ssl_context)
                self.session = aiohttp.ClientSession(connector=connector)
                
            async with self.session.post(url, json=body, headers=headers) as response:
                if response.status == 429:  # Rate limited
                    logger.warning("Rate limited, waiting 60 seconds...")
                    await asyncio.sleep(60)
                    return await self.get_detailed_report_v3(workspace_id, start_date, end_date, hide_amounts)
                
                if response.status == 402:  # Payment required
                    raise Exception("Feature requires Premium/Enterprise plan")
                
                if response.status == 403:  # Forbidden
                    raise Exception("Insufficient permissions - admin access required")
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            raise Exception(f"Reports API v3 request failed: {str(e)}")
    
    async def get_workspace_rates(
        self,
        workspace_id: int,
        level: str = "workspace",
        level_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get labor cost rates from Workspace Rates API
        
        Args:
            workspace_id: Target workspace ID
            level: Rate level - 'workspace', 'project', 'task', 'user'
            level_id: ID of the specific level (required for project/task/user levels)
        """
        if level != "workspace" and level_id is None:
            raise ValueError(f"level_id is required for {level} level rates")
        
        if level == "workspace":
            url = f"{self.api_v9_url}/workspaces/{workspace_id}/rates"
        else:
            url = f"{self.api_v9_url}/workspaces/{workspace_id}/rates/{level}/{level_id}"
        
        return await self._make_request(url, {})
    
    async def get_detailed_report(
        self, 
        workspace_id: int,
        start_date: str,
        end_date: str,
        first_row_number: Optional[int] = None,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get detailed time entries with pagination
        
        Args:
            workspace_id: Target workspace ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            first_row_number: Row number for pagination
            page_size: Number of entries per page (max 50)
        """
        url = f"{self.base_url}/detailed"
        params = {
            "workspace_id": workspace_id,
            "since": start_date,
            "until": end_date,
            "page_size": min(page_size, 50)
        }
        
        if first_row_number:
            params["first_row_number"] = first_row_number
            
        return await self._make_request(url, params)
    
    async def get_weekly_report(
        self,
        workspace_id: int,
        start_date: str,
        end_date: str,
        grouping: str = "projects"
    ) -> Dict[str, Any]:
        """
        Get weekly aggregated report
        
        Args:
            workspace_id: Target workspace ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            grouping: Group by 'projects', 'users', 'clients'
        """
        url = f"{self.base_url}/weekly"
        params = {
            "workspace_id": workspace_id,
            "since": start_date,
            "until": end_date,
            "grouping": grouping
        }
        
        return await self._make_request(url, params)
    
    async def get_all_detailed_entries(
        self,
        workspace_id: int, 
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get all detailed time entries by handling pagination automatically
        
        Args:
            workspace_id: Target workspace ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of all time entries across all pages
        """
        all_entries = []
        next_row = None
        
        while True:
            response = await self.get_detailed_report(
                workspace_id, start_date, end_date, next_row
            )
            
            if "data" in response:
                all_entries.extend(response["data"])
            
            # Check if there are more pages
            if "next_row_number" in response:
                next_row = response["next_row_number"]
                # Add delay to respect rate limits
                await asyncio.sleep(1.1)  # Slightly over 1 second for safety
            else:
                break
                
        return all_entries
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()