#!/usr/bin/env python3
"""
Command Executor MCP Tool / 命令执行器 MCP 工具

专门负责执行LLM生成的shell命令来创建文件树结构
Specialized in executing LLM-generated shell commands to create file tree structures
"""

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import MCP related modules
from mcp.server.fastmcp import FastMCP

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastMCP 服务器实例
mcp = FastMCP("command-executor")


@mcp.tool()
async def execute_commands(commands: str, working_directory: str) -> str:
    """
    执行shell命令列表来创建文件树结构
    Execute shell command list to create file tree structure

    Args:
        commands: 要执行的shell命令列表（每行一个命令）
        working_directory: 执行命令的工作目录

    Returns:
        命令执行结果和详细报告
    """
    try:
        # 确保工作目录存在
        work_dir = Path(working_directory).resolve()
        work_dir.mkdir(parents=True, exist_ok=True)

        # 分割命令
        command_list = [cmd.strip() for cmd in commands.split('\n') if cmd.strip()]

        results = []
        success_count = 0
        error_count = 0

        for i, cmd in enumerate(command_list, 1):
            try:
                logger.info(f"执行命令 {i}/{len(command_list)}: {cmd}")

                # 执行命令
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(work_dir),
                    timeout=30
                )

                if result.returncode == 0:
                    success_count += 1
                    status = "✅ SUCCESS"
                    output = result.stdout or "命令执行成功"
                else:
                    error_count += 1
                    status = "❌ ERROR"
                    output = result.stderr or f"命令执行失败，返回码: {result.returncode}"

                results.append({
                    "command": cmd,
                    "status": status,
                    "output": output.strip()
                })

            except subprocess.TimeoutExpired:
                error_count += 1
                results.append({
                    "command": cmd,
                    "status": "❌ TIMEOUT",
                    "output": "命令执行超时 (30秒)"
                })
            except Exception as e:
                error_count += 1
                results.append({
                    "command": cmd,
                    "status": "❌ EXCEPTION",
                    "output": f"执行异常: {str(e)}"
                })

        # 生成摘要报告
        summary = {
            "total_commands": len(command_list),
            "successful": success_count,
            "failed": error_count,
            "working_directory": str(work_dir),
            "details": results
        }

        return json.dumps(summary, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"批量命令执行失败: {e}")
        return json.dumps({
            "error": f"批量命令执行失败: {str(e)}",
            "working_directory": working_directory
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def execute_single_command(command: str, working_directory: str) -> str:
    """
    执行单个shell命令
    Execute single shell command

    Args:
        command: 要执行的单个shell命令
        working_directory: 执行命令的工作目录

    Returns:
        命令执行结果
    """
    try:
        # 确保工作目录存在
        work_dir = Path(working_directory).resolve()
        work_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"执行单个命令: {command}")

        # 执行命令
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(work_dir),
            timeout=30
        )

        response = {
            "command": command,
            "working_directory": str(work_dir),
            "return_code": result.returncode,
            "stdout": result.stdout.strip() if result.stdout else "",
            "stderr": result.stderr.strip() if result.stderr else "",
            "status": "SUCCESS" if result.returncode == 0 else "ERROR"
        }

        return json.dumps(response, indent=2, ensure_ascii=False)

    except subprocess.TimeoutExpired:
        return json.dumps({
            "command": command,
            "working_directory": working_directory,
            "error": "命令执行超时 (30秒)",
            "status": "TIMEOUT"
        }, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"单个命令执行失败: {e}")
        return json.dumps({
            "command": command,
            "working_directory": working_directory,
            "error": f"命令执行失败: {str(e)}",
            "status": "EXCEPTION"
        }, indent=2, ensure_ascii=False)


def main():
    """启动服务器"""
    print("🚀 Command Executor MCP Server")
    print("📝 Shell Command Execution Tool / Shell命令执行工具")
    print("")
    print("Available tools / 可用工具:")
    print("  • execute_commands       - Execute multiple shell commands / 执行多个shell命令")
    print("  • execute_single_command - Execute single shell command / 执行单个shell命令")
    print("")
    print("🔧 Server starting...")

    # 启动 FastMCP 服务器
    mcp.run()


if __name__ == "__main__":
    main()
