#!/usr/bin/env python3
"""
Minimal MCP server to eliminate any potential issues
"""

import json
import sys
from pathlib import Path


async def handle_set_workspace(workspace_path: str) -> str:
    """Handle set_workspace tool call"""
    try:
        workspace = Path(workspace_path).resolve()
        workspace.mkdir(parents=True, exist_ok=True)

        result = {
            "status": "success",
            "message": f"Workspace set to: {workspace_path}",
            "workspace_path": str(workspace)
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        result = {
            "status": "error",
            "message": f"Failed to set workspace: {str(e)}"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

def main():
    """Start minimal MCP server"""
    try:
        print("🔬 Minimal MCP Server")
        print("Importing MCP...")

        from mcp.server.fastmcp import FastMCP
        print("✅ MCP imported")

        print("Creating server...")
        mcp = FastMCP("code-implementation")
        print("✅ Server created")

        print("Registering tools...")

        @mcp.tool()
        async def set_workspace(workspace_path: str) -> str:
            """Set workspace directory"""
            return await handle_set_workspace(workspace_path)

        print("✅ Tools registered")
        print("Available tools:")
        print("  • set_workspace")
        print("")
        print("🚀 Starting server (this may take a moment)...")

        # Start server
        mcp.run()

    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
