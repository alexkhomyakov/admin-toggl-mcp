#!/usr/bin/env python3
"""
Standalone Toggl MCP Server - Can run without uv
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up environment
os.environ.setdefault('TOGGL_API_TOKEN', '8d2d6c77d4863189fd550c22992ded5c')

try:
    from toggl_server.main import main
    import asyncio
    
    if __name__ == "__main__":
        asyncio.run(main())
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    print("Please install dependencies: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
