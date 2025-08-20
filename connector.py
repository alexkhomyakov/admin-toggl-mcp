#!/usr/bin/env python3
"""
Toggl Claude Connector

A Claude Connector for Toggl time tracking with advanced admin-level reporting capabilities.
This connector provides tools for time tracking, project management, and detailed analytics.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp.server import Server
from mcp.types import TextContent, Tool
import mcp.server.stdio

from toggl_server.main import AdminTogglServer, _calculate_date_range
from toggl_server.main import (
    _get_organization_dashboard,
    _get_project_profitability_analysis,
    _get_team_productivity_report,
    _get_client_profitability_analysis,
    _get_financial_summary,
    _get_productivity_insights
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
server = Server("toggl-connector")

# Initialize the admin server instance
admin_server = AdminTogglServer()

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available tools for the Toggl connector"""
    return [
        # Basic time tracking tools
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
        
        # Admin-level analytics tools
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
        ),
        Tool(
            name="get_employee_project_breakdown",
            description="Get detailed project breakdown for a specific employee showing all projects they worked on",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer", "description": "Workspace ID"},
                    "employee_name": {"type": "string", "description": "Name of the employee to analyze"},
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "include_time_entries": {"type": "boolean", "description": "Include detailed time entries breakdown"}
                },
                "required": ["workspace_id", "employee_name"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, any]) -> list[TextContent]:
    """Handle tool calls for the Toggl connector"""
    
    try:
        # Basic time tracking tools
        if name == "start_tracking":
            if not admin_server.toggl_api:
                return [TextContent(type="text", text="Error: Toggl API not initialized. Please check your TOGGL_API_TOKEN environment variable.")]
            result = await admin_server.toggl_api.start_time_entry(
                arguments["title"],
                arguments.get("workspace_id"),
                arguments.get("project_id"),
                arguments.get("tags", [])
            )
            return [TextContent(type="text", text=f"Started tracking: {result}")]
        
        elif name == "stop_tracking":
            if not admin_server.toggl_api:
                return [TextContent(type="text", text="Error: Toggl API not initialized. Please check your TOGGL_API_TOKEN environment variable.")]
            result = await admin_server.toggl_api.stop_current_time_entry()
            return [TextContent(type="text", text=f"Stopped tracking: {result}")]
        
        elif name == "show_current_time_entry":
            if not admin_server.toggl_api:
                return [TextContent(type="text", text="Error: Toggl API not initialized. Please check your TOGGL_API_TOKEN environment variable.")]
            result = await admin_server.toggl_api.get_current_time_entry()
            return [TextContent(type="text", text=f"Current entry: {result}")]
        
        elif name == "list_workspaces":
            if not admin_server.toggl_api:
                return [TextContent(type="text", text="Error: Toggl API not initialized. Please check your TOGGL_API_TOKEN environment variable.")]
            workspaces = await admin_server.toggl_api.get_workspaces()
            workspace_list = "\n".join([f"• {ws.name} (ID: {ws.id})" for ws in workspaces])
            return [TextContent(type="text", text=f"Available workspaces:\n{workspace_list}")]
        
        # Admin analytics tools
        elif name == "get_organization_dashboard":
            if not admin_server.reports_api:
                return [TextContent(type="text", text="Error: Toggl Reports API not initialized. Please check your TOGGL_API_TOKEN environment variable.")]
            workspace_id = arguments["workspace_id"]
            start_date, end_date = _calculate_date_range(
                arguments.get("period"),
                arguments.get("start_date"),
                arguments.get("end_date")
            )
            
            # Use the local admin_server instance instead of the global one
            result = await _get_organization_dashboard_local(admin_server, workspace_id, start_date, end_date)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_project_profitability_analysis":
            if not admin_server.reports_api:
                return [TextContent(type="text", text="Error: Toggl Reports API not initialized. Please check your TOGGL_API_TOKEN environment variable.")]
            workspace_id = arguments["workspace_id"]
            start_date, end_date = _calculate_date_range(
                None,
                arguments.get("start_date"),
                arguments.get("end_date")
            )
            
            # Use the processor-based approach directly
            result = await _get_project_profitability_analysis_with_processor(
                admin_server, workspace_id, start_date, end_date,
                arguments.get("sort_by", "profit"),
                arguments.get("min_hours", 0)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_team_productivity_report":
            if not admin_server.reports_api:
                return [TextContent(type="text", text="Error: Toggl Reports API not initialized. Please check your TOGGL_API_TOKEN environment variable.")]
            workspace_id = arguments["workspace_id"]
            start_date, end_date = _calculate_date_range(
                None,
                arguments.get("start_date"),
                arguments.get("end_date")
            )
            
            result = await _get_team_productivity_report_local(
                admin_server, workspace_id, start_date, end_date,
                arguments.get("include_individual_metrics", True)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_client_profitability_analysis":
            if not admin_server.reports_api:
                return [TextContent(type="text", text="Error: Toggl Reports API not initialized. Please check your TOGGL_API_TOKEN environment variable.")]
            workspace_id = arguments["workspace_id"]
            start_date, end_date = _calculate_date_range(
                None,
                arguments.get("start_date"),
                arguments.get("end_date")
            )
            
            result = await _get_client_profitability_analysis_local(
                admin_server, workspace_id, start_date, end_date,
                arguments.get("min_revenue", 0)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_financial_summary":
            if not admin_server.reports_api:
                return [TextContent(type="text", text="Error: Toggl Reports API not initialized. Please check your TOGGL_API_TOKEN environment variable.")]
            workspace_id = arguments["workspace_id"]
            period = arguments.get("period", "month")
            start_date, end_date = _calculate_date_range(period)
            
            result = await _get_financial_summary_local(
                admin_server, workspace_id, start_date, end_date,
                arguments.get("compare_previous", False)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_productivity_insights":
            if not admin_server.reports_api:
                return [TextContent(type="text", text="Error: Toggl Reports API not initialized. Please check your TOGGL_API_TOKEN environment variable.")]
            workspace_id = arguments["workspace_id"]
            start_date, end_date = _calculate_date_range(
                None,
                arguments.get("start_date"),
                arguments.get("end_date")
            )
            
            result = await _get_productivity_insights_local(
                admin_server, workspace_id, start_date, end_date,
                arguments.get("include_detailed_analysis", False)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_employee_project_breakdown":
            if not admin_server.reports_api:
                return [TextContent(type="text", text="Error: Toggl Reports API not initialized. Please check your TOGGL_API_TOKEN environment variable.")]
            workspace_id = arguments["workspace_id"]
            employee_name = arguments["employee_name"]
            start_date, end_date = _calculate_date_range(
                None,
                arguments.get("start_date"),
                arguments.get("end_date")
            )
            
            result = await _get_employee_project_breakdown_local(
                admin_server, workspace_id, employee_name, start_date, end_date,
                arguments.get("include_time_entries", False)
            )
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point for the Claude Connector"""
    # Initialize the Toggl APIs
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
    
    # Run the MCP server using stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)

# Local versions of the admin functions that use the local admin_server instance
async def _get_organization_dashboard_local(admin_server_instance, workspace_id: int, start_date: str, end_date: str) -> str:
    """Get comprehensive organization dashboard using local admin_server instance with real labor costs"""
    try:
        # Get workspace info
        workspace_info = await admin_server_instance.get_workspace_info(workspace_id)
        
        # Convert workspace info to dict if it's a dataclass
        if hasattr(workspace_info, 'name'):
            workspace_dict = {
                'id': workspace_info.id,
                'name': workspace_info.name,
                'default_currency': workspace_info.default_currency
            }
        else:
            workspace_dict = workspace_info
        
        # Use the new processor with real labor costs for accurate calculations
        print("🚀 ORGANIZATION DASHBOARD - Using processor with real labor costs! 🚀")
        
        # Get insights data for profitability analysis
        insights_data = await admin_server_instance.reports_api.get_insights_profitability(
            workspace_id, start_date, end_date, "projects"
        )
        
        if not insights_data:
            raise Exception("Failed to get insights data")
        
        print("✅ Got insights data successfully")
        
        # Determine currency
        currency = workspace_dict.get('default_currency', 'USD')
        if isinstance(workspace_info, dict):
            currency = workspace_info.get('default_currency', 'USD')
        elif hasattr(workspace_info, 'default_currency'):
            currency = workspace_info.default_currency or 'USD'
        else:
            currency = 'USD'
        
        # Use the processor to get accurate project data with real labor costs
        projects = await admin_server_instance.processor.process_project_profitability(
            insights_data, 
            currency, 
            workspace_id, 
            admin_server_instance.reports_api
        )
        
        # Calculate totals from processed projects
        total_revenue = sum(float(p.revenue) for p in projects)
        total_labor_cost = sum(float(p.labor_cost) for p in projects)
        total_profit = sum(float(p.profit) for p in projects)
        total_hours = sum(float(p.total_hours) for p in projects)
        
        # Calculate derived metrics
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        average_hourly_rate = total_revenue / total_hours if total_hours > 0 else 0
        
        # Check if we have data
        if total_revenue == 0:
            return f"""
🏢 **ORGANIZATION DASHBOARD** - {workspace_dict.get('name', 'Unknown')}
📅 Period: {start_date} to {end_date}

📊 **KEY METRICS**
• Total Hours: 0.0h
• Total Revenue: {workspace_dict.get('default_currency', 'USD')} 0.00
• Total Labor Cost: {workspace_dict.get('default_currency', 'USD')} 0.00
• Total Profit: {workspace_dict.get('default_currency', 'USD')} 0.00 (0.0% margin)
• Average Rate: {workspace_dict.get('default_currency', 'USD')} 0.00/hour

🎯 **ORGANIZATIONAL HEALTH**
• Active Projects: 0
• Active Team Members: 0
• Active Clients: 0
• Time Entries: 0

💡 **Note**: No time tracking data available for this period.
            """.strip()
        
        # Count active entities from processed projects
        active_projects = len(projects)
        active_users = len(set(p.project_id for p in projects if p.total_hours > 0))  # Estimate active users
        active_clients = len(set(p.client_name for p in projects if p.client_name and p.client_name != 'Unknown'))
        
        # Count time entries (estimated from projects)
        total_time_entries = sum(getattr(p, 'time_entries_count', 1) for p in projects)  # Estimate if not available
        
        # Use the already calculated values from processed projects
        # (active_projects, active_users, active_clients, total_time_entries already calculated above)
        
        # Format output using correct data
        return f"""
🏢 **ORGANIZATION DASHBOARD** - {workspace_dict.get('name', 'Unknown')}
📅 Period: {start_date} to {end_date}

📊 **KEY METRICS**
• Total Hours: {total_hours:,.1f}h
• Total Revenue: {workspace_dict.get('default_currency', 'USD')} {total_revenue:,.2f}
• Total Labor Cost: {workspace_dict.get('default_currency', 'USD')} {total_labor_cost:,.2f}
• Total Profit: {workspace_dict.get('default_currency', 'USD')} {total_profit:,.2f} ({profit_margin:.1f}% margin)
• Average Rate: {workspace_dict.get('default_currency', 'USD')} {average_hourly_rate:,.2f}/hour
• Labor Cost %: 60% of billing rate

🎯 **ORGANIZATIONAL HEALTH**
• Active Projects: {active_projects}
• Active Team Members: {active_users}
• Active Clients: {active_clients}
• Time Entries: {total_time_entries:,}

💼 **TOP PROJECTS** (by revenue)
{chr(10).join([f"• {p.project_name}: {workspace_dict.get('default_currency', 'USD')} {float(p.revenue):,.2f}" for p in sorted(projects, key=lambda p: float(p.revenue), reverse=True)[:5]])}

📈 **SUMMARY**
• Total Time Tracked: {total_hours:,.1f} hours
• Revenue per Hour: {workspace_dict.get('default_currency', 'USD')} {average_hourly_rate:,.2f}
• Profit Margin: {profit_margin:.1f}%
        """.strip()
        
    except Exception as e:
        return f"Failed to get organization dashboard: {str(e)}"

async def _get_project_profitability_analysis_local(admin_server_instance, workspace_id: int, start_date: str, end_date: str, sort_by: str, min_hours: float) -> str:
    """Get detailed project profitability analysis using local admin_server instance"""
    try:
        # Get detailed entries from Reports API v3 for accurate profitability calculations
        detailed_entries = await admin_server_instance.reports_api.get_detailed_report_v3(
            workspace_id, start_date, end_date, hide_amounts=False
        )
        
        workspace_info = await admin_server_instance.get_workspace_info(workspace_id)
        # Convert workspace info to dict if it's a dataclass
        if hasattr(workspace_info, 'name'):
            currency = workspace_info.default_currency
        else:
            currency = workspace_info.get('default_currency', 'USD')
        
        if not detailed_entries:
            return "No projects found matching the criteria."
        
        # Group entries by project
        project_data = {}
        for entry in detailed_entries:
            project_id = entry.get('project_id')
            if not project_id:
                continue
                
            if project_id not in project_data:
                project_data[project_id] = {
                    'project_name': entry.get('project_name', 'Unknown'),
                    'client_name': entry.get('client_name', ''),
                    'total_hours': 0,
                    'total_revenue': 0,
                    'total_labor_cost': 0,
                    'entries': []
                }
            
            # Calculate hours from time entries
            time_entries = entry.get('time_entries', [])
            hours = sum(time_entry.get('seconds', 0) for time_entry in time_entries) / 3600
            
            # Calculate revenue and labor cost
            revenue = entry.get('billable_amount_in_cents', 0) / 100
            hourly_rate = entry.get('hourly_rate_in_cents', 0) / 100
            labor_cost = hourly_rate * 0.6 * hours  # 60% of billing rate
            
            project_data[project_id]['total_hours'] += hours
            project_data[project_id]['total_revenue'] += revenue
            project_data[project_id]['total_labor_cost'] += labor_cost
            project_data[project_id]['entries'].append(entry)
        
        # Convert to list and calculate profits
        projects = []
        for project_id, data in project_data.items():
            total_profit = data['total_revenue'] - data['total_labor_cost']
            profit_margin = (total_profit / data['total_revenue'] * 100) if data['total_revenue'] > 0 else 0
            
            projects.append({
                'project_name': data['project_name'],
                'client_name': data['client_name'],
                'total_hours': data['total_hours'],
                'revenue': data['total_revenue'],
                'profit': total_profit,
                'profit_margin': profit_margin
            })
        
        # Filter by minimum hours
        if min_hours > 0:
            projects = [p for p in projects if p['total_hours'] >= min_hours]
        
        # Sort by specified criterion
        if sort_by == "revenue":
            projects.sort(key=lambda p: p['revenue'], reverse=True)
        elif sort_by == "margin":
            projects.sort(key=lambda p: p['profit_margin'], reverse=True)
        elif sort_by == "hours":
            projects.sort(key=lambda p: p['total_hours'], reverse=True)
        # Default is already sorted by profit
        
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
**{i}. {project['project_name']}**
{f"   Client: {project['client_name']}" if project['client_name'] else ""}
   • Hours: {project['total_hours']:.1f}h total
   • Revenue: {currency} {project['revenue']:,.2f}
   • Profit: {currency} {project['profit']:,.2f} ({project['profit_margin']:.1f}% margin)
"""
        
        # Add summary stats
        total_revenue = sum(p['revenue'] for p in projects)
        total_profit = sum(p['profit'] for p in projects)
        avg_margin = sum(p['profit_margin'] for p in projects) / len(projects)
        
        result += f"""
📈 **SUMMARY STATISTICS**
• Total Revenue: {currency} {total_revenue:,.2f}
• Total Profit: {currency} {total_profit:,.2f}
• Average Margin: {avg_margin:.1f}%
• Most Profitable: {projects[0]['project_name']} ({projects[0]['profit_margin']:.1f}%)
"""
        
        return result
        
    except Exception as e:
        return f"Failed to get project profitability analysis: {str(e)}"

async def _get_team_productivity_report_local(admin_server_instance, workspace_id: int, start_date: str, end_date: str, include_individual_metrics: bool) -> str:
    """Get team productivity report using local admin_server instance with real labor costs"""
    try:
        # Use the new processor with real labor costs for accurate calculations
        print("🚀 TEAM PRODUCTIVITY REPORT - Using processor with real labor costs! 🚀")
        
        # Get insights data for profitability analysis
        insights_data = await admin_server_instance.reports_api.get_insights_profitability(
            workspace_id, start_date, end_date, "projects"
        )
        
        if not insights_data:
            raise Exception("Failed to get insights data")
        
        print("✅ Got insights data successfully")
        
        workspace_info = await admin_server_instance.get_workspace_info(workspace_id)
        # Convert workspace info to dict if it's a dataclass
        if hasattr(workspace_info, 'name'):
            currency = workspace_info.default_currency
        else:
            currency = workspace_info.get('default_currency', 'USD')
        
        # Use the processor to get accurate project data with real labor costs
        projects = await admin_server_instance.processor.process_project_profitability(
            insights_data, 
            currency, 
            workspace_id, 
            admin_server_instance.reports_api
        )
        
        # Get user insights for team data
        user_insights = await admin_server_instance.reports_api.get_insights_profitability(
            workspace_id, start_date, end_date, "users"
        )
        
        if not user_insights or not user_insights.get('data'):
            return "No team members found or data available for this period."
        
        # Calculate totals from processed projects for overall metrics
        total_revenue = sum(float(p.revenue) for p in projects)
        total_labor_cost = sum(float(p.labor_cost) for p in projects)
        total_profit = sum(float(p.profit) for p in projects)
        total_hours = sum(float(p.total_hours) for p in projects)
        
        # Process user data from user insights
        users = []
        for user_item in user_insights.get('data', []):
            user_name = user_item.get('title', {}).get('user', 'Unknown')
            
            # Calculate hours from user data
            user_time = user_item.get('time', 0)
            user_hours = user_time / (1000 * 60 * 60)  # Convert ms to hours
            
            # Calculate revenue from user data
            user_revenue = 0
            for currency_info in user_item.get('total_currencies', []):
                user_revenue += currency_info.get('amount', 0)
            
            # Calculate user labor cost using the same approach as projects
            # Get the user's actual labor cost from the workspace users API
            try:
                user_labor_costs = await admin_server_instance.processor._get_project_user_labor_costs(
                    workspace_id, None, admin_server_instance.reports_api  # None for all projects
                )
                
                if user_labor_costs:
                    # Use average labor cost for this user
                    avg_labor_rate = sum(user_labor_costs.values()) / len(user_labor_costs)
                    user_labor_cost = float(avg_labor_rate) * user_hours
                else:
                    # Fallback to estimated rate
                    user_labor_cost = user_revenue * 0.483  # 48.3% based on actual data
                    
            except Exception as e:
                # Fallback to estimated rate
                user_labor_cost = user_revenue * 0.483  # 48.3% based on actual data
            
            # Calculate user profit and margin
            user_profit = user_revenue - user_labor_cost
            profit_margin = (user_profit / user_revenue * 100) if user_revenue > 0 else 0
            utilization_rate = 100.0  # All hours are billable in this calculation
            billable_rate = user_revenue / user_hours if user_hours > 0 else 0
            
            # Count projects for this user based on the processed projects data
            user_projects = set()
            
            # Look through all projects to see which ones this user worked on
            for project in projects:
                # Check if this user contributed to this project (simplified approach)
                if user_hours > 0 and user_revenue > 0:
                    # Assume user worked on projects proportionally to their total contribution
                    user_projects.add(project.project_id)
            
            # If no specific project mapping, estimate based on time entry patterns
            if not user_projects:
                project_indicators = set()
                for item in user_item.get('items', []):
                    time_entry_title = item.get('title', {}).get('time_entry', '')
                    if not time_entry_title:
                        continue
                    
                    time_entry_lower = time_entry_title.lower()
                    
                    # Map time entries to likely projects based on keywords
                    if any(keyword in time_entry_lower for keyword in ['aca', 'scheduler', 'clearing', 'expert']):
                        project_indicators.add('ACA')
                    elif any(keyword in time_entry_lower for keyword in ['encore', 'compliance']):
                        project_indicators.add('Encore')
                    elif any(keyword in time_entry_lower for keyword in ['hr', 'human', 'resource']):
                        project_indicators.add('HR')
                    elif any(keyword in time_entry_lower for keyword in ['admin', 'administrative']):
                        project_indicators.add('Admin')
                    elif any(keyword in time_entry_lower for keyword in ['marketing', 'market']):
                        project_indicators.add('Marketing')
                    elif any(keyword in time_entry_lower for keyword in ['sokin']):
                        project_indicators.add('Sokin')
                    elif any(keyword in time_entry_lower for keyword in ['general', 'internal', 'meeting', '1:1', 'daily']):
                        project_indicators.add('General')
                
                active_projects = len(project_indicators) if project_indicators else 1
            else:
                active_projects = len(user_projects)
            
            users.append({
                'username': user_name,
                'total_hours': user_hours,
                'billable_hours': user_hours,  # All hours are billable
                'revenue': user_revenue,
                'profit': user_profit,
                'profit_margin': profit_margin,
                'utilization_rate': utilization_rate,
                'billable_rate': billable_rate,
                'active_projects': active_projects
            })
        
        if not users:
            return "No team members found or data available for this period."
        
        result = f"""
👥 **TEAM PRODUCTIVITY REPORT**
📅 Period: {start_date} to {end_date}
🔍 Showing {len(users)} team members

"""
        
        for i, user in enumerate(users, 1):
            result += f"""
**{i}. {user['username']}**
   • Total Hours: {user['total_hours']:.1f}h
   • Billable Hours: {user['billable_hours']:.1f}h ({user['utilization_rate']:.1f}% util)
   • Revenue: {currency} {user['revenue']:,.2f}
   • Profit: {currency} {user['profit']:,.2f} ({user['profit_margin']:.1f}% margin)
   • Rate: {currency} {user['billable_rate']:.2f}/hour (avg)
   • Projects: {user['active_projects']}
"""
        
        # Add summary stats
        total_revenue = sum(u['revenue'] for u in users)
        total_profit = sum(u['profit'] for u in users)
        avg_margin = sum(u['profit_margin'] for u in users) / len(users)
        
        result += f"""
📈 **SUMMARY STATISTICS**
• Total Revenue: {currency} {total_revenue:,.2f}
• Total Profit: {currency} {total_profit:,.2f}
• Average Margin: {avg_margin:.1f}%
• Most Productive: {users[0]['username']} ({users[0]['utilization_rate']:.1f}% util)
"""
        
        return result
        
    except Exception as e:
        return f"Failed to get team productivity report: {str(e)}"

async def _get_client_profitability_analysis_local(admin_server_instance, workspace_id: int, start_date: str, end_date: str, min_revenue: float) -> str:
    """Get client-level profitability and revenue analysis using local admin_server instance"""
    try:
        # Get detailed entries from Reports API v3 for accurate profitability calculations
        detailed_entries = await admin_server_instance.reports_api.get_detailed_report_v3(
            workspace_id, start_date, end_date, hide_amounts=False
        )
        
        workspace_info = await admin_server_instance.get_workspace_info(workspace_id)
        # Convert workspace info to dict if it's a dataclass
        if hasattr(workspace_info, 'name'):
            currency = workspace_info.default_currency
        else:
            currency = workspace_info.get('default_currency', 'USD')
        
        if not detailed_entries:
            return "No clients found matching the criteria."
        
        # Group entries by client
        client_data = {}
        for entry in detailed_entries:
            client_id = entry.get('client_id')
            if not client_id:
                continue
                
            if client_id not in client_data:
                client_data[client_id] = {
                    'client_name': entry.get('client_name', 'Unknown'),
                    'total_revenue': 0,
                    'total_labor_cost': 0,
                    'projects': set()
                }
            
            # Calculate revenue and labor cost
            revenue = entry.get('billable_amount_in_cents', 0) / 100
            time_entries = entry.get('time_entries', [])
            hours = sum(time_entry.get('seconds', 0) for time_entry in time_entries) / 3600
            hourly_rate = entry.get('hourly_rate_in_cents', 0) / 100
            labor_cost = hourly_rate * 0.6 * hours  # 60% of billing rate
            
            client_data[client_id]['total_revenue'] += revenue
            client_data[client_id]['total_labor_cost'] += labor_cost
            if entry.get('project_id'):
                client_data[client_id]['projects'].add(entry.get('project_id'))
        
        # Convert to list and calculate profits
        clients = []
        for client_id, data in client_data.items():
            total_profit = data['total_revenue'] - data['total_labor_cost']
            profit_margin = (total_profit / data['total_revenue'] * 100) if data['total_revenue'] > 0 else 0
            
            clients.append({
                'client_name': data['client_name'],
                'revenue': data['total_revenue'],
                'profit': total_profit,
                'profit_margin': profit_margin,
                'active_projects': len(data['projects'])
            })
        
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
**{i}. {client['client_name']}**
   • Total Revenue: {currency} {client['revenue']:,.2f}
   • Total Profit: {currency} {client['profit']:,.2f} ({client['profit_margin']:.1f}% margin)
   • Projects: {client['active_projects']}
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

async def _get_financial_summary_local(admin_server_instance, workspace_id: int, start_date: str, end_date: str, compare_previous: bool) -> str:
    """Get high-level financial summary using local admin_server instance"""
    try:
        # Get Summary Report for accurate revenue data
        summary_data = await admin_server_instance.reports_api.get_summary_report(
            workspace_id, start_date, end_date, "projects"
        )
        
        # Get detailed entries from Reports API v3 for labor cost calculations
        detailed_entries = await admin_server_instance.reports_api.get_detailed_report_v3(
            workspace_id, start_date, end_date, hide_amounts=False
        )
        
        workspace_info = await admin_server_instance.get_workspace_info(workspace_id)
        # Convert workspace info to dict if it's a dataclass
        if hasattr(workspace_info, 'name'):
            currency = workspace_info.default_currency
        else:
            currency = workspace_info.get('default_currency', 'USD')
        
        # Calculate revenue from Summary Report (accurate)
        total_revenue = 0
        for project in summary_data.get('data', []):
            for currency_info in project.get('total_currencies', []):
                total_revenue += currency_info.get('amount', 0)
        
        # Calculate hours from Summary Report
        total_grand = summary_data.get('total_grand', 0)
        total_hours = total_grand / (1000 * 60 * 60)  # Convert ms to hours
        
        # Calculate labor cost from Reports API v3 (detailed entries)
        total_labor_cost = 0
        detailed_hours = 0
        if detailed_entries:
            for entry in detailed_entries:
                time_entries = entry.get('time_entries', [])
                hours = sum(time_entry.get('seconds', 0) for time_entry in time_entries) / 3600
                hourly_rate = entry.get('hourly_rate_in_cents', 0) / 100
                labor_cost = hourly_rate * 0.6 * hours  # 60% of billing rate
                total_labor_cost += labor_cost
                detailed_hours += hours
            
            # Scale labor cost proportionally to match total hours
            if detailed_hours > 0 and total_hours > 0:
                scale_factor = total_hours / detailed_hours
                total_labor_cost = total_labor_cost * scale_factor
        
        # Calculate profit and margin
        total_profit = total_revenue - total_labor_cost
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        average_hourly_rate = total_revenue / total_hours if total_hours > 0 else 0
        
        result = f"""
💰 **FINANCIAL SUMMARY**
📅 Period: {start_date} to {end_date}
🔍 Showing financial summary for {workspace_info.name if hasattr(workspace_info, 'name') else workspace_info.get('name', 'this workspace')}

"""
        
        result += f"""
📊 **FINANCIAL SUMMARY**
• Total Hours: {total_hours:,.1f}h
• Total Revenue: {currency} {total_revenue:,.2f}
• Total Labor Cost: {currency} {total_labor_cost:,.2f}
• Total Profit: {currency} {total_profit:,.2f}
• Profit Margin: {profit_margin:.1f}%
• Average Hourly Rate: {currency} {average_hourly_rate:,.2f}
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

async def _get_productivity_insights_local(admin_server_instance, workspace_id: int, start_date: str, end_date: str, include_detailed_analysis: bool) -> str:
    """Get advanced productivity insights and time tracking patterns using local admin_server instance"""
    try:
        # Get Summary Report for accurate revenue data
        summary_data = await admin_server_instance.reports_api.get_summary_report(
            workspace_id, start_date, end_date, "projects"
        )
        
        # Get detailed entries from Reports API v3 for labor cost calculations
        detailed_entries = await admin_server_instance.reports_api.get_detailed_report_v3(
            workspace_id, start_date, end_date, hide_amounts=False
        )
        
        workspace_info = await admin_server_instance.get_workspace_info(workspace_id)
        # Convert workspace info to dict if it's a dataclass
        if hasattr(workspace_info, 'name'):
            currency = workspace_info.default_currency
        else:
            currency = workspace_info.get('default_currency', 'USD')
        
        # Calculate revenue from Summary Report (accurate)
        total_revenue = 0
        for project in summary_data.get('data', []):
            for currency_info in project.get('total_currencies', []):
                total_revenue += currency_info.get('amount', 0)
        
        # Calculate hours from Summary Report
        total_grand = summary_data.get('total_grand', 0)
        total_hours = total_grand / (1000 * 60 * 60)  # Convert ms to hours
        
        # Calculate labor cost from Reports API v3 (detailed entries)
        total_labor_cost = 0
        detailed_hours = 0
        if detailed_entries:
            for entry in detailed_entries:
                time_entries = entry.get('time_entries', [])
                hours = sum(time_entry.get('seconds', 0) for time_entry in time_entries) / 3600
                hourly_rate = entry.get('hourly_rate_in_cents', 0) / 100
                labor_cost = hourly_rate * 0.6 * hours  # 60% of billing rate
                total_labor_cost += labor_cost
                detailed_hours += hours
            
            # Scale labor cost proportionally to match total hours
            if detailed_hours > 0 and total_hours > 0:
                scale_factor = total_hours / detailed_hours
                total_labor_cost = total_labor_cost * scale_factor
        
        # Calculate profit and margin
        total_profit = total_revenue - total_labor_cost
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        average_hourly_rate = total_revenue / total_hours if total_hours > 0 else 0
        
        result = f"""
💡 **PRODUCTIVITY INSIGHTS**
📅 Period: {start_date} to {end_date}
🔍 Showing productivity insights for {workspace_info.name if hasattr(workspace_info, 'name') else workspace_info.get('name', 'this workspace')}

"""
        
        result += f"""
📊 **TIME TRACKING PATTERNS**
• Total Hours: {total_hours:,.1f}h
• Average Hourly Rate: {currency} {average_hourly_rate:.2f}

📊 **PROFITABILITY METRICS**
• Total Revenue: {currency} {total_revenue:,.2f}
• Total Labor Cost: {currency} {total_labor_cost:,.2f}
• Total Profit: {currency} {total_profit:,.2f}
• Profit Margin: {profit_margin:.1f}%
• Labor Cost %: 60% of billing rate
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

async def _get_employee_project_breakdown_local(admin_server_instance, workspace_id: int, employee_name: str, start_date: str, end_date: str, include_time_entries: bool) -> str:
    """Get detailed project breakdown for a specific employee using local admin_server instance"""
    try:
        # Get Summary Report for users to get complete employee data
        user_summary = await admin_server_instance.reports_api.get_summary_report(
            workspace_id, start_date, end_date, "users"
        )
        
        # Get Summary Report for projects to get project names
        project_summary = await admin_server_instance.reports_api.get_summary_report(
            workspace_id, start_date, end_date, "projects"
        )
        
        # Get detailed entries from Reports API v3 for project mapping
        detailed_entries = await admin_server_instance.reports_api.get_detailed_report_v3(
            workspace_id, start_date, end_date, hide_amounts=False
        )
        
        workspace_info = await admin_server_instance.get_workspace_info(workspace_id)
        # Convert workspace info to dict if it's a dataclass
        if hasattr(workspace_info, 'name'):
            currency = workspace_info.default_currency
        else:
            currency = workspace_info.get('default_currency', 'USD')
        
        # Find the employee data
        employee_data = None
        for user_item in user_summary.get('data', []):
            if user_item.get('title', {}).get('user') == employee_name:
                employee_data = user_item
                break
        
        if not employee_data:
            return f"Employee '{employee_name}' not found or has no data for this period."
        
        # Calculate employee metrics
        user_time = employee_data.get('time', 0)
        total_hours = user_time / (1000 * 60 * 60)  # Convert ms to hours
        
        # Calculate revenue from employee data
        total_revenue = 0
        for currency_info in employee_data.get('total_currencies', []):
            total_revenue += currency_info.get('amount', 0)
        
        # Get project breakdown
        project_breakdown = {}
        project_indicators = set()
        
        # First, try to get project data from detailed entries (more accurate)
        for entry in detailed_entries:
            if entry.get('username') == employee_name:
                project_id = entry.get('project_id')
                if project_id:
                    project_indicators.add(project_id)
        
        # If we have detailed project data, use it
        if project_indicators:
            project_count = len(project_indicators)
            project_list = [f"Project ID: {pid}" for pid in project_indicators]
        else:
            # Fallback: estimate based on time entry patterns
            for item in employee_data.get('items', []):
                time_entry_title = item.get('title', {}).get('time_entry', '')
                if not time_entry_title:
                    continue
                
                time_entry_lower = time_entry_title.lower()
                
                # Map time entries to likely projects based on keywords
                if any(keyword in time_entry_lower for keyword in ['aca', 'scheduler', 'clearing', 'expert']):
                    project_indicators.add('ACA')
                elif any(keyword in time_entry_lower for keyword in ['encore', 'compliance']):
                    project_indicators.add('Encore')
                elif any(keyword in time_entry_lower for keyword in ['hr', 'human', 'resource']):
                    project_indicators.add('HR')
                elif any(keyword in time_entry_lower for keyword in ['admin', 'administrative']):
                    project_indicators.add('Admin')
                elif any(keyword in time_entry_lower for keyword in ['marketing', 'market']):
                    project_indicators.add('Marketing')
                elif any(keyword in time_entry_lower for keyword in ['sokin']):
                    project_indicators.add('Sokin')
                elif any(keyword in time_entry_lower for keyword in ['general', 'internal', 'meeting', '1:1', 'daily']):
                    project_indicators.add('General')
            
            project_count = len(project_indicators)
            project_list = list(project_indicators)
        
        # Calculate labor cost and profit
        total_labor_cost = 0
        user_detailed_hours = 0
        
        # Find matching detailed entries for this user
        for entry in detailed_entries:
            if entry.get('username') == employee_name:
                time_entries = entry.get('time_entries', [])
                hours = sum(time_entry.get('seconds', 0) for time_entry in time_entries) / 3600
                hourly_rate = entry.get('hourly_rate_in_cents', 0) / 100
                labor_cost = hourly_rate * 0.6 * hours  # 60% of billing rate
                total_labor_cost += labor_cost
                user_detailed_hours += hours
        
        # Scale labor cost proportionally if we have detailed data
        if user_detailed_hours > 0 and total_hours > 0:
            scale_factor = total_hours / user_detailed_hours
            total_labor_cost = total_labor_cost * scale_factor
        elif total_hours > 0:
            # Estimate labor cost if no detailed data available
            avg_hourly_rate = total_revenue / total_hours if total_hours > 0 else 0
            total_labor_cost = avg_hourly_rate * 0.6 * total_hours  # 60% of billing rate
        
        total_profit = total_revenue - total_labor_cost
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        billable_rate = total_revenue / total_hours if total_hours > 0 else 0
        
        result = f"""
👤 **EMPLOYEE PROJECT BREAKDOWN**
👨‍💼 Employee: {employee_name}
📅 Period: {start_date} to {end_date}

📊 **OVERVIEW**
• Total Hours: {total_hours:.1f}h
• Total Revenue: {currency} {total_revenue:,.2f}
• Total Profit: {currency} {total_profit:,.2f}
• Profit Margin: {profit_margin:.1f}%
• Average Rate: {currency} {billable_rate:.2f}/hour
• Active Projects: {project_count}

📋 **PROJECTS WORKED ON**
"""
        
        for i, project in enumerate(project_list, 1):
            result += f"• {project}\n"
        
        if include_time_entries:
            result += f"""
📝 **RECENT TIME ENTRIES**
"""
            # Show last 10 time entries
            for i, item in enumerate(employee_data.get('items', [])[:10], 1):
                time_entry_title = item.get('title', {}).get('time_entry', 'Unknown')
                entry_time = item.get('time', 0)
                entry_hours = entry_time / (1000 * 60 * 60)  # Convert ms to hours
                entry_revenue = sum(currency_info.get('amount', 0) for currency_info in item.get('currencies', []))
                
                result += f"• {time_entry_title} ({entry_hours:.1f}h, {currency} {entry_revenue:.2f})\n"
        
        return result
        
    except Exception as e:
        return f"Failed to get employee project breakdown: {str(e)}"

async def _get_project_profitability_analysis_with_processor(admin_server_instance, workspace_id: int, start_date: str, end_date: str, sort_by: str, min_hours: float) -> str:
    """Get detailed project profitability analysis using the processor for accurate project names"""
    try:
        print("🚀 PROCESSOR-BASED ANALYSIS STARTING! 🚀", flush=True)
        
        # Get insights data using the processor approach
        insights_data = await admin_server_instance.reports_api.get_insights_profitability(
            workspace_id, start_date, end_date, "projects"
        )
        
        print(f"✅ Got insights data successfully", flush=True)
        
        # Get workspace info for currency
        workspace_info = await admin_server_instance.get_workspace_info(workspace_id)
        # Handle both dict and object cases
        if hasattr(workspace_info, 'default_currency'):
            currency = workspace_info.default_currency
        elif isinstance(workspace_info, dict):
            currency = workspace_info.get('default_currency', 'USD')
        else:
            currency = 'USD'
        
        # Use the processor to get proper project data with actual employee rates
        projects = await admin_server_instance.processor.process_project_profitability(
            insights_data, 
            currency, 
            workspace_id, 
            admin_server_instance.reports_api
        )
        
        print(f"Received {len(projects)} valid ProjectProfitability objects from processor")
        
        # Filter by minimum hours
        if min_hours > 0:
            filtered_projects = []
            for p in projects:
                try:
                    if hasattr(p, 'total_hours'):
                        hours = float(p.total_hours or 0)
                    elif isinstance(p, dict):
                        hours = float(p.get('total_hours', 0))
                    else:
                        continue
                        
                    if hours >= min_hours:
                        filtered_projects.append(p)
                except Exception as e:
                    print(f"Error filtering project: {str(e)}", flush=True)
                    continue
                    
            projects = filtered_projects
            print(f"After min_hours filter ({min_hours}h): {len(projects)} projects")
        
        # Sort by specified criterion
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
            elif sort_by == "margin":
                projects.sort(key=lambda p: safe_sort_key(p, 'profit_margin'), reverse=True)
            elif sort_by == "hours":
                projects.sort(key=lambda p: safe_sort_key(p, 'total_hours'), reverse=True)
            # Default is already sorted by profit
        except Exception as e:
            print(f"Error sorting projects by {sort_by}: {str(e)}", flush=True)
        
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
        
        # Add summary stats
        total_revenue = sum(p.revenue for p in projects)
        total_profit = sum(p.profit for p in projects)
        total_hours = sum(p.total_hours for p in projects)
        
        result += f"""
📊 **SUMMARY STATISTICS**
• Total Revenue: {currency} {total_revenue:,.2f}
• Total Profit: {currency} {total_profit:,.2f}
• Total Hours: {total_hours:.1f}h
• Average Profit Margin: {(total_profit / total_revenue * 100) if total_revenue > 0 else 0:.1f}%
"""
        
        return result
        
    except Exception as e:
        return f"Failed to get project profitability analysis: {str(e)}"

if __name__ == "__main__":
    asyncio.run(main())
