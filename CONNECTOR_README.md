# Toggl Claude Connector

A Claude Connector for Toggl time tracking with advanced admin-level reporting capabilities. This connector provides tools for time tracking, project management, and detailed analytics directly within Claude Desktop.

## Features

### Basic Time Tracking
- **Start tracking time** for tasks with optional workspace, project, and tags
- **Stop currently running** time entries
- **View current time entry** status
- **List available workspaces** for easy navigation

### Advanced Admin Reporting
- **Organization dashboard** with KPIs, hours, revenue, and profit metrics
- **Project profitability analysis** with profit margins, utilization rates, and ROI
- **Team productivity reports** with utilization rates and performance metrics
- **Client profitability analysis** for client-level insights
- **Financial summaries** with revenue, costs, and profit trends
- **Productivity insights** and time tracking patterns

## Installation

### Prerequisites
- Claude Desktop application
- Toggl API token

### Setup Steps

1. **Get your Toggl API token**
   - Go to [Toggl Track Profile](https://track.toggl.com/profile)
   - Scroll down to "API Token"
   - Copy your token

2. **Install the connector in Claude Desktop**
   - Open Claude Desktop
   - Go to Settings → Connectors
   - Click "Add Connector"
   - Select "Local Connector"
   - Choose this directory as the connector location
   - Set the environment variable:
     - Name: `TOGGL_API_TOKEN`
     - Value: Your Toggl API token
     - Check "Secret" to keep it secure

3. **Verify installation**
   - The connector should appear in your connectors list
   - Status should show as "Connected"
   - You can now use Toggl tools in your conversations

## Usage

Once installed, you can use the Toggl connector in your Claude conversations. Here are some example prompts:

### Basic Time Tracking
```
"Start tracking time for 'Review quarterly reports'"
"Stop my current time tracking"
"What am I currently working on?"
"Show me my available workspaces"
```

### Analytics and Reporting
```
"Get an organization dashboard for workspace 123456 for this month"
"Show me project profitability analysis for the last quarter"
"Generate a team productivity report for this week"
"Get financial summary for workspace 123456 comparing to last month"
```

### Advanced Analytics
```
"Analyze client profitability for the last 3 months"
"Get productivity insights for workspace 123456 with detailed analysis"
"Show me the top 5 most profitable projects this quarter"
```

## Tool Reference

### Basic Tools

#### `start_tracking`
Start tracking time for a new task.

**Parameters:**
- `title` (required): Title/description of the task
- `workspace_id` (optional): Workspace ID
- `project_id` (optional): Project ID
- `tags` (optional): List of tags

#### `stop_tracking`
Stop the currently running time entry.

#### `show_current_time_entry`
Show the currently running time entry, if any.

#### `list_workspaces`
List all available workspaces.

### Admin Analytics Tools

#### `get_organization_dashboard`
Get comprehensive organization dashboard with KPIs.

**Parameters:**
- `workspace_id` (required): Workspace ID
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `period` (optional): Predefined period (week, month, quarter, year)

#### `get_project_profitability_analysis`
Get detailed project profitability analysis.

**Parameters:**
- `workspace_id` (required): Workspace ID
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `sort_by` (optional): Sort criterion (profit, revenue, margin, hours)
- `min_hours` (optional): Minimum hours threshold

#### `get_team_productivity_report`
Get team productivity report with utilization rates.

**Parameters:**
- `workspace_id` (required): Workspace ID
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `include_individual_metrics` (optional): Include individual employee metrics

#### `get_client_profitability_analysis`
Get client-level profitability and revenue analysis.

**Parameters:**
- `workspace_id` (required): Workspace ID
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `min_revenue` (optional): Minimum revenue threshold

#### `get_financial_summary`
Get high-level financial summary with trends.

**Parameters:**
- `workspace_id` (required): Workspace ID
- `period` (optional): Period for analysis (month, quarter, year)
- `compare_previous` (optional): Include comparison with previous period

#### `get_productivity_insights`
Get advanced productivity insights and patterns.

**Parameters:**
- `workspace_id` (required): Workspace ID
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `include_detailed_analysis` (optional): Include detailed time entry analysis

## Troubleshooting

### Common Issues

1. **"Toggl API not initialized"**
   - Check that your `TOGGL_API_TOKEN` environment variable is set correctly
   - Verify your API token is valid by testing it with a simple API call
   - Restart Claude Desktop after setting the environment variable

2. **"Authentication failed"**
   - Ensure your Toggl API token is correct and not expired
   - Check that your Toggl account is active
   - Try regenerating your API token

3. **"Rate limit exceeded"**
   - Wait a moment before making more requests
   - The connector automatically handles rate limiting

4. **Connector not appearing**
   - Make sure you've selected the correct directory when adding the connector
   - Check that `connector.json` and `connector.py` are in the root directory
   - Restart Claude Desktop

5. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're using Python 3.12 or higher
   - Verify the `src/` directory structure is correct

### Getting Help

If you encounter issues:

1. **Check the logs** in Claude Desktop's developer console
2. **Verify your API token** with a simple curl request:
   ```bash
   curl -u YOUR_API_TOKEN:api_token https://api.track.toggl.com/api/v9/me
   ```
3. **Test the connector locally**:
   ```bash
   export TOGGL_API_TOKEN="your_token_here"
   python connector.py
   ```

## Development

### Project Structure
```
admin-toggl-mcp/
├── connector.json          # Claude Connector configuration
├── connector.py            # Main connector entry point
├── requirements.txt        # Python dependencies
├── src/
│   └── toggl_server/       # Core MCP server implementation
│       ├── __init__.py
│       ├── main.py         # Main server logic
│       ├── toggl_api.py    # Toggl Track API client
│       ├── reports_api.py  # Toggl Reports API client
│       ├── admin_processor.py
│       ├── models.py       # Data models
│       └── utils.py        # Utility functions
└── README.md              # Original MCP server documentation
```

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd admin-toggl-mcp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   export TOGGL_API_TOKEN="your_token_here"
   ```

4. **Test the connector**
   ```bash
   python connector.py
   ```

### Adding New Features

1. Add new tools to the `handle_list_tools()` function in `connector.py`
2. Implement tool handlers in `handle_call_tool()`
3. Update the `connector.json` file with new tool definitions
4. Test thoroughly before deploying

## Security

- Your Toggl API token is stored securely as a secret environment variable
- The connector only has access to the data your API token provides
- No data is stored locally beyond what's necessary for operation
- All API calls use HTTPS for secure communication

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues specific to the Claude Connector:
1. Check the troubleshooting section above
2. Review the Claude Desktop documentation
3. Open an issue in the repository

For Toggl API issues:
1. Check the [Toggl API documentation](https://github.com/toggl/toggl_api_docs)
2. Contact Toggl support if needed
