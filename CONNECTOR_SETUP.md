# Quick Setup Guide: Toggl Claude Connector

## 🚀 Quick Start

1. **Run the installation script:**
   ```bash
   python3 install_connector.py
   ```

2. **Get your Toggl API token:**
   - Go to [Toggl Track Profile](https://track.toggl.com/profile)
   - Copy your API token

3. **Install in Claude Desktop:**
   - Open Claude Desktop
   - Settings → Connectors → Add Connector → Local Connector
   - Choose this directory
   - Set environment variable: `TOGGL_API_TOKEN` = your token (mark as secret)

## ✅ What's Included

- **10 powerful tools** for time tracking and analytics
- **Basic time tracking**: start/stop tracking, view current entry, list workspaces
- **Advanced analytics**: organization dashboard, project profitability, team reports, financial summaries
- **Secure**: API token stored as secret environment variable
- **Tested**: Includes test scripts and installation verification

## 🛠️ Files Created

- `connector.json` - Claude Connector configuration
- `connector.py` - Main connector entry point
- `test_connector.py` - Test script to verify functionality
- `install_connector.py` - Automated installation helper
- `CONNECTOR_README.md` - Comprehensive documentation
- `.gitignore` - Git ignore file for security

## 🎯 Ready to Use

Your MCP server is now converted to a Claude Connector! Users can:

1. Run `python3 install_connector.py` for guided setup
2. Install directly in Claude Desktop as a local connector
3. Use all 10 Toggl tools in their conversations

The connector maintains all the advanced admin-level reporting capabilities while providing a seamless Claude Desktop experience.
