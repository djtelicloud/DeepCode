#!/usr/bin/env python3
"""
Debug version of code implementation server with enhanced error reporting
"""

import os
import sys
import traceback
from pathlib import Path


def debug_environment():
    """Print debug information about the environment"""
    print("=== DEBUG INFORMATION ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"Script location: {os.path.abspath(__file__)}")
    print("=========================")

def main():
    """Start MCP server with debug info"""
    try:
        debug_environment()

        # Add the project root to sys.path
        project_root = Path(__file__).parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        print("Importing FastMCP...")
        from mcp.server.fastmcp import FastMCP

        print("Creating MCP server instance...")
        mcp = FastMCP("code-implementation-server-debug")

        @mcp.tool()
        async def set_workspace(workspace_path: str) -> str:
            """Set workspace directory (debug version)"""
            import json
            result = {
                "status": "success",
                "message": f"Workspace set to: {workspace_path}",
                "workspace_path": workspace_path,
                "debug": True
            }
            return json.dumps(result, ensure_ascii=False, indent=2)

        @mcp.tool()
        async def debug_info() -> str:
            """Get debug information"""
            import json
            info = {
                "cwd": os.getcwd(),
                "python_executable": sys.executable,
                "python_version": sys.version,
                "pythonpath": os.environ.get('PYTHONPATH', 'Not set')
            }
            return json.dumps(info, ensure_ascii=False, indent=2)

        print("🚀 Debug Code Implementation MCP Server")
        print("📝 Debug version with enhanced error reporting")
        print("")
        print("Available tools:")
        print("  • set_workspace - Set workspace directory")
        print("  • debug_info - Get debug information")
        print("")
        print("🔧 Server starting...")

        # Start server
        mcp.run()

    except Exception as e:
        print(f"❌ Fatal error starting server: {e}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
