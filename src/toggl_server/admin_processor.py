"""
Data processing functions for admin-level analytics and reporting
"""
from typing import Dict, List, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
import logging
from collections import defaultdict, Counter

from .models import (
    OrganizationSummary, ProjectProfitability, EmployeeProfitability,
    ClientProfitability, TeamProductivityMetrics, AdminReportData,
    TimeTrackingInsights, BillingAnalysis
)

logger = logging.getLogger(__name__)

class AdminDataProcessor:
    """Processes raw Toggl API data into admin-level insights"""
    
    def __init__(self, labor_cost_percentage: float = 0.6):
        """
        Initialize the admin data processor
        
        Args:
            labor_cost_percentage: Percentage of billing rate to use as labor cost (default 60%)
        """
        self.currency_precision = Decimal('0.01')
        self.labor_cost_percentage = labor_cost_percentage
    
    def _safe_decimal(self, value: Any) -> Decimal:
        """Safely convert value to Decimal"""
        if value is None:
            return Decimal('0')
        try:
            return Decimal(str(value)).quantize(self.currency_precision, rounding=ROUND_HALF_UP)
        except (TypeError, ValueError):
            return Decimal('0')
    
    def _milliseconds_to_hours(self, milliseconds: int) -> float:
        """Convert milliseconds to hours"""
        if not milliseconds:
            return 0.0
        return round(milliseconds / (1000 * 60 * 60), 2)
    
    def _calculate_labor_cost_from_v3_data(self, detailed_entries: List[Dict[str, Any]]) -> Decimal:
        """
        Calculate total labor cost from Reports API v3 detailed entries
        
        Args:
            detailed_entries: List of time entries from Reports API v3
            
        Returns:
            Total labor cost as Decimal
        """
        total_labor_cost = Decimal('0')
        
        for entry in detailed_entries:
            # Get billing rate in cents and convert to dollars
            hourly_rate_cents = entry.get('hourly_rate_in_cents', 0)
            hourly_rate_dollars = self._safe_decimal(hourly_rate_cents) / Decimal('100')
            
            # Calculate labor cost as percentage of billing rate
            labor_rate = hourly_rate_dollars * Decimal(str(self.labor_cost_percentage))
            
            # Get time from time_entries array
            time_entries = entry.get('time_entries', [])
            for time_entry in time_entries:
                seconds = time_entry.get('seconds', 0)
                hours = Decimal(str(seconds)) / Decimal('3600')
                
                # Calculate labor cost for this time entry
                entry_labor_cost = labor_rate * hours
                total_labor_cost += entry_labor_cost
        
        return total_labor_cost
    
    def _calculate_revenue_from_v3_data(self, detailed_entries: List[Dict[str, Any]]) -> Decimal:
        """
        Calculate total revenue from Reports API v3 detailed entries
        
        Args:
            detailed_entries: List of time entries from Reports API v3
            
        Returns:
            Total revenue as Decimal
        """
        total_revenue = Decimal('0')
        
        for entry in detailed_entries:
            # Get billable amount in cents and convert to dollars
            billable_amount_cents = entry.get('billable_amount_in_cents', 0)
            billable_amount_dollars = self._safe_decimal(billable_amount_cents) / Decimal('100')
            total_revenue += billable_amount_dollars
        
        return total_revenue
    
    def process_profitability_from_v3_data(
        self,
        detailed_entries: List[Dict[str, Any]],
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Process profitability data from Reports API v3 detailed entries
        
        Args:
            detailed_entries: List of time entries from Reports API v3
            currency: Currency code
            
        Returns:
            Dictionary with profitability metrics
        """
        total_revenue = self._calculate_revenue_from_v3_data(detailed_entries)
        total_labor_cost = self._calculate_labor_cost_from_v3_data(detailed_entries)
        total_profit = total_revenue - total_labor_cost
        
        # Calculate profit margin
        profit_margin = 0.0
        if total_revenue > 0:
            profit_margin = float((total_profit / total_revenue) * 100)
        
        # Calculate total hours
        total_hours = 0.0
        for entry in detailed_entries:
            time_entries = entry.get('time_entries', [])
            for time_entry in time_entries:
                seconds = time_entry.get('seconds', 0)
                hours = seconds / 3600
                total_hours += hours
        
        # Calculate average hourly rate
        average_hourly_rate = Decimal('0')
        if total_hours > 0:
            average_hourly_rate = total_revenue / Decimal(str(total_hours))
        
        return {
            'total_revenue': total_revenue,
            'total_labor_cost': total_labor_cost,
            'total_profit': total_profit,
            'profit_margin': profit_margin,
            'total_hours': total_hours,
            'average_hourly_rate': average_hourly_rate,
            'currency': currency,
            'labor_cost_percentage': self.labor_cost_percentage
        }
    
    def process_organization_summary(
        self, 
        summary_data: Dict[str, Any],
        insights_data: Dict[str, Any],
        workspace_info: Dict[str, Any],
        date_range: str
    ) -> OrganizationSummary:
        """Process raw API data into organization summary"""
        
        # Debug: Log raw data for troubleshooting
        logger.debug(f"Processing organization summary for date range: {date_range}")
        logger.debug(f"Summary data groups: {len(summary_data.get('groups', []))}")
        logger.debug(f"Insights data groups: {len(insights_data.get('groups', []))}")
        
        # Extract totals from summary data (Toggl Reports API v2 structure)
        total_milliseconds = summary_data.get('total_grand', 0)
        billable_milliseconds = summary_data.get('total_billable', 0)
        
        total_hours = self._milliseconds_to_hours(total_milliseconds)
        billable_hours = self._milliseconds_to_hours(billable_milliseconds)
        non_billable_hours = total_hours - billable_hours
        
        # Debug: Log time values for troubleshooting
        logger.debug(f"Organization summary time values:")
        logger.debug(f"  Total milliseconds: {total_milliseconds}")
        logger.debug(f"  Billable milliseconds: {billable_milliseconds}")
        logger.debug(f"  Total hours: {total_hours}")
        logger.debug(f"  Billable hours: {billable_hours}")
        
        # Validate hours - flag unrealistic values
        if total_hours > 168:  # More than 7 days worth of hours
            logger.warning(f"Unrealistic total hours detected in organization summary: {total_hours}h")
            # Cap at reasonable maximum (e.g., 80 hours per week)
            total_hours = min(total_hours, 80.0)
            billable_hours = min(billable_hours, total_hours)
            non_billable_hours = total_hours - billable_hours
        
        # Extract financial data from insights (Toggl Reports API v2 structure)
        total_currencies = insights_data.get('total_currencies', [])
        total_revenue = Decimal('0')
        for curr in total_currencies:
            if curr.get('currency') == 'USD':
                total_revenue = self._safe_decimal(curr.get('amount', 0))
                break
        
        # Calculate total labor cost from all time entries
        total_labor_cost = Decimal('0')
        data = insights_data.get('data', [])
        for item in data:
            items = item.get('items', [])
            for time_entry in items:
                entry_time_ms = time_entry.get('time', 0)
                entry_rate = self._safe_decimal(time_entry.get('rate', 0))
                entry_hours = self._milliseconds_to_hours(entry_time_ms)
                entry_cost = entry_hours * entry_rate
                total_labor_cost += entry_cost
        
        total_profit = total_revenue - total_labor_cost
        
        # Calculate average hourly rate
        average_hourly_rate = Decimal('0')
        if billable_hours > 0:
            average_hourly_rate = total_revenue / Decimal(str(billable_hours))
        
        # Count active entities from data structure (Toggl Reports API v2)
        data = summary_data.get('data', [])
        active_projects = len([d for d in data if d.get('id') and d.get('title', {}).get('project')])
        
        # For now, we can't determine active users and clients from projects data
        # These would need to be calculated from users and clients data respectively
        active_users = 0  # Would need users data to calculate this
        active_clients = 0  # Would need clients data to calculate this
        
        # Count time entries
        total_time_entries = sum(len(d.get('items', [])) for d in data)
        
        return OrganizationSummary(
            workspace_id=workspace_info.get('id', 0),
            workspace_name=workspace_info.get('name', 'Unknown'),
            date_range=date_range,
            currency=workspace_info.get('default_currency', 'USD'),
            total_hours=total_hours,
            billable_hours=billable_hours,
            non_billable_hours=non_billable_hours,
            total_revenue=total_revenue,
            total_labor_cost=total_labor_cost,
            total_profit=total_profit,
            average_hourly_rate=average_hourly_rate,
            active_projects=active_projects,
            active_clients=active_clients,
            active_users=active_users,
            total_time_entries=total_time_entries
        )
    
    def process_project_profitability(
        self, 
        insights_data: Dict[str, Any],
        currency: str = "USD"
    ) -> List[ProjectProfitability]:
        """Process insights data into project profitability objects"""
        
        projects = []
        data = insights_data.get('data', [])
        
        for item in data:
            if not item.get('id'):  # Skip ungrouped entries
                continue
            
            try:
                total_ms = item.get('time', 0)
                # For now, assume all time is billable (would need additional data for billable vs non-billable)
                billable_ms = item.get('time', 0)
                
                total_hours = self._milliseconds_to_hours(total_ms)
                billable_hours = self._milliseconds_to_hours(billable_ms)
                non_billable_hours = total_hours - billable_hours
                
                # Validate hours - flag unrealistic values
                if total_hours > 168:  # More than 7 days worth of hours
                    logger.warning(f"Unrealistic total hours detected for project {item.get('id')}: {total_hours}h")
                    # Cap at reasonable maximum (e.g., 80 hours per week)
                    total_hours = min(total_hours, 80.0)
                    billable_hours = min(billable_hours, total_hours)
                    non_billable_hours = total_hours - billable_hours
                
                # Extract revenue from total_currencies
                revenue = Decimal('0')
                total_currencies = item.get('total_currencies', [])
                for curr in total_currencies:
                    if curr.get('currency') == 'USD':
                        revenue = self._safe_decimal(curr.get('amount', 0))
                        break
                
                # Calculate labor cost from individual time entries
                labor_cost = Decimal('0')
                items = item.get('items', [])
                for time_entry in items:
                    entry_time_ms = time_entry.get('time', 0)
                    entry_rate = self._safe_decimal(time_entry.get('rate', 0))
                    entry_hours = self._milliseconds_to_hours(entry_time_ms)
                    entry_cost = entry_hours * entry_rate
                    labor_cost += entry_cost
                
                profit = revenue - labor_cost
                
                # Calculate profit margin
                profit_margin = 0.0
                if revenue > 0:
                    profit_margin = float((profit / revenue) * 100)
                
                # Calculate billable rate
                billable_rate = None
                if billable_hours > 0:
                    billable_rate = revenue / Decimal(str(billable_hours))
                
                # Extract project name with multiple fallbacks
                title_info = item.get('title', {})
                project_name = 'Unknown Project'
                
                # Debug: Log the structure to understand how project names are stored
                logger.debug(f"Project {item.get('id')} title structure: {title_info}")
                logger.debug(f"Project {item.get('id')} available keys: {list(item.keys())}")
                
                if isinstance(title_info, dict):
                    project_name = title_info.get('project') or title_info.get('name') or 'Unknown Project'
                elif isinstance(title_info, str):
                    project_name = title_info
                
                # Also try other common fields
                if project_name == 'Unknown Project':
                    project_name = item.get('project', {}).get('name', 'Unknown Project') if isinstance(item.get('project'), dict) else item.get('project', 'Unknown Project')
                
                # Extract client name with fallbacks
                client_name = None
                if isinstance(title_info, dict):
                    client_name = title_info.get('client')
                if not client_name and 'client' in item:
                    client_info = item.get('client', {})
                    if isinstance(client_info, dict):
                        client_name = client_info.get('name')
                    elif isinstance(client_info, str):
                        client_name = client_info
                
                project = ProjectProfitability(
                    project_id=item.get('id', 0),
                    project_name=project_name,
                    client_name=client_name,
                    total_hours=total_hours,
                    billable_hours=billable_hours,
                    non_billable_hours=non_billable_hours,
                    revenue=revenue,
                    labor_cost=labor_cost,
                    profit=profit,
                    profit_margin=profit_margin,
                    billable_rate=billable_rate,
                    currency=currency,
                    active_users=1,  # Would need additional data to determine actual user count
                    time_entries_count=len(item.get('items', []))
                )
                
                projects.append(project)
                
            except Exception as e:
                logger.error(f"Failed to process project {item.get('id', 'unknown')}: {str(e)}")
                logger.error(f"Item data: {item}")
                # Skip this project and continue with the next one
                continue
        
        # Filter out any non-ProjectProfitability objects that might have slipped through
        valid_projects = []
        for p in projects:
            # Check for all required attributes that will be used later
            required_attrs = ['total_hours', 'profit', 'revenue', 'profit_margin', 'project_name', 
                            'client_name', 'billable_hours', 'utilization_rate', 'billable_rate', 
                            'active_users', 'time_entries_count']
            
            if all(hasattr(p, attr) for attr in required_attrs):
                valid_projects.append(p)
            else:
                logger.warning(f"Filtering out invalid project object: {type(p)}")
                missing_attrs = [attr for attr in required_attrs if not hasattr(p, attr)]
                logger.warning(f"Missing attributes: {missing_attrs}")
        
        if not valid_projects:
            logger.warning("No valid project objects found after filtering")
            return []
        
        logger.info(f"Returning {len(valid_projects)} valid ProjectProfitability objects")
        return sorted(valid_projects, key=lambda p: float(p.profit or 0), reverse=True)
    
    def process_employee_profitability(
        self,
        user_summary_data: Dict[str, Any],
        user_insights_data: Dict[str, Any]
    ) -> List[EmployeeProfitability]:
        """Process user data into employee profitability metrics"""
        
        # Debug: Log raw data for troubleshooting
        logger.debug(f"Processing employee profitability data:")
        logger.debug(f"User summary data items: {len(user_summary_data.get('data', []))}")
        logger.debug(f"User insights data items: {len(user_insights_data.get('data', []))}")
        
        employees = []
        
        # Create lookup for insights data by user
        insights_by_user = {}
        for item in user_insights_data.get('data', []):
            user_id = item.get('id')
            if user_id:
                insights_by_user[user_id] = item
        
        # Process each user from summary data
        for item in user_summary_data.get('data', []):
            user_id = item.get('id')
            if not user_id:
                continue
                
            total_ms = item.get('time', 0)
            # For now, assume all time is billable (would need additional data for billable vs non-billable)
            billable_ms = item.get('time', 0)
            
            total_hours = self._milliseconds_to_hours(total_ms)
            billable_hours = self._milliseconds_to_hours(billable_ms)
            non_billable_hours = total_hours - billable_hours
            
            # Debug: Log time values for troubleshooting
            logger.debug(f"User {user_id} time values:")
            logger.debug(f"  Total milliseconds: {total_ms}")
            logger.debug(f"  Billable milliseconds: {billable_ms}")
            logger.debug(f"  Total hours: {total_hours}")
            logger.debug(f"  Billable hours: {billable_hours}")
            
            # Validate hours - flag unrealistic values
            if total_hours > 168:  # More than 7 days worth of hours
                logger.warning(f"Unrealistic total hours detected for user {user_id}: {total_hours}h")
                # Cap at reasonable maximum (e.g., 80 hours per week)
                total_hours = min(total_hours, 80.0)
                billable_hours = min(billable_hours, total_hours)
                non_billable_hours = total_hours - billable_hours
            
            # Get financial data from insights
            insights = insights_by_user.get(user_id, {})
            
            # Extract revenue from total_currencies
            revenue = Decimal('0')
            total_currencies = insights.get('total_currencies', [])
            for curr in total_currencies:
                if curr.get('currency') == 'USD':
                    revenue = self._safe_decimal(curr.get('amount', 0))
                    break
            
            # Calculate labor cost from individual time entries
            labor_cost = Decimal('0')
            items = item.get('items', [])
            for time_entry in items:
                entry_time_ms = time_entry.get('time', 0)
                entry_rate = self._safe_decimal(time_entry.get('rate', 0))
                entry_hours = self._milliseconds_to_hours(entry_time_ms)
                entry_cost = entry_hours * entry_rate
                labor_cost += entry_cost
            
            # Calculate billable rate
            billable_rate = None
            if billable_hours > 0:
                billable_rate = revenue / Decimal(str(billable_hours))
            
            employee = EmployeeProfitability(
                user_id=user_id,
                username=item.get('title', {}).get('user', 'Unknown User'),
                email=None,  # Would need additional data for email
                total_hours=total_hours,
                billable_hours=billable_hours,
                non_billable_hours=non_billable_hours,
                billable_rate=billable_rate,
                labor_cost=labor_cost,
                revenue_generated=revenue,
                projects_worked=1,  # Would need additional data to determine actual project count
                time_entries_count=len(item.get('items', []))
            )
            
            employees.append(employee)
        
        return sorted(employees, key=lambda e: e.utilization_rate, reverse=True)
    
    def process_client_profitability(
        self,
        client_summary_data: Dict[str, Any],
        client_insights_data: Dict[str, Any],
        currency: str = "USD"
    ) -> List[ClientProfitability]:
        """Process client data into profitability metrics"""
        
        clients = []
        
        # Create lookup for insights data by client
        insights_by_client = {}
        for item in client_insights_data.get('data', []):
            client_id = item.get('id')
            if client_id:
                insights_by_client[client_id] = item
        
        # Process each client
        for item in client_summary_data.get('data', []):
            client_id = item.get('id')
            if not client_id:
                continue
                
            client_name = item.get('title', {}).get('client', 'No Client')
            
            total_ms = item.get('time', 0)
            # For now, assume all time is billable (would need additional data for billable vs non-billable)
            billable_ms = item.get('time', 0)
            
            total_hours = self._milliseconds_to_hours(total_ms)
            billable_hours = self._milliseconds_to_hours(billable_ms)
            
            # Get financial data
            insights = insights_by_client.get(client_id, {})
            
            # Extract revenue from total_currencies
            revenue = Decimal('0')
            total_currencies = insights.get('total_currencies', [])
            for curr in total_currencies:
                if curr.get('currency') == 'USD':
                    revenue = self._safe_decimal(curr.get('amount', 0))
                    break
            
            # Calculate labor cost from individual time entries
            labor_cost = Decimal('0')
            items = insights.get('items', [])
            for time_entry in items:
                entry_time_ms = time_entry.get('time', 0)
                entry_rate = self._safe_decimal(time_entry.get('rate', 0))
                entry_hours = self._milliseconds_to_hours(entry_time_ms)
                entry_cost = entry_hours * entry_rate
                labor_cost += entry_cost
            
            profit = revenue - labor_cost
            
            profit_margin = 0.0
            if revenue > 0:
                profit_margin = float((profit / revenue) * 100)
            
            client = ClientProfitability(
                client_id=client_id,
                client_name=client_name,
                total_hours=total_hours,
                billable_hours=billable_hours,
                revenue=revenue,
                labor_cost=labor_cost,
                profit=profit,
                profit_margin=profit_margin,
                active_projects=1,  # Would need additional data to determine actual project count
                active_users=1,  # Would need additional data to determine actual user count
                currency=currency
            )
            
            clients.append(client)
        
        return sorted(clients, key=lambda c: c.profit, reverse=True)
    
    def calculate_team_metrics(
        self,
        employees: List[EmployeeProfitability],
        workspace_id: int,
        expected_hours_per_person: float = 160.0  # Monthly full-time
    ) -> TeamProductivityMetrics:
        """Calculate team-wide productivity metrics"""
        
        team_size = len(employees)
        total_capacity = team_size * expected_hours_per_person
        
        actual_hours = sum(e.total_hours for e in employees)
        billable_hours = sum(e.billable_hours for e in employees)
        
        # Calculate utilization rates
        capacity_utilization = (actual_hours / total_capacity * 100) if total_capacity > 0 else 0
        billable_utilization = (billable_hours / actual_hours * 100) if actual_hours > 0 else 0
        overall_efficiency = (billable_hours / total_capacity * 100) if total_capacity > 0 else 0
        
        # Identify top and underperformers
        top_performers = sorted(employees, key=lambda e: e.utilization_rate, reverse=True)[:5]
        underperformers = [e for e in employees if e.utilization_rate < 60.0]
        
        # Calculate team average rate
        total_revenue = sum(e.revenue_generated for e in employees)
        team_average_rate = Decimal('0')
        if billable_hours > 0:
            team_average_rate = total_revenue / Decimal(str(billable_hours))
        
        return TeamProductivityMetrics(
            workspace_id=workspace_id,
            team_size=team_size,
            total_capacity_hours=total_capacity,
            actual_hours=actual_hours,
            billable_hours=billable_hours,
            capacity_utilization=capacity_utilization,
            billable_utilization=billable_utilization,
            overall_efficiency=overall_efficiency,
            top_performers=top_performers,
            underperformers=underperformers,
            team_average_rate=team_average_rate
        )
    
    def process_time_tracking_insights(
        self,
        detailed_entries: List[Dict[str, Any]],
        workspace_id: int,
        date_range: str
    ) -> TimeTrackingInsights:
        """Analyze detailed time entries for productivity patterns"""
        
        if not detailed_entries:
            return TimeTrackingInsights(
                workspace_id=workspace_id,
                date_range=date_range,
                peak_productivity_hours=[],
                peak_productivity_days=[],
                average_session_length=0.0,
                context_switching_frequency=0.0,
                deep_work_sessions=0,
                fragmented_time_percentage=0.0,
                project_time_distribution={},
                most_productive_projects=[]
            )
        
        # Analyze peak productivity hours
        hour_distribution = Counter()
        day_distribution = Counter()
        session_lengths = []
        project_hours = defaultdict(float)
        daily_project_switches = defaultdict(int)
        
        for entry in detailed_entries:
            # Parse start time
            start_time = datetime.fromisoformat(entry.get('start', '').replace('Z', '+00:00'))
            duration_ms = entry.get('dur', 0)
            duration_hours = self._milliseconds_to_hours(duration_ms)
            
            # Track peak hours and days
            hour_distribution[start_time.hour] += duration_hours
            day_distribution[start_time.strftime('%A')] += duration_hours
            
            # Session length analysis
            session_length_minutes = duration_ms / (1000 * 60)
            session_lengths.append(session_length_minutes)
            
            # Project distribution
            project_name = entry.get('project', 'No Project')
            project_hours[project_name] += duration_hours
            
            # Context switching (project changes per day)
            day_key = start_time.date()
            # This is simplified - would need proper session grouping for accuracy
            daily_project_switches[day_key] += 1
        
        # Calculate insights
        peak_hours = [hour for hour, _ in hour_distribution.most_common(8)]
        peak_days = [day for day, _ in day_distribution.most_common(3)]
        
        avg_session_length = sum(session_lengths) / len(session_lengths) if session_lengths else 0
        
        deep_work_sessions = len([s for s in session_lengths if s >= 120])  # 2+ hours
        fragmented_sessions = len([s for s in session_lengths if s < 30])   # <30 min
        fragmented_percentage = (fragmented_sessions / len(session_lengths) * 100) if session_lengths else 0
        
        # Project time distribution
        total_project_hours = sum(project_hours.values())
        project_distribution = {
            project: round((hours / total_project_hours * 100), 1)
            for project, hours in project_hours.items()
        } if total_project_hours > 0 else {}
        
        most_productive_projects = [
            project for project, _ in 
            sorted(project_hours.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Context switching frequency (switches per day)
        avg_switches_per_day = (
            sum(daily_project_switches.values()) / len(daily_project_switches)
            if daily_project_switches else 0
        )
        
        return TimeTrackingInsights(
            workspace_id=workspace_id,
            date_range=date_range,
            peak_productivity_hours=peak_hours,
            peak_productivity_days=peak_days,
            average_session_length=avg_session_length,
            context_switching_frequency=avg_switches_per_day,
            deep_work_sessions=deep_work_sessions,
            fragmented_time_percentage=fragmented_percentage,
            project_time_distribution=project_distribution,
            most_productive_projects=most_productive_projects
        )
    
    def process_productivity_insights(
        self,
        insights_data: Dict[str, Any],
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """Process productivity insights from time tracking data"""
        
        # Extract key metrics from insights data
        total_hours = 0
        billable_hours = 0
        non_billable_hours = 0
        total_revenue = Decimal('0')
        
        # Process groups data if available
        for group in insights_data.get('groups', []):
            tracked_ms = group.get('tracked', 0)
            billable_ms = group.get('billable', 0)
            revenue = self._safe_decimal(group.get('revenue', 0))
            
            group_hours = self._milliseconds_to_hours(tracked_ms)
            group_billable_hours = self._milliseconds_to_hours(billable_ms)
            group_non_billable_hours = group_hours - group_billable_hours
            
            total_hours += group_hours
            billable_hours += group_billable_hours
            non_billable_hours += group_non_billable_hours
            total_revenue += revenue
        
        # Calculate productivity metrics
        utilization_rate = (billable_hours / total_hours * 100) if total_hours > 0 else 0
        efficiency_rate = (billable_hours / (total_hours + non_billable_hours) * 100) if (total_hours + non_billable_hours) > 0 else 0
        
        # Calculate average hourly rate
        avg_hourly_rate = float(total_revenue / Decimal(str(billable_hours))) if billable_hours > 0 else 0
        
        return {
            'total_hours': total_hours,
            'billable_hours': billable_hours,
            'non_billable_hours': non_billable_hours,
            'total_revenue': float(total_revenue),
            'utilization_rate': utilization_rate,
            'efficiency_rate': efficiency_rate,
            'avg_hourly_rate': avg_hourly_rate,
            'currency': currency
        }
    
    def process_productivity_insights_from_summary(
        self,
        summary_data: Dict[str, Any],
        insights_data: Dict[str, Any],
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """Process productivity insights using the same data source as organization dashboard"""
        
        # Extract totals from summary data (same as organization dashboard)
        total_milliseconds = summary_data.get('total_grand', 0)
        billable_milliseconds = summary_data.get('total_billable', 0)
        
        total_hours = self._milliseconds_to_hours(total_milliseconds)
        billable_hours = self._milliseconds_to_hours(billable_milliseconds)
        non_billable_hours = total_hours - billable_hours
        
        # Extract financial data from insights (same as organization dashboard)
        total_currencies = insights_data.get('total_currencies', [])
        total_revenue = Decimal('0')
        for curr in total_currencies:
            if curr.get('currency') == 'USD':
                total_revenue = self._safe_decimal(curr.get('amount', 0))
                break
        
        # Calculate productivity metrics
        utilization_rate = (billable_hours / total_hours * 100) if total_hours > 0 else 0
        efficiency_rate = (billable_hours / (total_hours + non_billable_hours) * 100) if (total_hours + non_billable_hours) > 0 else 0
        
        # Calculate average hourly rate
        avg_hourly_rate = float(total_revenue / Decimal(str(billable_hours))) if billable_hours > 0 else 0
        
        return {
            'total_hours': total_hours,
            'billable_hours': billable_hours,
            'non_billable_hours': non_billable_hours,
            'total_revenue': float(total_revenue),
            'utilization_rate': utilization_rate,
            'efficiency_rate': efficiency_rate,
            'avg_hourly_rate': avg_hourly_rate,
            'currency': currency
        }
    
    def process_financial_summary(
        self,
        summary_data: Dict[str, Any],
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """Process financial summary from summary data"""
        
        # Extract totals from summary data (Toggl Reports API v2 structure)
        total_grand = summary_data.get('total_grand', 0)
        total_billable = summary_data.get('total_billable', 0)
        total_currencies = summary_data.get('total_currencies', [])
        
        # Convert milliseconds to hours
        total_hours = self._milliseconds_to_hours(total_grand)
        billable_hours = self._milliseconds_to_hours(total_billable)
        non_billable_hours = total_hours - billable_hours
        
        # Calculate revenue from currencies
        total_revenue = Decimal('0')
        for curr in total_currencies:
            if curr.get('currency') == currency:
                total_revenue = self._safe_decimal(curr.get('amount', 0))
                break
        
        # Calculate utilization rates
        utilization_rate = (billable_hours / total_hours * 100) if total_hours > 0 else 0
        
        return {
            'total_hours': total_hours,
            'billable_hours': billable_hours,
            'non_billable_hours': non_billable_hours,
            'total_revenue': float(total_revenue),
            'utilization_rate': utilization_rate,
            'currency': currency
        }
    
    def process_billing_analysis(
        self,
        projects: List[ProjectProfitability],
        clients: List[ClientProfitability],
        period: str,
        workspace_id: int
    ) -> BillingAnalysis:
        """Analyze billing efficiency and revenue patterns"""
        
        total_billable = sum(p.revenue for p in projects)
        
        # Calculate billing efficiency (simplified - would need actual billing data)
        billing_efficiency = 85.0  # Placeholder - would calculate from actual vs billed
        
        # Identify rate gaps (projects without proper rates)
        rate_gaps = [
            p.project_name for p in projects 
            if not p.billable_rate or p.billable_rate <= Decimal('10')
        ]
        
        # Rate utilization analysis
        rate_tiers = {
            'low': [p for p in projects if p.billable_rate and p.billable_rate < Decimal('50')],
            'medium': [p for p in projects if p.billable_rate and Decimal('50') <= p.billable_rate < Decimal('100')],
            'high': [p for p in projects if p.billable_rate and p.billable_rate >= Decimal('100')]
        }
        
        total_hours = sum(p.total_hours for p in projects)
        rate_utilization = {}
        for tier, tier_projects in rate_tiers.items():
            tier_hours = sum(p.total_hours for p in tier_projects)
            rate_utilization[tier] = (tier_hours / total_hours * 100) if total_hours > 0 else 0
        
        # Suggest rate adjustments (simplified logic)
        suggested_adjustments = {}
        for project in projects:
            if project.profit_margin < 20 and project.billable_rate:
                suggested_rate = project.billable_rate * Decimal('1.15')  # 15% increase
                suggested_adjustments[project.project_name] = suggested_rate
        
        # Client analysis
        high_value_clients = [
            c.client_name for c in clients 
            if c.revenue > Decimal('10000')  # Threshold for high value
        ]
        
        at_risk_clients = [
            c.client_name for c in clients
            if c.total_hours < 20 and c.profit_margin < 30  # Low hours and margin
        ]
        
        return BillingAnalysis(
            workspace_id=workspace_id,
            period=period,
            total_billable_amount=total_billable,
            total_unbilled_amount=Decimal('0'),  # Would need billing system integration
            average_collection_time=30.0,  # Placeholder
            billing_efficiency=billing_efficiency,
            rate_utilization=rate_utilization,
            rate_gaps=rate_gaps,
            suggested_rate_adjustments=suggested_adjustments,
            client_payment_patterns={},  # Would need payment history
            high_value_clients=high_value_clients,
            at_risk_clients=at_risk_clients
        )
    
    def create_admin_report(
        self,
        workspace_info: Dict[str, Any],
        summary_data: Dict[str, Any],
        insights_data: Dict[str, Any],
        user_summary_data: Dict[str, Any],
        user_insights_data: Dict[str, Any],
        client_summary_data: Dict[str, Any],
        client_insights_data: Dict[str, Any],
        detailed_entries: List[Dict[str, Any]],
        date_range: str
    ) -> AdminReportData:
        """Create comprehensive admin report from all data sources"""
        
        # Process all components
        org_summary = self.process_organization_summary(
            summary_data, insights_data, workspace_info, date_range
        )
        
        project_profitability = self.process_project_profitability(
            insights_data, org_summary.currency
        )
        
        employee_profitability = self.process_employee_profitability(
            user_summary_data, user_insights_data
        )
        
        client_profitability = self.process_client_profitability(
            client_summary_data, client_insights_data, org_summary.currency
        )
        
        team_metrics = self.calculate_team_metrics(
            employee_profitability, workspace_info.get('id', 0)
        )
        
        return AdminReportData(
            organization_summary=org_summary,
            project_profitability=project_profitability,
            employee_profitability=employee_profitability,
            client_profitability=client_profitability,
            team_metrics=team_metrics,
            generated_at=datetime.now(),
            report_period=date_range
        )