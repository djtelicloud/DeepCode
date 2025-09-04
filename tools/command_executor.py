#!/usr/bin/env python3
"""
Command Executor MCP Tool

Specialized in executing LLM-generated shell commands to create file tree structures
"""

import subprocess
from pathlib import Path
from typing import Dict, List

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Create MCP server instance
app = Server("command-executor")


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools
    """
    return [
        types.Tool(
            name="execute_commands",
            description="""
            Execute shell command list to create file tree structure

            Args:
                commands: List of shell commands to execute (one command per line)
                working_directory: Working directory for command execution

            Returns:
                Command execution results and detailed report
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "commands": {
                        "type": "string",
                        "title": "Commands",
                        "description": "List of shell commands to execute, one command per line",
                    },
                    "working_directory": {
                        "type": "string",
                        "title": "Working Directory",
                        "description": "Working directory for command execution",
                    },
                },
                "required": ["commands", "working_directory"],
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="execute_single_command",
            description="""
            Execute single shell command

            Args:
                command: Single command to execute
                working_directory: Working directory for command execution

            Returns:
                Command execution result
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "title": "Command",
                        "description": "Single shell command to execute",
                    },
                    "working_directory": {
                        "type": "string",
                        "title": "Working Directory",
                        "description": "Working directory for command execution",
                    },
                },
                "required": ["command", "working_directory"],
                "additionalProperties": False,
            },
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """
    Handle tool calls
    """
    try:
        if name == "execute_commands":
            return await execute_command_batch(
                arguments.get("commands", ""), arguments.get("working_directory", ".")
            )
        elif name == "execute_single_command":
            return await execute_single_command(
                arguments.get("command", ""), arguments.get("working_directory", ".")
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error executing tool {name}: {str(e)}",
            )
        ]


async def execute_command_batch(
    commands: str, working_directory: str
) -> list[types.TextContent]:
    """
    Execute multiple shell commands

    Args:
        commands: Command list, one command per line
        working_directory: Working directory

    Returns:
        Execution results
    """
    try:
        # Ensure working directory exists
        Path(working_directory).mkdir(parents=True, exist_ok=True)

        # Split command lines
        command_lines = [
            cmd.strip() for cmd in commands.strip().split("\n") if cmd.strip()
        ]

        if not command_lines:
            return [
                types.TextContent(
                    type="text", text="No valid commands provided"
                )
            ]

        results = []
        stats = {"successful": 0, "failed": 0, "timeout": 0}

        for i, command in enumerate(command_lines, 1):
            try:
                # Execute command
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=working_directory,
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout
                )

                if result.returncode == 0:
                    results.append(f"✅ Command {i}: {command}")
                    if result.stdout.strip():
                        results.append(f"   Output: {result.stdout.strip()}")
                    stats["successful"] += 1
                else:
                    results.append(f"❌ Command {i}: {command}")
                    if result.stderr.strip():
                        results.append(f"   Error: {result.stderr.strip()}")
                    stats["failed"] += 1

            except subprocess.TimeoutExpired:
                results.append(f"⏱️ Command {i} timeout: {command}")
                stats["timeout"] += 1
            except Exception as e:
                results.append(f"💥 Command {i} exception: {command} - {str(e)}")
                stats["failed"] += 1

        # Generate execution report
        summary = generate_execution_summary(working_directory, command_lines, stats)
        final_result = summary + "\n" + "\n".join(results)

        return [types.TextContent(type="text", text=final_result)]

    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Failed to execute command batch: {str(e)}",
            )
        ]


async def execute_single_command(
    command: str, working_directory: str
) -> list[types.TextContent]:
    """
    Execute single shell command

    Args:
        command: Command to execute
        working_directory: Working directory

    Returns:
        Execution result
    """
    try:
        # Ensure working directory exists
        Path(working_directory).mkdir(parents=True, exist_ok=True)

        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Format output
        output = format_single_command_result(command, working_directory, result)

        return [types.TextContent(type="text", text=output)]

    except subprocess.TimeoutExpired:
        return [
            types.TextContent(
                type="text", text=f"⏱️ Command timeout: {command}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text", text=f"💥 Command execution error: {str(e)}"
            )
        ]


def generate_execution_summary(
    working_directory: str, command_lines: List[str], stats: Dict[str, int]
) -> str:
    """
    Generate execution summary

    Args:
        working_directory: Working directory
        command_lines: Command list
        stats: Statistics

    Returns:
        Formatted summary
    """
    return f"""
Command Execution Summary:
{'='*50}
Working Directory: {working_directory}
Total Commands: {len(command_lines)}
Successful: {stats['successful']}
Failed: {stats['failed']}
Timeout: {stats['timeout']}

Detailed Results:
{'-'*50}"""


def format_single_command_result(
    command: str, working_directory: str, result: subprocess.CompletedProcess
) -> str:
    """
    Format single command execution result

    Args:
        command: Executed command
        working_directory: Working directory
        result: Execution result

    Returns:
        Formatted result
    """
    output = f"""
Single Command Execution:
{'='*40}
Working Directory: {working_directory}
Command: {command}
Return Code: {result.returncode}

"""

    if result.returncode == 0:
        output += "✅ Status: SUCCESS\n"
        if result.stdout.strip():
            output += f"Output:\n{result.stdout.strip()}\n"
    else:
        output += "❌ Status: FAILED\n"
        if result.stderr.strip():
            output += f"Error:\n{result.stderr.strip()}\n"

    return output


async def main():
    """
    Run MCP server
    """
    # Run server via stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="command-executor",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
