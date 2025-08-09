"""
Extended data models for Toggl MCP server with admin-level reporting
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

# Original models (keep existing ones)
@dataclass
class TogglWorkspace:
    id: int
    name: str
    premium: bool
    admin: bool
    organization_id: Optional[int] = None
    business_ws: Optional[bool] = None
    role: Optional[str] = None
    suspended_at: Optional[str] = None
    server_deleted_at: Optional[str] = None
    rate_last_updated: Optional[str] = None
    default_hourly_rate: Optional[float] = None
    default_currency: str = "USD"
    only_admins_may_create_projects: bool = False
    only_admins_see_billable_rates: bool = False
    only_admins_see_team_dashboard: bool = False
    projects_billable_by_default: bool = True
    rounding: int = 0
    rounding_minutes: int = 0

@dataclass
class TogglTimeEntry:
    id: int
    description: str
    start: datetime
    duration: int
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    task_id: Optional[int] = None
    workspace_id: Optional[int] = None
    billable: bool = False
    tags: List[str] = field(default_factory=list)
    # Additional fields from Toggl API
    stop: Optional[datetime] = None
    created_with: Optional[str] = None
    duronly: Optional[bool] = None
    at: Optional[datetime] = None
    uid: Optional[int] = None
    wid: Optional[int] = None
    pid: Optional[int] = None
    tid: Optional[int] = None

# New admin-level models
@dataclass
class ProjectProfitability:
    """Project profitability analysis data"""
    project_id: int
    project_name: str
    client_name: Optional[str]
    total_hours: float
    billable_hours: float
    non_billable_hours: float
    revenue: Decimal
    labor_cost: Decimal
    profit: Decimal
    profit_margin: float  # percentage
    billable_rate: Optional[Decimal]
    currency: str
    active_users: int
    time_entries_count: int
    
    @property
    def utilization_rate(self) -> float:
        """Calculate billable utilization rate"""
        if self.total_hours == 0:
            return 0.0
        return (self.billable_hours / self.total_hours) * 100
    
    @property
    def hourly_profit(self) -> Decimal:
        """Calculate profit per hour"""
        if self.total_hours == 0:
            return Decimal('0')
        return self.profit / Decimal(str(self.total_hours))

@dataclass
class EmployeeProfitability:
    """Employee productivity and profitability metrics"""
    user_id: int
    username: str
    email: Optional[str]
    total_hours: float
    billable_hours: float
    non_billable_hours: float
    billable_rate: Optional[Decimal]
    labor_cost: Optional[Decimal]
    revenue_generated: Decimal
    projects_worked: int
    time_entries_count: int
    
    @property
    def utilization_rate(self) -> float:
        """Calculate billable utilization rate"""
        if self.total_hours == 0:
            return 0.0
        return (self.billable_hours / self.total_hours) * 100
    
    @property
    def average_hours_per_day(self) -> float:
        """Calculate average hours per working day (assuming 5 day work week)"""
        # This would need date range context to be accurate
        return self.total_hours / 30  # Rough monthly estimate
    
    @property
    def productivity_score(self) -> float:
        """Simple productivity score based on utilization and hours"""
        base_score = self.utilization_rate
        if self.total_hours > 160:  # Full-time equivalent per month
            base_score *= 1.1  # Bonus for high volume
        return min(base_score, 100.0)

@dataclass  
class ClientProfitability:
    """Client-level profitability analysis"""
    client_id: Optional[int]
    client_name: str
    total_hours: float
    billable_hours: float
    revenue: Decimal
    labor_cost: Decimal
    profit: Decimal
    profit_margin: float
    active_projects: int
    active_users: int
    currency: str

@dataclass
class OrganizationSummary:
    """High-level organization metrics and KPIs"""
    workspace_id: int
    workspace_name: str
    date_range: str
    currency: str
    
    # Time metrics
    total_hours: float
    billable_hours: float
    non_billable_hours: float
    
    # Financial metrics  
    total_revenue: Decimal
    total_labor_cost: Decimal
    total_profit: Decimal
    average_hourly_rate: Decimal
    
    # Organizational metrics
    active_projects: int
    active_clients: int
    active_users: int
    total_time_entries: int
    
    # Calculated properties
    @property
    def overall_utilization_rate(self) -> float:
        """Organization-wide billable utilization rate"""
        if self.total_hours == 0:
            return 0.0
        return (self.billable_hours / self.total_hours) * 100
    
    @property
    def overall_profit_margin(self) -> float:
        """Organization-wide profit margin percentage"""
        if self.total_revenue == 0:
            return 0.0
        return float((self.total_profit / self.total_revenue) * 100)
    
    @property
    def average_project_size(self) -> float:
        """Average hours per active project"""
        if self.active_projects == 0:
            return 0.0
        return self.total_hours / self.active_projects
    
    @property
    def average_user_hours(self) -> float:
        """Average hours per active user"""
        if self.active_users == 0:
            return 0.0
        return self.total_hours / self.active_users

@dataclass
class TeamProductivityMetrics:
    """Team-wide productivity analysis"""
    workspace_id: int
    team_size: int
    total_capacity_hours: float  # Expected working hours
    actual_hours: float
    billable_hours: float
    
    # Productivity metrics
    capacity_utilization: float  # actual vs expected hours
    billable_utilization: float  # billable vs actual hours
    overall_efficiency: float    # billable vs capacity hours
    
    # Performance indicators
    top_performers: List[EmployeeProfitability]
    underperformers: List[EmployeeProfitability]
    team_average_rate: Decimal
    
    @property
    def productivity_trend(self) -> str:
        """Simple productivity trend indicator"""
        if self.overall_efficiency >= 80:
            return "Excellent"
        elif self.overall_efficiency >= 60:
            return "Good"  
        elif self.overall_efficiency >= 40:
            return "Fair"
        else:
            return "Needs Improvement"

@dataclass
class AdminReportData:
    """Complete admin dashboard data structure"""
    organization_summary: OrganizationSummary
    project_profitability: List[ProjectProfitability]
    employee_profitability: List[EmployeeProfitability]
    client_profitability: List[ClientProfitability]
    team_metrics: TeamProductivityMetrics
    generated_at: datetime
    report_period: str
    
    def get_top_projects_by_profit(self, limit: int = 5) -> List[ProjectProfitability]:
        """Get top N most profitable projects"""
        return sorted(
            self.project_profitability, 
            key=lambda p: p.profit, 
            reverse=True
        )[:limit]
    
    def get_top_employees_by_utilization(self, limit: int = 5) -> List[EmployeeProfitability]:
        """Get top N employees by utilization rate"""
        return sorted(
            self.employee_profitability,
            key=lambda e: e.utilization_rate,
            reverse=True
        )[:limit]
    
    def get_underperforming_projects(self, profit_threshold: float = 20.0) -> List[ProjectProfitability]:
        """Get projects with profit margin below threshold"""
        return [
            p for p in self.project_profitability 
            if p.profit_margin < profit_threshold
        ]

@dataclass
class TimeTrackingInsights:
    """Advanced time tracking insights and patterns"""
    workspace_id: int
    date_range: str
    
    # Pattern analysis
    peak_productivity_hours: List[int]  # Hours of day (0-23)
    peak_productivity_days: List[str]   # Days of week
    average_session_length: float       # Minutes
    
    # Efficiency metrics
    context_switching_frequency: float  # Project switches per day
    deep_work_sessions: int            # Sessions > 2 hours
    fragmented_time_percentage: float   # Time in sessions < 30 min
    
    # Project distribution
    project_time_distribution: Dict[str, float]  # project_name: percentage
    most_productive_projects: List[str]
    
@dataclass
class BillingAnalysis:
    """Billing and revenue analysis"""
    workspace_id: int
    period: str
    
    # Billing metrics
    total_billable_amount: Decimal
    total_unbilled_amount: Decimal
    average_collection_time: float  # Days
    billing_efficiency: float       # Billed vs billable percentage
    
    # Rate analysis
    rate_utilization: Dict[str, float]  # rate_tier: utilization_percentage
    rate_gaps: List[str]               # Projects missing rates
    suggested_rate_adjustments: Dict[str, Decimal]  # project: suggested_rate
    
    # Client billing patterns
    client_payment_patterns: Dict[str, float]  # client: avg_payment_time
    high_value_clients: List[str]
    at_risk_clients: List[str]  # Clients with declining hours