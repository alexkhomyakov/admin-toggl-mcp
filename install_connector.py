#!/usr/bin/env python3
"""
Installation script for the Toggl Claude Connector

This script helps users set up the connector by checking dependencies and providing setup instructions.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 12):
        print("❌ Python 3.12 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "httpx",
        "mcp",
        "pydantic",
        "python-dateutil"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} (missing)")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("   Please run: pip install -r requirements.txt")
            return False
    
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        "connector.json",
        "connector.py",
        "requirements.txt",
        "src/toggl_server/__init__.py",
        "src/toggl_server/main.py",
        "src/toggl_server/toggl_api.py",
        "src/toggl_server/reports_api.py",
        "src/toggl_server/models.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} (missing)")
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    return True

def get_api_token():
    """Get API token from user"""
    print("\n🔑 Toggl API Token Setup")
    print("=" * 50)
    print("To use this connector, you need a Toggl API token.")
    print("\nTo get your API token:")
    print("1. Go to https://track.toggl.com/profile")
    print("2. Scroll down to 'API Token'")
    print("3. Copy your token")
    print("\nEnter your API token (or press Enter to skip for now):")
    
    token = input("API Token: ").strip()
    
    if token:
        # Save to .env file
        with open(".env", "w") as f:
            f.write(f"TOGGL_API_TOKEN={token}\n")
        print("✅ API token saved to .env file")
        return token
    else:
        print("⚠️  No API token provided. You can set it later in Claude Desktop.")
        return None

def print_installation_instructions():
    """Print installation instructions for Claude Desktop"""
    print("\n📱 Claude Desktop Installation")
    print("=" * 50)
    print("To install this connector in Claude Desktop:")
    print("\n1. Open Claude Desktop")
    print("2. Go to Settings → Connectors")
    print("3. Click 'Add Connector'")
    print("4. Select 'Local Connector'")
    print("5. Choose this directory as the connector location")
    print("6. Set the environment variable:")
    print("   - Name: TOGGL_API_TOKEN")
    print("   - Value: Your Toggl API token")
    print("   - Check 'Secret' to keep it secure")
    print("\n7. The connector should appear in your connectors list")
    print("8. Status should show as 'Connected'")
    print("\n🎉 You can now use Toggl tools in your conversations!")

def main():
    """Main installation function"""
    print("🚀 Toggl Claude Connector Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check files
    if not check_files():
        return False
    
    # Get API token
    api_token = get_api_token()
    
    # Test the connector
    print("\n🧪 Testing connector...")
    try:
        result = subprocess.run([
            sys.executable, "test_connector.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Connector test passed")
        else:
            print("⚠️  Connector test failed, but installation may still work")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Could not test connector: {e}")
    
    # Print installation instructions
    print_installation_instructions()
    
    print("\n🎉 Installation completed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
