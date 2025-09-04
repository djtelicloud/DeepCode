#!/usr/bin/env python3
"""
MCP server with explicit tool registration following MCP spec
"""

import json
import sys
from pathlib import Path


def main():
    """Start MCP server with explicit tool registration"""
    try:
        from mcp.server.fastmcp import FastMCP

        print("🚀 Explicit MCP Server")
        print("Initializing server...")

        # Create server with explicit name
        server = FastMCP("code-implementation")

        # Define tools with explicit typing and descriptions
        @server.tool()
        async def set_workspace(workspace_path: str) -> str:
            """
            Set workspace directory for code implementation.

            Args:
                workspace_path: Path to the workspace directory

            Returns:
                JSON string containing operation result
            """
            try:
                workspace = Path(workspace_path).resolve()
                workspace.mkdir(parents=True, exist_ok=True)

                result = {
                    "status": "success",
                    "message": f"Workspace set successfully: {workspace_path}",
                    "workspace_path": str(workspace),
                    "tool_name": "set_workspace",
                    "tool_version": "1.0"
                }
                return json.dumps(result, ensure_ascii=False, indent=2)
            except Exception as e:
                result = {
                    "status": "error",
                    "message": f"Failed to set workspace: {str(e)}",
                    "tool_name": "set_workspace",
                    "error_type": type(e).__name__
                }
                return json.dumps(result, ensure_ascii=False, indent=2)

        @server.tool()
        async def get_server_info() -> str:
            """
            Get server information and available tools.

            Returns:
                JSON string containing server information
            """
            result = {
                "status": "success",
                "server_name": "code-implementation",
                "server_version": "1.0",
                "available_tools": ["set_workspace", "get_server_info"],
                "message": "Server is running correctly"
            }
            return json.dumps(result, ensure_ascii=False, indent=2)

        print("Tools registered:")
        print("  • set_workspace - Set workspace directory")
        print("  • get_server_info - Get server information")
        print("")
        print("🔧 Starting server...")

        # Start the server
        server.run()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
