#!/usr/bin/env python3
"""
Lazy Toggl MCP Server

A Model Context Protocol server that provides tools for interacting with Toggl time tracking:
- start_tracking: Start a new time entry
- stop_tracking: Stop the currently running time entry
- list_workspaces: List all available workspaces
- show_current_time_entry: Show the currently running time entry, if any
"""

import asyncio
from typing import Any, Dict, List

from mcp.server import Server, InitializationOptions, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from toggl_server.toggl_api import TogglAPI
from toggl_server.utils import format_duration

class LazyTogglMCPServer:
    def __init__(self):
        self.server = Server("toggl-mcp-server")
        self.toggl_api = TogglAPI()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Set up the MCP server request handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="start_tracking",
                    description="Start tracking time for a new task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title/description of the task to track",
                            },
                            "workspace_id": {
                                "type": "integer",
                                "description": "Workspace ID (optional, uses default if not provided)",
                            },
                            "project_id": {
                                "type": "integer",
                                "description": "Project ID (optional)",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of tags (optional)",
                            },
                        },
                        "required": ["title"],
                    },
                ),
                Tool(
                    name="stop_tracking",
                    description="Stop the currently running time entry",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="list_workspaces",
                    description="List all available workspaces",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="show_current_time_entry",
                    description="Show the currently running time entry, if any",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[TextContent]:
            """Handle tool execution requests."""
            
            if name == "start_tracking":
                return await self._handle_start_tracking(arguments)
            elif name == "stop_tracking":
                return await self._handle_stop_tracking(arguments)
            elif name == "list_workspaces":
                return await self._handle_list_workspaces(arguments)
            elif name == "show_current_time_entry":
                return await self._handle_show_current_time_entry(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _handle_start_tracking(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle starting time tracking."""
        try:
            title = arguments["title"]
            workspace_id = arguments.get("workspace_id")
            project_id = arguments.get("project_id")
            tags = arguments.get("tags", [])
            
            # Check if there's already a running time entry
            current_entry = await self.toggl_api.get_current_time_entry()
            if current_entry:
                return [
                    TextContent(
                        type="text",
                        text=f"⚠️  There's already a running time entry: '{current_entry.description}'\n"
                             f"Please stop it first before starting a new one.",
                    )
                ]
            
            # Get default workspace if not provided
            if workspace_id is None:
                user_info = await self.toggl_api.get_user_info()
                workspace_id = user_info["default_workspace_id"]
            
            # Start the new time entry
            time_entry = await self.toggl_api.start_time_entry(
                title=title,
                workspace_id=workspace_id,
                project_id=project_id,
                tags=tags,
            )
            
            return [
                TextContent(
                    type="text",
                    text=f"✅ Started tracking: '{time_entry.description}'\n"
                         f"🆔 Entry ID: {time_entry.id}\n"
                         f"🏢 Workspace: {workspace_id}\n"
                         f"🕐 Started at: {time_entry.start}",
                )
            ]
            
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error starting time tracking: {str(e)}",
                )
            ]

    async def _handle_stop_tracking(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle stopping time tracking."""
        try:
            # Get current running time entry
            current_entry = await self.toggl_api.get_current_time_entry()
            if not current_entry:
                return [
                    TextContent(
                        type="text",
                        text="ℹ️  No time entry is currently running.",
                    )
                ]
            
            # Stop the time entry
            stopped_entry = await self.toggl_api.stop_time_entry(
                workspace_id=current_entry.workspace_id,
                time_entry_id=current_entry.id,
            )
            
            # Calculate duration
            duration_str = format_duration(stopped_entry.duration)
            
            return [
                TextContent(
                    type="text",
                    text=f"⏹️  Stopped tracking: '{stopped_entry.description}'\n"
                         f"⏱️  Duration: {duration_str}\n"
                         f"🕐 Stopped at: {stopped_entry.stop}",
                )
            ]
            
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error stopping time tracking: {str(e)}",
                )
            ]

    async def _handle_list_workspaces(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle listing workspaces."""
        try:
            workspaces = await self.toggl_api.get_workspaces()
            
            if not workspaces:
                return [
                    TextContent(
                        type="text",
                        text="No workspaces found.",
                    )
                ]
            
            # Format workspace list
            workspace_list = "📁 **Available Workspaces:**\n\n"
            for workspace in workspaces:
                workspace_list += f"• **{workspace.name}** (ID: {workspace.id})\n"
                if workspace.premium:
                    workspace_list += "  🌟 Premium workspace\n"
            
            return [
                TextContent(
                    type="text",
                    text=workspace_list,
                )
            ]
            
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error listing workspaces: {str(e)}",
                )
            ]

    async def _handle_show_current_time_entry(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle showing the current time entry."""
        try:
            # Get current running time entry
            current_entry = await self.toggl_api.get_current_time_entry()
            
            if not current_entry:
                return [
                    TextContent(
                        type="text",
                        text="⏸️ No time entry is currently running",
                    )
                ]
            
            # Calculate running duration
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            running_seconds = int((now - current_entry.start).total_seconds())
            duration_str = format_duration(running_seconds)
            
            # Format the current entry information
            entry_info = f"✅ Currently tracking time entry\n"
            entry_info += f"📝 Task: '{current_entry.description}'\n"
            entry_info += f"🆔 Entry ID: {current_entry.id}\n"
            entry_info += f"🏢 Workspace ID: {current_entry.workspace_id}\n"
            entry_info += f"🕐 Started: {current_entry.start}\n"
            entry_info += f"⏱️ Running for: {duration_str}"
            
            # Add tags if present
            if current_entry.tags:
                entry_info += f"\n🏷️ Tags: {', '.join(current_entry.tags)}"
            
            # Add project if present
            if current_entry.project_id:
                entry_info += f"\n📁 Project ID: {current_entry.project_id}"
            
            return [
                TextContent(
                    type="text",
                    text=entry_info,
                )
            ]
            
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error getting current time entry: {str(e)}",
                )
            ]

    async def run(self):
        """Run the MCP server using stdio transport."""
        async with stdio_server() as streams:
            await self.server.run(
                streams[0], 
                streams[1],
                InitializationOptions(
                    server_name="toggl-mcp-server",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    """Main entry point for the MCP server."""
    server = LazyTogglMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
