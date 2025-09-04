#!/usr/bin/env python3
"""
Debug MCP server with connection monitoring
"""

import asyncio
import json
import sys
import time
from pathlib import Path


def main():
    """Start debug MCP server with connection monitoring"""
    try:
        print("🐛 Debug MCP Server")
        print("="*50)
        print(f"Python version: {sys.version}")
        print(f"Current working directory: {Path.cwd()}")
        print(f"Script location: {Path(__file__).resolve()}")
        print("="*50)

        from mcp.server.fastmcp import FastMCP
        print("✅ FastMCP imported successfully")

        # Create server
        server = FastMCP("code-implementation")
        print("✅ FastMCP server instance created")

        # Tool registration with detailed logging
        @server.tool()
        async def set_workspace(workspace_path: str) -> str:
            """Set workspace directory - debug version"""
            print(f"🔧 set_workspace called with: {workspace_path}")
            try:
                workspace = Path(workspace_path).resolve()
                workspace.mkdir(parents=True, exist_ok=True)

                result = {
                    "status": "success",
                    "message": f"Workspace set successfully: {workspace_path}",
                    "workspace_path": str(workspace),
                    "debug_info": {
                        "server_name": "debug-mcp-server",
                        "timestamp": time.time(),
                        "tool": "set_workspace"
                    }
                }
                print(f"✅ set_workspace completed: {workspace}")
                return json.dumps(result, ensure_ascii=False, indent=2)

            except Exception as e:
                print(f"❌ set_workspace error: {e}")
                result = {
                    "status": "error",
                    "message": f"Failed to set workspace: {str(e)}",
                    "error_type": type(e).__name__
                }
                return json.dumps(result, ensure_ascii=False, indent=2)

        @server.tool()
        async def debug_connection() -> str:
            """Test connection and return debug information"""
            print("🔍 debug_connection called")
            result = {
                "status": "success",
                "message": "Connection is working",
                "debug_info": {
                    "server_alive": True,
                    "timestamp": time.time(),
                    "python_version": sys.version,
                    "cwd": str(Path.cwd())
                }
            }
            print("✅ debug_connection completed")
            return json.dumps(result, ensure_ascii=False, indent=2)

        print("✅ Tools registered:")
        print("  • set_workspace - Set workspace directory")
        print("  • debug_connection - Test connection")
        print("")
        print("🚀 Starting server...")
        print("   (Server will print messages when tools are called)")
        print("   (Press Ctrl+C to stop)")
        print("")

        # Add some startup delay to ensure everything is ready
        print("⏳ Initializing (3 seconds)...")
        time.sleep(3)
        print("🎯 Server ready for connections!")

        # Start server with connection monitoring
        try:
            server.run()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"\n❌ Server runtime error: {e}")
            import traceback
            traceback.print_exc()
            raise

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
