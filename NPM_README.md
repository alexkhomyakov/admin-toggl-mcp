# @akhomyakov/server-toggl

A Model Context Protocol (MCP) server for Toggl time tracking with advanced admin-level reporting capabilities.

## Installation

```bash
npm install -g @akhomyakov/server-toggl
```

## Usage

### Prerequisites

1. **Python 3.8+**: This package requires Python to be installed on your system
2. **Toggl API Token**: Get your API token from [Toggl Profile](https://track.toggl.com/profile)

### Environment Setup

Set your Toggl API token as an environment variable:

```bash
export TOGGL_API_TOKEN="your_toggl_api_token_here"
```

### Running the Server

```bash
mcp-server-toggl
```

Or use it directly with Claude Desktop by adding to your config:

```json
{
  "mcpServers": {
    "toggl": {
      "command": "npx",
      "args": ["-y", "@akhomyakov/server-toggl"],
      "env": {
        "TOGGL_API_TOKEN": "your_toggl_api_token_here"
      }
    }
  }
}
```

## Features

- **Time Tracking**: Start and stop time entries
- **Workspace Management**: List and manage workspaces
- **Advanced Analytics**: 
  - Organization dashboard with KPIs
  - Project profitability analysis
  - Team productivity reports
  - Client profitability analysis
  - Financial summaries
  - Productivity insights

## Tools Available

- `start_tracking` - Start tracking time for a new task
- `stop_tracking` - Stop the currently running time entry
- `show_current_time_entry` - Show the currently running time entry
- `list_workspaces` - List all available workspaces
- `get_organization_dashboard` - Get comprehensive organization dashboard
- `get_project_profitability_analysis` - Get detailed project profitability analysis
- `get_team_productivity_report` - Get team productivity report
- `get_client_profitability_analysis` - Get client-level profitability analysis
- `get_financial_summary` - Get high-level financial summary
- `get_productivity_insights` - Get advanced productivity insights

## Development

To build from source:

```bash
git clone https://github.com/alexkhomyakov/admin-toggl-mcp
cd admin-toggl-mcp
npm install
npm run build
```

## License

MIT
