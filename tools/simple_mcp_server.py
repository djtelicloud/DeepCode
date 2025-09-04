#!/usr/bin/env python3
"""
Simplified MCP server implementation to isolate the issue
"""

import asyncio
import json
import sys
from pathlib import Path

# Try different MCP approaches
try:
    # First try FastMCP
    from mcp.server.fastmcp import FastMCP
    print("Using FastMCP implementation")

    mcp = FastMCP("code-implementation-simple")

    @mcp.tool()
    async def set_workspace(workspace_path: str) -> str:
        """Set workspace directory"""
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

    @mcp.tool()
    async def test_connection() -> str:
        """Test MCP connection"""
        result = {
            "status": "success",
            "message": "MCP server is running correctly",
            "server_type": "simplified"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    def main():
        print("🚀 Simplified MCP Server")
        print("Available tools:")
        print("  • set_workspace")
        print("  • test_connection")
        print("🔧 Starting server...")

        try:
            mcp.run()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Server error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

except ImportError as e:
    print(f"❌ Could not import FastMCP: {e}")
    sys.exit(1)

if __name__ == "__main__":
    main()
