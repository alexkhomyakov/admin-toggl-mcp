# Admin Toggl MCP Server

A Model Context Protocol (MCP) server for Toggl time tracking with advanced admin-level reporting capabilities.

## Features

### Basic Time Tracking
- Start time tracking for tasks
- Stop currently running time entries
- View current time entry
- List available workspaces

### Advanced Admin Reporting
- Organization dashboard with KPIs
- Project profitability analysis
- Team productivity reports
- Client profitability analysis
- Financial summaries
- Productivity insights

## Installation

### Prerequisites
- Python 3.12 or higher
- Toggl API token

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd admin-toggl-mcp
   ```

2. **Install dependencies**
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env
   
   # Install project dependencies
   uv sync
   ```

3. **Get your Toggl API token**
   - Go to [Toggl Track](https://track.toggl.com/profile)
   - Scroll down to "API Token"
   - Copy your token

4. **Set environment variable**
   ```bash
   export TOGGL_API_TOKEN='your_api_token_here'
   ```

## Usage

### Running the Server

```bash
# Run the server
uv run python server.py

# Or run with help
uv run python server.py --help
```

### Testing the Setup

```bash
# Run the test suite to verify everything is working
uv run python test_server.py
```

## API Reference

### Basic Tools

#### `start_tracking`
Start tracking time for a new task.

**Parameters:**
- `title` (string, required): Title/description of the task
- `workspace_id` (integer, optional): Workspace ID
- `project_id` (integer, optional): Project ID
- `tags` (array of strings, optional): List of tags

#### `stop_tracking`
Stop the currently running time entry.

#### `show_current_time_entry`
Show the currently running time entry, if any.

#### `list_workspaces`
List all available workspaces.

### Admin Tools

#### `get_organization_dashboard`
Get comprehensive organization dashboard with KPIs, hours, revenue, and profit metrics.

**Parameters:**
- `workspace_id` (integer, required): Workspace ID
- `start_date` (string, optional): Start date (YYYY-MM-DD)
- `end_date` (string, optional): End date (YYYY-MM-DD)
- `period` (string, optional): Predefined period (week, month, quarter, year)

#### `get_project_profitability_analysis`
Get detailed project profitability analysis with profit margins, utilization rates, and ROI.

**Parameters:**
- `workspace_id` (integer, required): Workspace ID
- `start_date` (string, optional): Start date (YYYY-MM-DD)
- `end_date` (string, optional): End date (YYYY-MM-DD)
- `sort_by` (string, optional): Sort criterion (profit, revenue, margin, hours)
- `min_hours` (number, optional): Minimum hours threshold for inclusion

#### `get_team_productivity_report`
Get team productivity report with utilization rates, performance metrics, and capacity analysis.

**Parameters:**
- `workspace_id` (integer, required): Workspace ID
- `start_date` (string, optional): Start date (YYYY-MM-DD)
- `end_date` (string, optional): End date (YYYY-MM-DD)
- `include_individual_metrics` (boolean, optional): Include individual employee metrics

#### `get_client_profitability_analysis`
Get client-level profitability and revenue analysis.

**Parameters:**
- `workspace_id` (integer, required): Workspace ID
- `start_date` (string, optional): Start date (YYYY-MM-DD)
- `end_date` (string, optional): End date (YYYY-MM-DD)
- `min_revenue` (number, optional): Minimum revenue threshold

#### `get_financial_summary`
Get high-level financial summary with revenue, costs, and profit trends.

**Parameters:**
- `workspace_id` (integer, required): Workspace ID
- `period` (string, optional): Period for analysis (month, quarter, year)
- `compare_previous` (boolean, optional): Include comparison with previous period

#### `get_productivity_insights`
Get advanced productivity insights and time tracking patterns.

**Parameters:**
- `workspace_id` (integer, required): Workspace ID
- `start_date` (string, optional): Start date (YYYY-MM-DD)
- `end_date` (string, optional): End date (YYYY-MM-DD)
- `include_detailed_analysis` (boolean, optional): Include detailed time entry analysis

## Architecture

### Core Components

- **`main.py`**: Main server implementation with MCP protocol handlers
- **`toggl_api.py`**: Toggl Track API client for basic operations
- **`reports_api.py`**: Toggl Reports API client for advanced analytics
- **`models.py`**: Data models for workspaces, time entries, and reports
- **`admin_processor.py`**: Data processing for admin-level reports
- **`utils.py`**: Utility functions for data parsing and formatting

### Data Models

- **`TogglWorkspace`**: Workspace information
- **`TogglTimeEntry`**: Time entry data
- **`ProjectProfitability`**: Project-level profitability metrics
- **`EmployeeProfitability`**: Employee productivity metrics
- **`ClientProfitability`**: Client-level profitability analysis
- **`OrganizationSummary`**: High-level organization KPIs

## Error Handling

The server includes comprehensive error handling for:
- Network connectivity issues
- API rate limiting
- Authentication failures
- Invalid data formats
- Missing required fields

## Development

### Project Structure
```
admin-toggl-mcp/
├── src/
│   └── toggl_server/
│       ├── __init__.py
│       ├── main.py
│       ├── toggl_api.py
│       ├── reports_api.py
│       ├── admin_processor.py
│       ├── models.py
│       └── utils.py
├── server.py
├── test_server.py
├── pyproject.toml
└── README.md
```

### Running Tests
```bash
uv run python test_server.py
```

### Adding New Features
1. Add new tools to the `handle_list_tools()` function in `main.py`
2. Implement tool handlers in `handle_call_tool()`
3. Add corresponding data models in `models.py` if needed
4. Update the test suite in `test_server.py`

## Troubleshooting

### Common Issues

1. **"TOGGL_API_TOKEN environment variable is required"**
   - Make sure you've set the environment variable correctly
   - Verify your API token is valid

2. **"Authentication failed"**
   - Check that your API token is correct
   - Ensure your Toggl account is active

3. **"Rate limit exceeded"**
   - Wait a moment before making more requests
   - The server automatically handles rate limiting

4. **Import errors**
   - Run `uv sync` to ensure all dependencies are installed
   - Check that you're using Python 3.12 or higher

### Getting Help

If you encounter issues:
1. Run the test suite: `uv run python test_server.py`
2. Check the logs for detailed error messages
3. Verify your Toggl API token is working with a simple curl request

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
