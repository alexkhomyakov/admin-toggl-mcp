"""
Utility functions for Toggl API operations.
"""

from datetime import datetime
from typing import Dict, Any


def parse_time_entry_response(entry_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and normalize a time entry response from the Toggl API.
    
    Args:
        entry_data: Raw time entry data from the API
        
    Returns:
        Normalized time entry data compatible with TimeEntry model
    """
    # Parse datetime strings
    if "start" in entry_data:
        entry_data["start"] = datetime.fromisoformat(entry_data["start"].replace("Z", "+00:00"))
    if "stop" in entry_data and entry_data["stop"]:
        entry_data["stop"] = datetime.fromisoformat(entry_data["stop"].replace("Z", "+00:00"))
    if "at" in entry_data and entry_data["at"]:
        entry_data["at"] = datetime.fromisoformat(entry_data["at"].replace("Z", "+00:00"))
    
    # Handle missing fields and None values
    if entry_data.get("tags") is None:
        entry_data["tags"] = []
    entry_data.setdefault("tags", [])
    entry_data.setdefault("billable", False)
    entry_data.setdefault("created_with", "Lazy Toggl MCP Server")
    entry_data.setdefault("duronly", False)
    
    # Map API field names to our model (but keep both for compatibility)
    if "wid" in entry_data:
        entry_data["workspace_id"] = entry_data["wid"]
    if "pid" in entry_data and entry_data["pid"]:
        entry_data["project_id"] = entry_data["pid"]
    if "tid" in entry_data and entry_data["tid"]:
        entry_data["task_id"] = entry_data["tid"]
    if "uid" in entry_data and entry_data["uid"]:
        entry_data["user_id"] = entry_data["uid"]
    
    return entry_data


def format_duration(duration_seconds: int) -> str:
    """
    Format duration in seconds to a human-readable string.
    
    Args:
        duration_seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2h 30m", "45m", "< 1m")
    """
    hours = duration_seconds // 3600
    minutes = (duration_seconds % 3600) // 60
    
    duration_str = ""
    if hours > 0:
        duration_str += f"{hours}h "
    if minutes > 0:
        duration_str += f"{minutes}m"
    if not duration_str:
        duration_str = "< 1m"
    
    return duration_str.strip()
