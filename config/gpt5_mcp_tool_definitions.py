#!/usr/bin/env python3
"""
GPT-5 Compatible MCP Tool Definitions
Updated to work with GPT-5 Responses API format
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.gpt5_tool_converter import GPT5ToolConverter


class GPT5MCPToolDefinitions:
    """GPT-5 compatible MCP tool definitions manager"""

    @staticmethod
    def get_code_implementation_tools() -> List[Dict[str, Any]]:
        """
        Get tool definitions for code implementation (GPT-5 format)
        """
        mcp_tools = [
            GPT5MCPToolDefinitions._get_set_workspace_tool(),
            GPT5MCPToolDefinitions._get_read_file_tool(),
            GPT5MCPToolDefinitions._get_read_multiple_files_tool(),
            GPT5MCPToolDefinitions._get_write_file_tool(),
            GPT5MCPToolDefinitions._get_write_multiple_files_tool(),
            GPT5MCPToolDefinitions._get_execute_python_tool(),
            GPT5MCPToolDefinitions._get_execute_bash_tool(),
        ]

        # Convert to GPT-5 format
        return GPT5ToolConverter.convert_mcp_tools_list(mcp_tools)

    @staticmethod
    def get_command_executor_tools() -> List[Dict[str, Any]]:
        """
        Get command executor tools (GPT-5 format)
        """
        mcp_tools = [
            GPT5MCPToolDefinitions._get_execute_commands_tool(),
            GPT5MCPToolDefinitions._get_execute_single_command_tool(),
        ]

        # Convert to GPT-5 format
        return GPT5ToolConverter.convert_mcp_tools_list(mcp_tools)

    @staticmethod
    def _get_read_file_tool() -> Dict[str, Any]:
        """读取文件工具定义"""
        return {
            "type": "function",
            "name": "read_file",
            "description": "Read file content, supports specifying line number range",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path, relative to workspace",
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Start line number (1-based, optional)",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "End line number (1-based, optional)",
                    },
                },
                "required": ["file_path"],
            },
        }

    @staticmethod
    def _get_set_workspace_tool() -> Dict[str, Any]:
        """设置工作目录工具定义"""
        return {
            "type": "function",
            "name": "set_workspace",
            "description": "Set the current workspace directory for all file operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_path": {
                        "type": "string",
                        "description": "Absolute path to the workspace directory",
                    }
                },
                "required": ["workspace_path"],
            },
        }

    @staticmethod
    def _get_read_multiple_files_tool() -> Dict[str, Any]:
        """批量读取文件工具定义"""
        return {
            "type": "function",
            "name": "read_multiple_files",
            "description": "Read content from multiple files at once",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of file paths to read",
                    }
                },
                "required": ["file_paths"],
            },
        }

    @staticmethod
    def _get_write_file_tool() -> Dict[str, Any]:
        """写入文件工具定义"""
        return {
            "type": "function",
            "name": "write_file",
            "description": "Write content to a file, creating directories if needed",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path, relative to workspace",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file",
                    },
                },
                "required": ["file_path", "content"],
            },
        }

    @staticmethod
    def _get_write_multiple_files_tool() -> Dict[str, Any]:
        """批量写入文件工具定义"""
        return {
            "type": "function",
            "name": "write_multiple_files",
            "description": "Write content to multiple files at once",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"type": "string"}
                            },
                            "required": ["path", "content"]
                        },
                        "description": "Array of file objects with path and content",
                    }
                },
                "required": ["files"],
            },
        }

    @staticmethod
    def _get_execute_python_tool() -> Dict[str, Any]:
        """执行Python代码工具定义"""
        return {
            "type": "function",
            "name": "execute_python",
            "description": "Execute Python code in the workspace environment",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Execution timeout in seconds (default: 30)",
                    },
                },
                "required": ["code"],
            },
        }

    @staticmethod
    def _get_execute_bash_tool() -> Dict[str, Any]:
        """执行Bash命令工具定义"""
        return {
            "type": "function",
            "name": "execute_bash",
            "description": "Execute bash/shell command in the workspace",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Execution timeout in seconds (default: 30)",
                    },
                },
                "required": ["command"],
            },
        }

    @staticmethod
    def _get_execute_commands_tool() -> Dict[str, Any]:
        """批量执行命令工具定义"""
        return {
            "type": "function",
            "name": "execute_commands",
            "description": "Execute multiple shell commands to create file tree structure",
            "parameters": {
                "type": "object",
                "properties": {
                    "commands": {
                        "type": "string",
                        "description": "Shell command list (one command per line)",
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory for command execution",
                    },
                },
                "required": ["commands", "working_directory"],
            },
        }

    @staticmethod
    def _get_execute_single_command_tool() -> Dict[str, Any]:
        """单命令执行工具定义"""
        return {
            "type": "function",
            "name": "execute_single_command",
            "description": "Execute single shell command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Single shell command to execute",
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory for command execution",
                    },
                },
                "required": ["command", "working_directory"],
            },
        }

    @staticmethod
    def get_all_tools() -> List[Dict[str, Any]]:
        """Get all available tools in GPT-5 format"""
        return (
            GPT5MCPToolDefinitions.get_code_implementation_tools() +
            GPT5MCPToolDefinitions.get_command_executor_tools()
        )

# Test the tool definitions
if __name__ == "__main__":
    import json

    print("🛠️  GPT-5 Compatible MCP Tool Definitions")
    print("="*50)

    tools = GPT5MCPToolDefinitions.get_code_implementation_tools()

    print(f"📋 Found {len(tools)} code implementation tools:")
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool['name']}: {tool['description'][:50]}...")

    print(f"\n🔧 Sample tool definition:")
    print(json.dumps(tools[0], indent=2))
