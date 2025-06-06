# Lazy Toggl MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with Toggl time tracking.

## Features

This MCP server provides three main tools:

1. **`start_tracking`** - Start tracking time for a new task
2. **`stop_tracking`** - Stop the currently running time entry
3. **`list_workspaces`** - List all available workspaces

## Installation

1. Clone/create this project
2. Install dependencies with `uv`:
   ```bash
   cd lazy-toggl-mcp
   uv sync
   ```

## Configuration

### Get Your Toggl API Token

1. Go to [Toggl Track](https://track.toggl.com/)
2. Sign in to your account
3. Click on your profile picture/avatar in the top right corner
4. Go to "Profile" or "Settings"
5. Find your "API Token" - copy this long string of characters

### Configure MCP Server

Add the following configuration to your MCP settings file:

```json
{
  "mcpServers": {
    "lazy-toggl-mcp": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "transportType": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/lazy-toggl-mcp",
        "python",
        "server.py"
      ],
      "env": {
        "TOGGL_API_TOKEN": "your-actual-api-token-here"
      }
    }
  }
}
```

**Important**: Replace `/path/to/lazy-toggl-mcp` with the actual path to this project and `your-actual-api-token-here` with your real Toggl API token.

## Usage

Once configured, you can use the following commands with your MCP client:

### Start Tracking
```
start_tracking title="Working on project documentation"
```

With optional parameters:
```
start_tracking title="Bug fix" workspace_id=12345 project_id=67890 tags=["development", "bug-fix"]
```

### Stop Tracking
```
stop_tracking
```

### List Workspaces
```
list_workspaces
```

## API Integration

This server uses the Toggl Track API v9. The following endpoints are utilized:

- `GET /me` - Get user information
- `GET /workspaces` - List workspaces
- `GET /me/time_entries/current` - Get current running time entry
- `POST /workspaces/{workspace_id}/time_entries` - Start time tracking
- `PATCH /workspaces/{workspace_id}/time_entries/{time_entry_id}/stop` - Stop time tracking

## Error Handling

The server includes comprehensive error handling for:
- Invalid API tokens
- Rate limiting
- Network errors
- Missing or invalid time entries

## Development

To modify the server:

1. Edit the source files in `src/toggl_server/`
2. Reinstall the package: `uv pip install -e .`
3. Restart your MCP client to reload the server

## Project Structure

```
lazy-toggl-mcp/
├── src/
│   └── toggl_server/
│       ├── __init__.py      # Package initialization
│       ├── main.py          # MCP server implementation (new structure)
│       ├── models.py        # Data models and type definitions
│       ├── toggl_api.py     # Toggl API client
│       └── utils.py         # Utility functions
├── main.py                  # CLI interface for testing
├── server.py                # Main MCP server entry point
├── pyproject.toml           # Project configuration and dependencies
├── README.md                # This file
├── uv.lock                  # Dependency lock file
├── .gitignore               # Git ignore patterns
└── .python-version          # Python version specification
```

## License

MIT License - feel free to modify and use as needed.
