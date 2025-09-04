#!/usr/bin/env python3
"""
Robust MCP server with comprehensive error handling
"""

import asyncio
import json
import logging
import sys
import traceback
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start MCP server with comprehensive error handling"""
    try:
        logger.info("Starting robust MCP server...")

        # Import MCP components
        from mcp.server.fastmcp import FastMCP
        logger.info("FastMCP imported successfully")

        # Create server instance
        server = FastMCP("code-implementation")
        logger.info("FastMCP server instance created")

        # Define tools with comprehensive error handling
        @server.tool()
        async def set_workspace(workspace_path: str) -> str:
            """Set workspace directory for code implementation"""
            try:
                logger.info(f"set_workspace called with path: {workspace_path}")
                workspace = Path(workspace_path).resolve()
                workspace.mkdir(parents=True, exist_ok=True)
                logger.info(f"Workspace created/verified: {workspace}")

                result = {
                    "status": "success",
                    "message": f"Workspace set successfully: {workspace_path}",
                    "workspace_path": str(workspace)
                }
                logger.info("set_workspace completed successfully")
                return json.dumps(result, ensure_ascii=False, indent=2)

            except Exception as e:
                logger.error(f"Error in set_workspace: {e}", exc_info=True)
                result = {
                    "status": "error",
                    "message": f"Failed to set workspace: {str(e)}"
                }
                return json.dumps(result, ensure_ascii=False, indent=2)

        @server.tool()
        async def ping() -> str:
            """Simple ping tool to test connectivity"""
            try:
                logger.info("ping called")
                result = {
                    "status": "success",
                    "message": "pong",
                    "timestamp": str(asyncio.get_event_loop().time())
                }
                return json.dumps(result, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Error in ping: {e}", exc_info=True)
                return json.dumps({"status": "error", "message": str(e)})

        logger.info("Tools registered successfully:")
        logger.info("  • set_workspace")
        logger.info("  • ping")

        print("🚀 Robust MCP Server")
        print("Tools registered:")
        print("  • set_workspace - Set workspace directory")
        print("  • ping - Test connectivity")
        print("🔧 Starting server...")

        # Start server with error handling
        try:
            server.run()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            print("\n🛑 Server stopped by user")
        except Exception as server_error:
            logger.error(f"Server runtime error: {server_error}", exc_info=True)
            print(f"❌ Server runtime error: {server_error}")
            raise

    except ImportError as e:
        error_msg = f"Failed to import required modules: {e}"
        logger.error(error_msg, exc_info=True)
        print(f"❌ {error_msg}")
        sys.exit(1)
    except Exception as e:
        error_msg = f"Fatal server error: {e}"
        logger.error(error_msg, exc_info=True)
        print(f"❌ {error_msg}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
