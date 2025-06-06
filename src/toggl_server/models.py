"""
Data models for Toggl API responses.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TimeEntry(BaseModel):
    """Represents a Toggl time entry."""
    id: int
    workspace_id: int
    project_id: Optional[int] = None
    description: str
    start: datetime
    stop: Optional[datetime] = None
    duration: int  # Duration in seconds, negative for running entries
    billable: bool = False
    tags: List[str] = Field(default_factory=list)
    created_with: str = "Lazy Toggl MCP Server"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Workspace(BaseModel):
    """Represents a Toggl workspace."""
    id: int
    name: str
    premium: bool = False
    admin: bool = False
    default_hourly_rate: Optional[float] = None
    default_currency: str = "USD"
    only_admins_may_create_projects: bool = False
    only_admins_see_billable_rates: bool = False
    only_admins_see_team_dashboard: bool = False
    projects_billable_by_default: bool = True
    rounding: int = 0
    rounding_minutes: int = 0


class User(BaseModel):
    """Represents a Toggl user."""
    id: int
    email: str
    fullname: str
    timezone: str
    default_workspace_id: int
    beginning_of_week: int = 0  # 0 = Sunday, 1 = Monday
    language: str = "en_US"
    image_url: Optional[str] = None
