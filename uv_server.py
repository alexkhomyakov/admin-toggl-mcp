#!/usr/bin/env python3
"""
UV wrapper for Toggl MCP Server
"""

import sys
import os
import subprocess

# Set up environment
os.environ.setdefault('TOGGL_API_TOKEN', '8d2d6c77d4863189fd550c22992ded5c')

def main():
    """Run the server using uv"""
    try:
        # Use the full path to uv
        uv_path = os.path.expanduser('~/.local/bin/uv')
        if not os.path.exists(uv_path):
            print(f"Error: uv not found at {uv_path}", file=sys.stderr)
            print("Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh", file=sys.stderr)
            sys.exit(1)
            
        # Run with uv
        result = subprocess.run([
            uv_path, 'run', '--directory', os.path.dirname(__file__),
            'python', 'server.py'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            sys.exit(result.returncode)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
