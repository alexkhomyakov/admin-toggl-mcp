"""
Extended Toggl MCP server with admin-level reporting capabilities
"""
import asyncio
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from mcp.server import Server
from mcp.types import TextContent, Tool
import mcp.server.stdio

from .toggl_api import TogglAPI  # Original basic API
from .reports_api import TogglReportsAPI  # New reports API
from .admin_processor import AdminDataProcessor
from .models import AdminReportData

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("admin-toggl-mcp")

class AdminTogglServer:
    """Extended Toggl MCP server with admin-level analytics"""
    
    def __init__(self):
        self.toggl_api: Optional[TogglAPI] = None
        self.reports_api: Optional[TogglReportsAPI] = None
        self.processor = AdminDataProcessor()
        self.workspaces_cache = {}
    
    async def initialize_apis(self, api_token: str):
        """Initialize both Track API and Reports API"""
        try:
            self.toggl_api = TogglAPI(api_token)
            self.reports_api = TogglReportsAPI(api_token)
            
            # Cache workspace info
            workspaces = await self.toggl_api.get_workspaces()
            self.workspaces_cache = {ws.id: ws for ws in workspaces}
            
            logger.info("Admin Toggl APIs initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize APIs: {e}")
            raise
    
    async def get_workspace_info(self, workspace_id: int) -> Dict[str, Any]:
        """Get workspace information with caching"""
        if workspace_id in self.workspaces_cache:
            return self.workspaces_cache[workspace_id]
        
        # Fallback to API call
        try:
            workspace = await self.toggl_api.get_workspace(workspace_id)
            self.workspaces_cache[workspace_id] = workspace
            return workspace
        except Exception as e:
            logger.error(f"Failed to get workspace {workspace_id}: {e}")
            return {"id": workspace_id, "name": "Unknown", "default_currency": "USD"}

