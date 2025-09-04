#!/usr/bin/env python3
"""
MCP server with standard MCP protocol compliance
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict


def main():
    """Start MCP server with standard protocol compliance"""
    try:
        from mcp.server.fastmcp import FastMCP
        from mcp.types import TextContent, Tool

        print("🚀 Standard MCP Server")
        print("Following MCP protocol specification...")

        # Create server
        server = FastMCP("code-implementation")

        @server.tool()
        async def set_workspace(workspace_path: str) -> str:
            """Set workspace directory for code implementation"""
            try:
                workspace = Path(workspace_path).resolve()
                workspace.mkdir(parents=True, exist_ok=True)

                result = {
                    "status": "success",
                    "message": f"Workspace set successfully: {workspace_path}",
                    "workspace_path": str(workspace)
                }
                return json.dumps(result, ensure_ascii=False, indent=2)
            except Exception as e:
                result = {
                    "status": "error",
                    "message": f"Failed to set workspace: {str(e)}"
                }
                return json.dumps(result, ensure_ascii=False, indent=2)

        print("Tools registered successfully:")
        print("  • set_workspace")
        print("")
        print("🔧 Starting MCP server...")

        # Start the server
        server.run()

    except ImportError as import_err:
        print(f"❌ Import error: {import_err}")
        # Try alternative import
        try:
            from mcp.server.fastmcp import FastMCP
            print("Fallback: Using basic FastMCP import...")

            server = FastMCP("code-implementation")

            @server.tool()
            async def set_workspace(workspace_path: str) -> str:
                """Set workspace directory"""
                workspace = Path(workspace_path).resolve()
                workspace.mkdir(parents=True, exist_ok=True)
                return json.dumps({
                    "status": "success",
                    "workspace": str(workspace)
                })

            print("Fallback server starting...")
            server.run()

        except Exception as fallback_err:
            print(f"❌ Fallback failed: {fallback_err}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
