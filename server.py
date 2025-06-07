#!/usr/bin/env python3
"""
Lazy Toggl MCP Server - Standalone Entry Point

A Model Context Protocol server that provides tools for interacting with Toggl time tracking:
- start_tracking: Start a new time entry
- stop_tracking: Stop the currently running time entry
- list_workspaces: List all available workspaces
- show_current_time_entry: Show the currently running time entry, if any
"""

import asyncio

from src.toggl_server.main import main

if __name__ == "__main__":
    asyncio.run(main())
