#!/usr/bin/env python3
"""
MCP server that exactly matches the expected tool definitions
"""

import json
import sys
from pathlib import Path
from typing import Optional


def main():
    """Start MCP server with exact tool definition matching"""
    try:
        from mcp.server.fastmcp import FastMCP

        print("🎯 Tool Definition Matching MCP Server")
        print("Creating server with exact tool specifications...")

        # Create server
        server = FastMCP("code-implementation")

        # Define set_workspace tool with EXACT signature from MCPToolDefinitions
        @server.tool()
        async def set_workspace(workspace_path: str) -> str:
            """Set the workspace directory for file operations"""
            try:
                workspace = Path(workspace_path).resolve()
                workspace.mkdir(parents=True, exist_ok=True)

                # Return result in exact format expected
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

        # Add a simple test tool to verify server is working
        @server.tool()
        async def read_file(file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
            """Read file content, supports specifying line number range"""
            try:
                if not Path(file_path).exists():
                    result = {"status": "error", "message": f"File not found: {file_path}"}
                    return json.dumps(result, ensure_ascii=False, indent=2)

                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                if start_line is not None or end_line is not None:
                    start_idx = (start_line - 1) if start_line else 0
                    end_idx = end_line if end_line else len(lines)
                    lines = lines[start_idx:end_idx]

                content = ''.join(lines)
                result = {
                    "status": "success",
                    "content": content,
                    "file_path": file_path,
                    "total_lines": len(lines)
                }
                return json.dumps(result, ensure_ascii=False, indent=2)

            except Exception as e:
                result = {
                    "status": "error",
                    "message": f"Failed to read file: {str(e)}"
                }
                return json.dumps(result, ensure_ascii=False, indent=2)

        print("Tools registered with exact specifications:")
        print("  • set_workspace (workspace_path: str)")
        print("  • read_file (file_path: str, start_line?: int, end_line?: int)")
        print("")
        print("🔧 Starting server...")

        # Start the server
        server.run()

    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