# Initialize server instance
admin_server = AdminTogglServer()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available tools including admin capabilities"""
    return [
        # Original basic tools
        Tool(
            name="start_tracking",
            description="Start tracking time for a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title/description of the task"},
                    "workspace_id": {"type": "integer", "description": "Workspace ID (optional)"},
                    "project_id": {"type": "integer", "description": "Project ID (optional)"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tags (optional)"}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="stop_tracking",
            description="Stop the currently running time entry",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="show_current_time_entry",
            description="Show the currently running time entry",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_workspaces",
            description="List all available workspaces",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="test_connection",
            description="Test the MCP server connection and API status",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        # New admin-level tools
        Tool(
            name="get_organization_dashboard",
            description="Get comprehensive organization dashboard with KPIs, hours, revenue, and profit metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer", "description": "Workspace ID"},
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "period": {"type": "string", "enum": ["week", "month", "quarter", "year"], "description": "Predefined period (optional)"}
                },
                "required": ["workspace_id"]
            }
        ),
        Tool(
            name="get_project_profitability_analysis",
            description="Get detailed project profitability analysis with profit margins, utilization rates, and ROI",
            inputSchema={
                "type": "object", 
                "properties": {
                    "workspace_id": {"type": "integer", "description": "Workspace ID"},
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "sort_by": {"type": "string", "enum": ["profit", "revenue", "margin", "hours"], "description": "Sort criterion"},
                    "min_hours": {"type": "number", "description": "Minimum hours threshold for inclusion"}
                },
                "required": ["workspace_id"]
            }
        ),
        Tool(
            name="get_team_productivity_report",
            description="Get team productivity report with utilization rates, performance metrics, and capacity analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer", "description": "Workspace ID"},
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "include_individual_metrics": {"type": "boolean", "description": "Include individual employee metrics"}
                },
                "required": ["workspace_id"]
            }
        ),
        Tool(
            name="get_client_profitability_analysis",
            description="Get client-level profitability and revenue analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer", "description": "Workspace ID"},
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "min_revenue": {"type": "number", "description": "Minimum revenue threshold"}
                },
                "required": ["workspace_id"]
            }
        ),
        Tool(
            name="get_financial_summary",
            description="Get high-level financial summary with revenue, costs, and profit trends",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer", "description": "Workspace ID"},
                    "period": {"type": "string", "enum": ["month", "quarter", "year"], "description": "Period for analysis"},
                    "compare_previous": {"type": "boolean", "description": "Include comparison with previous period"}
                },
                "required": ["workspace_id"]
            }
        ),
        Tool(
            name="get_productivity_insights",
            description="Get advanced productivity insights and time tracking patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer", "description": "Workspace ID"},
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "include_detailed_analysis": {"type": "boolean", "description": "Include detailed time entry analysis"}
                },
                "required": ["workspace_id"]
            }
        )
    ]

def _calculate_date_range(period: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Calculate date range based on period or explicit dates"""
    if start_date and end_date:
        return start_date, end_date
    
    today = datetime.now().date()
    
    if period == "week":
        start = today - timedelta(days=today.weekday())  # Monday
        end = start + timedelta(days=6)  # Sunday
    elif period == "month":
        start = today.replace(day=1)
        next_month = start.replace(month=start.month + 1) if start.month < 12 else start.replace(year=start.year + 1, month=1)
        end = next_month - timedelta(days=1)
    elif period == "quarter":
        quarter_start_month = ((today.month - 1) // 3) * 3 + 1
        start = today.replace(month=quarter_start_month, day=1)
        end = (start + timedelta(days=90)).replace(day=1) - timedelta(days=1)
    elif period == "year":
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
    else:
        # Default to current month
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for both basic and admin functionality"""
    
    try:
        # Basic tools (original functionality)
        if name == "start_tracking":
            if not admin_server.toggl_api:
                return [TextContent(type="text", text="Error: Toggl API not initialized. Please check your API token.")]
            result = await admin_server.toggl_api.start_time_entry(
                arguments["title"],
                arguments.get("workspace_id"),
                arguments.get("project_id"),
                arguments.get("tags", [])
            )
            return [TextContent(type="text", text=f"Started tracking: {result}")]
        
        elif name == "stop_tracking":
            if not admin_server.toggl_api:
                return [TextContent(type="text", text="Error: Toggl API not initialized. Please check your API token.")]
            result = await admin_server.toggl_api.stop_current_time_entry()
            return [TextContent(type="text", text=f"Stopped tracking: {result}")]
        
        elif name == "show_current_time_entry":
            if not admin_server.toggl_api:
                return [TextContent(type="text", text="Error: Toggl API not initialized. Please check your API token.")]
            result = await admin_server.toggl_api.get_current_time_entry()
            return [TextContent(type="text", text=f"Current entry: {result}")]
        
        elif name == "list_workspaces":
            if not admin_server.toggl_api:
                return [TextContent(type="text", text="Error: Toggl API not initialized. Please check your API token.")]
            workspaces = await admin_server.toggl_api.get_workspaces()
            workspace_list = "\n".join([f"• {ws.name} (ID: {ws.id})" for ws in workspaces])
            return [TextContent(type="text", text=f"Available workspaces:\n{workspace_list}")]
        
        elif name == "test_connection":
            api_status = "✅ Connected" if admin_server.toggl_api else "❌ Not connected"
            reports_status = "✅ Connected" if admin_server.reports_api else "❌ Not connected"
            return [TextContent(type="text", text=f"""🔗 **MCP Server Connection Test**

✅ **MCP Server**: Running successfully
{api_status} **Toggl Track API**
{reports_status} **Toggl Reports API**

💡 **Note**: If APIs show as not connected, please check your TOGGL_API_TOKEN environment variable.""")]
        
        # Admin tools (new functionality)
        elif name == "get_organization_dashboard":
            if not admin_server.reports_api:
                return [TextContent(type="text", text="Error: Toggl Reports API not initialized. Please check your API token.")]
            workspace_id = arguments["workspace_id"]
            start_date, end_date = _calculate_date_range(
                arguments.get("period"),
                arguments.get("start_date"),
                arguments.get("end_date")
            )
            
            result = await _get_organization_dashboard(workspace_id, start_date, end_date)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_project_profitability_analysis":
            workspace_id = arguments["workspace_id"]
            start_date, end_date = _calculate_date_range(
                None,
                arguments.get("start_date"),
                arguments.get("end_date")
            )
            
            result = await _get_project_profitability_analysis(
                workspace_id, start_date, end_date,
                arguments.get("sort_by", "profit"),
                arguments.get("min_hours", 0)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_team_productivity_report":
            workspace_id = arguments["workspace_id"]
            start_date, end_date = _calculate_date_range(
                None,
                arguments.get("start_date"),
                arguments.get("end_date")
            )
            
            result = await _get_team_productivity_report(
                workspace_id, start_date, end_date,
                arguments.get("include_individual_metrics", True)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_client_profitability_analysis":
            workspace_id = arguments["workspace_id"]
            start_date, end_date = _calculate_date_range(
                None,
                arguments.get("start_date"),
                arguments.get("end_date")
            )
            
            result = await _get_client_profitability_analysis(
                workspace_id, start_date, end_date,
                arguments.get("min_revenue", 0)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_financial_summary":
            workspace_id = arguments["workspace_id"]
            period = arguments.get("period", "month")
            start_date, end_date = _calculate_date_range(period)
            
            result = await _get_financial_summary(
                workspace_id, start_date, end_date,
                arguments.get("compare_previous", False)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_productivity_insights":
            workspace_id = arguments["workspace_id"]
            start_date, end_date = _calculate_date_range(
                None,
                arguments.get("start_date"),
                arguments.get("end_date")
            )
            
            result = await _get_productivity_insights(
                workspace_id, start_date, end_date,
                arguments.get("include_detailed_analysis", False)
            )
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def _get_organization_dashboard(workspace_id: int, start_date: str, end_date: str) -> str:
    """Get comprehensive organization dashboard"""
    try:
        # Get workspace info
        workspace_info = await admin_server.get_workspace_info(workspace_id)
        
        # Get summary data
        summary_data = await admin_server.reports_api.get_summary_report(
            workspace_id, start_date, end_date, "projects"
        )
        
        # Get detailed entries from Reports API v3 for accurate profitability calculations
        detailed_entries = await admin_server.reports_api.get_detailed_report_v3(
            workspace_id, start_date, end_date, hide_amounts=False
        )
        
        # Get insights data (keeping for compatibility)
        insights_data = await admin_server.reports_api.get_insights_profitability(
            workspace_id, start_date, end_date, "projects"
        )
        
        # Get user data
        user_summary = await admin_server.reports_api.get_summary_report(
            workspace_id, start_date, end_date, "users"
        )
        user_insights = await admin_server.reports_api.get_insights_profitability(
            workspace_id, start_date, end_date, "users"
        )
        
        # Get client data  
        client_summary = await admin_server.reports_api.get_summary_report(
            workspace_id, start_date, end_date, "clients"
        )
        client_insights = await admin_server.reports_api.get_insights_profitability(
            workspace_id, start_date, end_date, "clients"
        )
        
        # Process into admin report (keeping existing structure for now)
        admin_report = admin_server.processor.create_admin_report(
            workspace_info, summary_data, insights_data,
            user_summary, user_insights, client_summary, client_insights,
            [], f"{start_date} to {end_date}"
        )
        
        # Process profitability data from Reports API v3
        org = admin_report.organization_summary
        profitability_data = admin_server.processor.process_profitability_from_v3_data(detailed_entries, org.currency)
        
        return f"""
🏢 **ORGANIZATION DASHBOARD** - {org.workspace_name}
📅 Period: {start_date} to {end_date}

📊 **KEY METRICS**
• Total Hours: {profitability_data['total_hours']:,.1f}h
• Total Revenue: {org.currency} {profitability_data['total_revenue']:,.2f}
• Total Labor Cost: {org.currency} {profitability_data['total_labor_cost']:,.2f}
• Total Profit: {org.currency} {profitability_data['total_profit']:,.2f} ({profitability_data['profit_margin']:.1f}% margin)
• Average Rate: {org.currency} {profitability_data['average_hourly_rate']:.2f}/hour
• Labor Cost %: {profitability_data['labor_cost_percentage']*100:.0f}% of billing rate

🎯 **ORGANIZATIONAL HEALTH**
• Active Projects: {org.active_projects}
• Active Team Members: {org.active_users}
• Active Clients: {org.active_clients}
• Time Entries: {org.total_time_entries:,}
• Avg Hours/Project: {org.average_project_size:.1f}h
• Avg Hours/Person: {org.average_user_hours:.1f}h

💼 **TOP PROJECTS** (by profit)
{chr(10).join([f"• {p.project_name}: {org.currency} {p.profit:,.2f} ({p.profit_margin:.1f}% margin)" for p in admin_report.get_top_projects_by_profit(5)])}

👥 **TOP PERFORMERS** (by utilization)
{chr(10).join([f"• {e.username}: {e.utilization_rate:.1f}% utilization, {e.total_hours:.1f}h" for e in admin_report.get_top_employees_by_utilization(5)])}

⚠️ **AREAS FOR ATTENTION**
{chr(10).join([f"• {p.project_name}: {p.profit_margin:.1f}% margin (low profitability)" for p in admin_report.get_underperforming_projects(20)[:3]])}
        """.strip()
        
    except Exception as e:
        return f"Failed to get organization dashboard: {str(e)}"

async def _get_project_profitability_analysis(workspace_id: int, start_date: str, end_date: str, sort_by: str, min_hours: float) -> str:
    """Get detailed project profitability analysis"""
    try:
        print("🚀 VERSION 1.0.16 BULLETPROOF ANALYSIS STARTING! 🚀", flush=True)
        logger.info(f"🚀 VERSION 1.0.16: Starting project profitability analysis: workspace_id={workspace_id}, sort_by={sort_by}, min_hours={min_hours}")
        
        insights_data = await admin_server.reports_api.get_insights_profitability(
            workspace_id, start_date, end_date, "projects"
        )
        
        print(f"✅ VERSION 1.0.16: Got insights data successfully", flush=True)
        logger.info(f"✅ VERSION 1.0.16: Got insights data successfully")
        
        # Debug: Check the API response structure
        logger.info(f"Insights data keys: {list(insights_data.keys())}")
        logger.info(f"Data array length: {len(insights_data.get('data', []))}")
        if insights_data.get('data'):
            logger.info(f"First data item keys: {list(insights_data['data'][0].keys())}")
        
        workspace_info = await admin_server.get_workspace_info(workspace_id)
        currency = workspace_info.get('default_currency', 'USD')
        
        projects = admin_server.processor.process_project_profitability(insights_data, currency)
        
        logger.info(f"Received {len(projects)} valid ProjectProfitability objects from processor")
        
        # Filter by minimum hours with bulletproof error handling
        if min_hours > 0:
            filtered_projects = []
            for p in projects:
                try:
                    # Handle both dict and object cases
                    if hasattr(p, 'total_hours'):
                        hours = float(p.total_hours or 0)
                    elif isinstance(p, dict):
                        hours = float(p.get('total_hours', 0))
                    else:
                        logger.warning(f"Unknown project type: {type(p)}")
                        continue
                        
                    if hours >= min_hours:
                        filtered_projects.append(p)
                except Exception as e:
                    print(f"🔧 VERSION 1.0.16: Error filtering project: {str(e)}, type: {type(p)}", flush=True)
                    logger.error(f"🔧 VERSION 1.0.16: Error filtering project: {str(e)}, type: {type(p)}")
                    continue
                    
            projects = filtered_projects
            logger.info(f"After min_hours filter ({min_hours}h): {len(projects)} projects")
        
        # Sort by specified criterion with bulletproof error handling
        def safe_sort_key(p, attr_name, default=0):
            try:
                if hasattr(p, attr_name):
                    value = getattr(p, attr_name, default)
                elif isinstance(p, dict):
                    value = p.get(attr_name, default)
                else:
                    return default
                return float(value or default)
            except Exception:
                return default
        
        try:
            if sort_by == "revenue":
                projects.sort(key=lambda p: safe_sort_key(p, 'revenue'), reverse=True)
                logger.info(f"Sorted by revenue: {len(projects)} projects")
            elif sort_by == "margin":
                projects.sort(key=lambda p: safe_sort_key(p, 'profit_margin'), reverse=True)
                logger.info(f"Sorted by margin: {len(projects)} projects")
            elif sort_by == "hours":
                projects.sort(key=lambda p: safe_sort_key(p, 'total_hours'), reverse=True)
                logger.info(f"Sorted by hours: {len(projects)} projects")
            # Default is already sorted by profit
        except Exception as e:
            print(f"🔧 VERSION 1.0.16: Error sorting projects by {sort_by}: {str(e)}", flush=True)
            logger.error(f"🔧 VERSION 1.0.16: Error sorting projects by {sort_by}: {str(e)}")
            # Keep original order if sorting fails
        
        if not projects:
            return "No projects found matching the criteria."
        
        # Format output
        result = f"""
💰 **PROJECT PROFITABILITY ANALYSIS**
📅 Period: {start_date} to {end_date}
🔍 Showing {len(projects)} projects (min {min_hours}h, sorted by {sort_by})

"""
        
        for i, project in enumerate(projects[:10], 1):
            result += f"""
**{i}. {project.project_name}**
{f"   Client: {project.client_name}" if project.client_name else ""}
   • Hours: {project.total_hours:.1f}h total, {project.billable_hours:.1f}h billable ({project.utilization_rate:.1f}% util)
   • Revenue: {currency} {project.revenue:,.2f}
   • Profit: {currency} {project.profit:,.2f} ({project.profit_margin:.1f}% margin)
   • Rate: {currency} {project.billable_rate:.2f}/hour (avg)
   • Team: {project.active_users} members, {project.time_entries_count} entries
"""
        
        # Add summary stats with bulletproof error handling
        def safe_get_value(p, attr_name, default=0):
            try:
                if hasattr(p, attr_name):
                    value = getattr(p, attr_name, default)
                elif isinstance(p, dict):
                    value = p.get(attr_name, default)
                else:
                    return default
                return float(value or default)
            except Exception:
                return default
        
        total_revenue = sum(safe_get_value(p, 'revenue') for p in projects)
        total_profit = sum(safe_get_value(p, 'profit') for p in projects)
        avg_margin = sum(safe_get_value(p, 'profit_margin') for p in projects) / len(projects) if projects else 0
        
        result += f"""
📈 **SUMMARY STATISTICS**
• Total Revenue: {currency} {total_revenue:,.2f}
• Total Profit: {currency} {total_profit:,.2f}
• Average Margin: {avg_margin:.1f}%
• Most Profitable: {projects[0].project_name} ({projects[0].profit_margin:.1f}%)
"""
        
        return result
        
    except Exception as e:
        return f"Failed to get project profitability analysis: {str(e)}"

async def _get_team_productivity_report(workspace_id: int, start_date: str, end_date: str, include_individual_metrics: bool) -> str:
    """Get team productivity report"""
    try:
        insights_data = await admin_server.reports_api.get_insights_profitability(
            workspace_id, start_date, end_date, "users"
        )
        
        workspace_info = await admin_server.get_workspace_info(workspace_id)
        currency = workspace_info.get('default_currency', 'USD')
        
        # Get user summary data for employee profitability analysis
        user_summary = await admin_server.reports_api.get_summary_report(
            workspace_id, start_date, end_date, "users"
        )
        users = admin_server.processor.process_employee_profitability(user_summary, insights_data)
        
        if not users:
            return "No team members found or data available for this period."
        
        result = f"""
👥 **TEAM PRODUCTIVITY REPORT**
📅 Period: {start_date} to {end_date}
🔍 Showing {len(users)} team members

"""
        
        for i, user in enumerate(users, 1):
            result += f"""
**{i}. {user.username}**
   • Total Hours: {user.total_hours:.1f}h
   • Billable Hours: {user.billable_hours:.1f}h ({user.utilization_rate:.1f}% util)
   • Revenue: {currency} {user.revenue:,.2f}
   • Profit: {currency} {user.profit:,.2f} ({user.profit_margin:.1f}% margin)
   • Rate: {currency} {user.billable_rate:.2f}/hour (avg)
   • Projects: {user.active_projects}
"""
        
        # Add summary stats
        total_revenue = sum(u.revenue for u in users)
        total_profit = sum(u.profit for u in users)
        avg_margin = sum(u.profit_margin for u in users) / len(users)
        
        result += f"""
📈 **SUMMARY STATISTICS**
• Total Revenue: {currency} {total_revenue:,.2f}
• Total Profit: {currency} {total_profit:,.2f}
• Average Margin: {avg_margin:.1f}%
• Most Productive: {users[0].username} ({users[0].utilization_rate:.1f}% util)
"""
        
        return result
        
    except Exception as e:
        return f"Failed to get team productivity report: {str(e)}"

async def _get_client_profitability_analysis(workspace_id: int, start_date: str, end_date: str, min_revenue: float) -> str:
    """Get client-level profitability and revenue analysis"""
    try:
        insights_data = await admin_server.reports_api.get_insights_profitability(
            workspace_id, start_date, end_date, "clients"
        )
        
        workspace_info = await admin_server.get_workspace_info(workspace_id)
        currency = workspace_info.get('default_currency', 'USD')
        
        # Get client summary data for client profitability analysis
        client_summary = await admin_server.reports_api.get_summary_report(
            workspace_id, start_date, end_date, "clients"
        )
        clients = admin_server.processor.process_client_profitability(client_summary, insights_data, currency)
        
        # Filter by minimum revenue
        if min_revenue > 0:
            clients = [c for c in clients if c.revenue >= min_revenue]
        
        if not clients:
            return "No clients found matching the criteria."
        
        result = f"""
💰 **CLIENT PROFITABILITY ANALYSIS**
📅 Period: {start_date} to {end_date}
🔍 Showing {len(clients)} clients

"""
        
        for i, client in enumerate(clients[:10], 1):
            result += f"""
**{i}. {client.client_name}**
   • Total Revenue: {currency} {client.revenue:,.2f}
   • Total Profit: {currency} {client.profit:,.2f} ({client.profit_margin:.1f}% margin)
   • Projects: {client.active_projects}
"""
        
        # Add summary stats
        total_revenue = sum(c.revenue for c in clients)
        total_profit = sum(c.profit for c in clients)
        avg_margin = sum(c.profit_margin for c in clients) / len(clients)
        
        result += f"""
📈 **SUMMARY STATISTICS**
• Total Revenue: {currency} {total_revenue:,.2f}
• Total Profit: {currency} {total_profit:,.2f}
• Average Margin: {avg_margin:.1f}%
• Most Profitable: {clients[0].client_name} ({clients[0].profit_margin:.1f}% margin)
"""
        
        return result
        
    except Exception as e:
        return f"Failed to get client profitability analysis: {str(e)}"

async def _get_financial_summary(workspace_id: int, start_date: str, end_date: str, compare_previous: bool) -> str:
    """Get high-level financial summary"""
    try:
        summary_data = await admin_server.reports_api.get_summary_report(
            workspace_id, start_date, end_date, "projects"
        )
        
        workspace_info = await admin_server.get_workspace_info(workspace_id)
        currency = workspace_info.get('default_currency', 'USD')
        
        financial_summary = admin_server.processor.process_financial_summary(summary_data, currency)
        
        result = f"""
💰 **FINANCIAL SUMMARY**
📅 Period: {start_date} to {end_date}
🔍 Showing financial summary for {workspace_info.get('name', 'this workspace')}

"""
        
        result += f"""
📊 **FINANCIAL SUMMARY**
• Total Hours: {financial_summary['total_hours']:,.1f}h
• Billable Hours: {financial_summary['billable_hours']:,.1f}h
• Non-Billable Hours: {financial_summary['non_billable_hours']:,.1f}h
• Total Revenue: {currency} {financial_summary['total_revenue']:,.2f}
• Utilization Rate: {financial_summary['utilization_rate']:.1f}%
"""
        
        if compare_previous:
            result += f"""
📈 **COMPARISON WITH PREVIOUS PERIOD**
• This feature is currently being enhanced to provide period-over-period comparisons.
• Current focus is on current period financial metrics.
"""
        
        return result
        
    except Exception as e:
        return f"Failed to get financial summary: {str(e)}"

async def _get_productivity_insights(workspace_id: int, start_date: str, end_date: str, include_detailed_analysis: bool) -> str:
    """Get advanced productivity insights and time tracking patterns"""
    try:
        # Get detailed entries from Reports API v3 for accurate profitability calculations
        detailed_entries = await admin_server.reports_api.get_detailed_report_v3(
            workspace_id, start_date, end_date, hide_amounts=False
        )
        
        workspace_info = await admin_server.get_workspace_info(workspace_id)
        # Handle both dict and dataclass workspace info
        if hasattr(workspace_info, 'default_currency'):
            currency = workspace_info.default_currency
        else:
            currency = workspace_info.get('default_currency', 'USD')
        
        # Use the new profitability processing with Reports API v3 data
        profitability_data = admin_server.processor.process_profitability_from_v3_data(detailed_entries, currency)
        
        # Handle workspace name
        if hasattr(workspace_info, 'name'):
            workspace_name = workspace_info.name
        else:
            workspace_name = workspace_info.get('name', 'this workspace')
        
        result = f"""
💡 **PRODUCTIVITY INSIGHTS**
📅 Period: {start_date} to {end_date}
🔍 Showing productivity insights for {workspace_name}

"""
        
        result += f"""
📊 **TIME TRACKING PATTERNS**
• Total Hours: {profitability_data['total_hours']:,.1f}h
• Average Hourly Rate: {currency} {profitability_data['average_hourly_rate']:.2f}

📊 **PROFITABILITY METRICS**
• Total Revenue: {currency} {profitability_data['total_revenue']:,.2f}
• Total Labor Cost: {currency} {profitability_data['total_labor_cost']:,.2f}
• Total Profit: {currency} {profitability_data['total_profit']:,.2f}
• Profit Margin: {profitability_data['profit_margin']:.1f}%
• Labor Cost %: {profitability_data['labor_cost_percentage']*100:.0f}% of billing rate
"""
        
        if include_detailed_analysis:
            result += f"""
📊 **DETAILED ANALYSIS**
• This feature is currently being enhanced to provide more detailed insights.
• Current focus is on high-level productivity metrics and utilization rates.
"""
        
        return result
        
    except Exception as e:
        return f"Failed to get productivity insights: {str(e)}"

async def main():
    """Main entry point for the MCP server"""
    # Run the MCP server using the stdio_server context manager
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        # Create initialization options
        init_options = server.create_initialization_options()
        
        # Initialize the server with API token (but don't fail if missing)
        api_token = os.getenv("TOGGL_API_TOKEN")
        if api_token:
            try:
                await admin_server.initialize_apis(api_token)
                logger.info("Toggl APIs initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Toggl APIs: {e}")
                # Continue without API initialization - tools will show appropriate errors
        else:
            logger.warning("TOGGL_API_TOKEN not set - API features will be limited")
        
        # Run the server
        await server.run(read_stream, write_stream, init_options)