"""
Paper Code Implementation Workflow - MCP-compliant Iterative Development

Features:
1. File Tree Creation
2. Code Implementation - Based on aisi-basic-agent iterative development

MCP Architecture:
- MCP Server: tools/code_implementation_server.py
- MCP Client: Called through mcp_agent framework
- Configuration: mcp_agent.config.yaml
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
# MCP Agent imports
from mcp_agent.agents.agent import Agent

# Local imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.mcp_tool_definitions import get_mcp_tools
from prompts.code_prompts import (PURE_CODE_IMPLEMENTATION_SYSTEM_PROMPT_INDEX,
                                  STRUCTURE_GENERATOR_PROMPT)
from utils.llm_utils import get_default_models
from workflows.agents import CodeImplementationAgent
from workflows.agents.memory_agent_concise import ConciseMemoryAgent

# DialogueLogger removed - no longer needed


class CodeImplementationWorkflowWithIndex:
    """
    Paper Code Implementation Workflow Manager with Code Reference Indexer

    Uses standard MCP architecture with enhanced indexing capabilities:
    1. Connect to code-implementation server via MCP client
    2. Use MCP protocol for tool calls
    3. Support workspace management and operation history tracking
    4. Integrated code reference indexer for enhanced code understanding
    """

    # ==================== 1. Class Initialization and Configuration (Infrastructure Layer) ====================

    def __init__(self, config_path: str = "mcp_agent.secrets.yaml"):
        """Initialize workflow with configuration"""
        self.config_path = config_path
        self.api_config = self._load_api_config()
        self.default_models = get_default_models("mcp_agent.config.yaml")
        self.logger = self._create_logger()
        self.mcp_agent = None
        self.enable_read_tools = (
            True  # Default value, will be overridden by run_workflow parameter
        )

    def _load_api_config(self) -> Dict[str, Any]:
        """Load API configuration from YAML file"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Failed to load API config: {e}")

    def _create_logger(self) -> logging.Logger:
        """Create and configure logger"""
        logger = logging.getLogger(__name__)
        # Don't add handlers to child loggers - let them propagate to root
        logger.setLevel(logging.INFO)
        return logger

    def _read_plan_file(self, plan_file_path: str) -> str:
        """Read implementation plan file with fallback mechanisms"""
        plan_path = Path(plan_file_path)

        # Try the original path first
        if plan_path.exists():
            with open(plan_path, "r", encoding="utf-8") as f:
                return f.read()

        # Fallback 1: Look for plan file in current working directory and paper iterations
        fallback_paths = [Path("initial_plan.txt")]

        # Add dynamic paths for paper iterations (1, 2, 3, etc.)
        base_paths = [
            "deepcode_lab/papers",
            "papers",
            "agent_folders/papers",  # Common alternative structure
        ]

        for base_path in base_paths:
            base_dir = Path(base_path)
            if base_dir.exists():
                # Find all numbered subdirectories (1, 2, 3, etc.)
                for item in base_dir.iterdir():
                    if item.is_dir() and item.name.isdigit():
                        plan_file = item / "initial_plan.txt"
                        fallback_paths.append(plan_file)

        # Sort by paper number (highest first) to prioritize latest iterations
        numbered_paths = [p for p in fallback_paths if p.parent.name.isdigit()]
        other_paths = [p for p in fallback_paths if not p.parent.name.isdigit()]
        numbered_paths.sort(key=lambda p: int(p.parent.name), reverse=True)
        fallback_paths = numbered_paths + other_paths

        for fallback_path in fallback_paths:
            if fallback_path.exists():
                self.logger.warning(f"Plan file not found at {plan_file_path}, using fallback: {fallback_path}")
                with open(fallback_path, "r", encoding="utf-8") as f:
                    return f.read()

        # Fallback 2: Create a basic plan if no plan file exists
        self.logger.warning(f"No implementation plan found. Creating a basic plan at {plan_file_path}")
        return self._create_default_plan(plan_file_path)

    def _create_default_plan(self, plan_file_path: str) -> str:
        """Create a default implementation plan when none exists"""
        plan_path = Path(plan_file_path)

        # Ensure parent directory exists
        plan_path.parent.mkdir(parents=True, exist_ok=True)

        default_plan = """# Default Implementation Plan

## Overview
This is an auto-generated implementation plan created because no plan file was found.

## Project Structure
```
generate_code/
├── main.py           # Main entry point
├── README.md         # Project documentation
├── requirements.txt  # Dependencies
└── src/             # Source code directory
    └── __init__.py  # Package initialization
```

## Implementation Strategy
1. **Setup Phase**: Create basic project structure
2. **Core Implementation**: Implement main functionality
3. **Documentation**: Add README and documentation
4. **Dependencies**: Set up requirements.txt

## Notes
- This is a minimal plan. Please replace with a proper implementation plan.
- Consider the specific requirements of your project.
- Update the file structure based on your actual needs.
"""

        # Write the default plan to file
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(default_plan)

        self.logger.info(f"Created default plan file at: {plan_file_path}")
        return default_plan

    def _check_file_tree_exists(self, target_directory: str) -> bool:
        """Check if file tree structure already exists"""
        code_directory = os.path.join(target_directory, "generate_code")
        return os.path.exists(code_directory) and len(os.listdir(code_directory)) > 0

    # ==================== 2. Public Interface Methods (External API Layer) ====================

    async def run_workflow(
        self,
        plan_file_path: str,
        target_directory: Optional[str] = None,
        pure_code_mode: bool = False,
        enable_read_tools: bool = True,
    ):
        """Run complete workflow - Main public interface"""
        # Set the read tools configuration
        self.enable_read_tools = enable_read_tools

        try:
            plan_content = self._read_plan_file(plan_file_path)

            if target_directory is None:
                target_directory = str(Path(plan_file_path).parent)

            # Calculate code directory for workspace alignment
            code_directory = os.path.join(target_directory, "generate_code")

            self.logger.info("=" * 80)
            self.logger.info("🚀 STARTING CODE IMPLEMENTATION WORKFLOW")
            self.logger.info("=" * 80)
            self.logger.info(f"📄 Plan file: {plan_file_path}")
            self.logger.info(f"📂 Plan file parent: {target_directory}")
            self.logger.info(f"🎯 Code directory (MCP workspace): {code_directory}")
            self.logger.info(
                f"⚙️  Read tools: {'ENABLED' if self.enable_read_tools else 'DISABLED'}"
            )
            self.logger.info("=" * 80)

            results = {}

            # Check if file tree exists
            if self._check_file_tree_exists(target_directory):
                self.logger.info("File tree exists, skipping creation")
                results["file_tree"] = "Already exists, skipped creation"
            else:
                self.logger.info("Creating file tree...")
                results["file_tree"] = await self.create_file_structure(
                    plan_content, target_directory
                )

            # Code implementation
            if pure_code_mode:
                self.logger.info("Starting pure code implementation...")
                results["code_implementation"] = await self.implement_code_pure(
                    plan_content, target_directory, code_directory
                )
            else:
                pass

            self.logger.info("Workflow execution successful")

            return {
                "status": "success",
                "plan_file": plan_file_path,
                "target_directory": target_directory,
                "code_directory": os.path.join(target_directory, "generate_code"),
                "results": results,
                "mcp_architecture": "standard",
            }

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")

            return {"status": "error", "message": str(e), "plan_file": plan_file_path}
        finally:
            await self._cleanup_mcp_agent()

    async def create_file_structure(
        self, plan_content: str, target_directory: str
    ) -> str:
        """Create file tree structure based on implementation plan"""
        self.logger.info("Starting file tree creation...")

        structure_agent = Agent(
            name="StructureGeneratorAgent",
            instruction=STRUCTURE_GENERATOR_PROMPT,
            server_names=["command-executor"],
        )

        entered = False
        try:
            # Explicitly enter the Agent async context instead of using `async with`
            await structure_agent.__aenter__()
            entered = True

            from mcp_agent.workflows.llm.augmented_llm_openai import \
                OpenAIAugmentedLLM
            creator = await structure_agent.attach_llm(OpenAIAugmentedLLM)

            message = f"""Analyze the following implementation plan and generate shell commands to create the file tree structure.

Target Directory: {target_directory}/generate_code

Implementation Plan:
{plan_content}

Tasks:
1. Find the file tree structure in the implementation plan
2. Generate shell commands (mkdir -p, touch) to create that structure
3. Use the execute_commands tool to run the commands and create the file structure

Requirements:
- Use mkdir -p to create directories
- Use touch to create files
- Include __init__.py file for Python packages
- Use relative paths to the target directory
- Execute commands to actually create the file structure"""

            result = await creator.generate_str(message=message)
            self.logger.info("File tree structure creation completed")
            return result
        finally:
            if entered:
                try:
                    await structure_agent.__aexit__(None, None, None)
                except Exception as e:
                    self.logger.warning(f"Failed to close structure agent: {e}")

    async def implement_code_pure(
        self, plan_content: str, target_directory: str, code_directory: Optional[str] = None
    ) -> str:
        """Pure code implementation - focus on code writing without testing"""
        self.logger.info("Starting pure code implementation (no testing)...")

        # Use provided code_directory or calculate it (for backwards compatibility)
        if code_directory is None:
            code_directory = os.path.join(target_directory, "generate_code")

        self.logger.info(f"🎯 Using code directory (MCP workspace): {code_directory}")

        if not os.path.exists(code_directory):
            raise FileNotFoundError(
                "File tree structure not found, please run file tree creation first"
            )

        try:
            client = await self._initialize_llm_client()
            await self._initialize_mcp_agent(code_directory)

            tools = self._prepare_mcp_tool_definitions()
            system_message = PURE_CODE_IMPLEMENTATION_SYSTEM_PROMPT_INDEX
            messages = []

            #             implementation_message = f"""**TASK: Implement Research Paper Reproduction Code**

            # You are implementing a complete, working codebase that reproduces the core algorithms, experiments, and methods described in a research paper. Your goal is to create functional code that can replicate the paper's key results and contributions.

            # **What you need to do:**
            # - Analyze the paper content and reproduction plan to understand requirements
            # - Implement all core algorithms mentioned in the main body of the paper
            # - Create the necessary components following the planned architecture
            # - Test each component to ensure functionality
            # - Integrate components into a cohesive, executable system
            # - Focus on reproducing main contributions rather than appendix-only experiments

            # **RESOURCES:**
            # - **Paper & Reproduction Plan**: `{target_directory}/` (contains .md paper files and initial_plan.txt with detailed implementation guidance)
            # - **Reference Code Indexes**: `{target_directory}/indexes/` (JSON files with implementation patterns from related codebases)
            # - **Implementation Directory**: `{code_directory}/` (your working directory for all code files)

            # **CURRENT OBJECTIVE:**
            # Start by reading the reproduction plan (`{target_directory}/initial_plan.txt`) to understand the implementation strategy, then examine the paper content to identify the first priority component to implement. Use the search_code tool to find relevant reference implementations from the indexes directory (`{target_directory}/indexes/*.json`) before coding.

            # ---
            # **START:** Review the plan above and begin implementation."""
            implementation_message = f"""**Task: Implement code based on the following reproduction plan**

**Code Reproduction Plan:**
{plan_content}

**Working Directory:** {code_directory}

**Current Objective:** Begin implementation by analyzing the plan structure, examining the current project layout, and implementing the first foundation file according to the plan's priority order."""

            messages.append({"role": "user", "content": implementation_message})

            result = await self._pure_code_implementation_loop(
                client,
                system_message,
                messages,
                tools,
                plan_content,
                target_directory,
            )

            return result

        finally:
            await self._cleanup_mcp_agent()

    # ==================== 3. Core Business Logic (Implementation Layer) ====================

    async def _pure_code_implementation_loop(
        self,
        client,
        system_message,
        messages,
        tools,
        plan_content,
        target_directory,
    ):
        """Pure code implementation loop with memory optimization and phase consistency"""
        max_iterations = 500
        iteration = 0
        start_time = time.time()
        max_time = 5000  # 40 minutes

        # Initialize specialized agents
        code_agent = CodeImplementationAgent(
            self.mcp_agent, self.logger, self.enable_read_tools
        )
        memory_agent = ConciseMemoryAgent(plan_content, self.logger, target_directory)

        # Log read tools configuration
        read_tools_status = "ENABLED" if self.enable_read_tools else "DISABLED"
        self.logger.info(
            f"🔧 Read tools (read_file, read_code_mem): {read_tools_status}"
        )
        if not self.enable_read_tools:
            self.logger.info(
                "🚫 No read mode: read_file and read_code_mem tools will be skipped"
            )

        # Connect code agent with memory agent for summary generation
        # Note: Memory agent now uses GPTClient internally
        code_agent.set_memory_agent(memory_agent)

        # Initialize memory agent with iteration 0
        memory_agent.start_new_round(iteration=0)

        while iteration < max_iterations:
            iteration += 1
            elapsed_time = time.time() - start_time

            if elapsed_time > max_time:
                self.logger.warning(f"Time limit reached: {elapsed_time:.2f}s")
                break

            # # Test simplified memory approach if we have files implemented
            # if iteration == 5 and code_agent.get_files_implemented_count() > 0:
            #     self.logger.info("🧪 Testing simplified memory approach...")
            #     test_results = await memory_agent.test_simplified_memory_approach()
            #     self.logger.info(f"Memory test results: {test_results}")

            # self.logger.info(f"Pure code implementation iteration {iteration}: generating code")

            messages = self._validate_messages(messages)
            current_system_message = code_agent.get_system_prompt()

            # Round logging removed

            # Call LLM
            response = await self._call_llm_with_tools(
                client, current_system_message, messages, tools
            )

            response_content = response.get("content", "").strip()
            if not response_content:
                response_content = "Continue implementing code files..."

            messages.append({"role": "assistant", "content": response_content})

            # Handle tool calls
            if response.get("tool_calls"):
                tool_results = await code_agent.execute_tool_calls(
                    response["tool_calls"]
                )

                # Record essential tool results in concise memory agent
                for tool_call, tool_result in zip(response["tool_calls"], tool_results):
                    memory_agent.record_tool_result(
                        tool_name=tool_call["name"],
                        tool_input=tool_call["input"],
                        tool_result=tool_result.get("result"),
                    )

                # NEW LOGIC: Check if write_file was called and trigger memory optimization immediately

                # Determine guidance based on results
                has_error = self._check_tool_results_for_errors(tool_results)
                files_count = code_agent.get_files_implemented_count()

                if has_error:
                    guidance = self._generate_error_guidance()
                else:
                    guidance = self._generate_success_guidance(files_count)

                compiled_response = self._compile_user_response(tool_results, guidance)
                messages.append({"role": "user", "content": compiled_response})

                # NEW LOGIC: Apply memory optimization immediately after write_file detection
                if memory_agent.should_trigger_memory_optimization(
                    messages, code_agent.get_files_implemented_count()
                ):
                    # Memory optimization triggered

                    # Apply concise memory optimization
                    files_implemented_count = code_agent.get_files_implemented_count()
                    current_system_message = code_agent.get_system_prompt()
                    messages = memory_agent.apply_memory_optimization(
                        current_system_message, messages, files_implemented_count
                    )

                    # Memory optimization completed

            else:
                files_count = code_agent.get_files_implemented_count()
                no_tools_guidance = self._generate_no_tools_guidance(files_count)
                messages.append({"role": "user", "content": no_tools_guidance})

            # Check for analysis loop and provide corrective guidance
            if code_agent.is_in_analysis_loop():
                analysis_loop_guidance = code_agent.get_analysis_loop_guidance()
                messages.append({"role": "user", "content": analysis_loop_guidance})
                self.logger.warning(
                    "Analysis loop detected and corrective guidance provided"
                )

            # Record file implementations in memory agent (for the current round)
            for file_info in code_agent.get_implementation_summary()["completed_files"]:
                memory_agent.record_file_implementation(file_info["file"])

            # REMOVED: Old memory optimization logic - now happens immediately after write_file
            # Memory optimization is now triggered immediately after write_file detection

            # Start new round for next iteration, sync with workflow iteration
            memory_agent.start_new_round(iteration=iteration)

            # Check completion
            if any(
                keyword in response_content.lower()
                for keyword in [
                    "all files implemented",
                    "all phases completed",
                    "reproduction plan fully implemented",
                    "all code of repo implementation complete",
                ]
            ):
                self.logger.info("Code implementation declared complete")
                break

            # Emergency trim if too long
            if len(messages) > 500:
                self.logger.warning(
                    "Emergency message trim - applying concise memory optimization"
                )

                current_system_message = code_agent.get_system_prompt()
                files_implemented_count = code_agent.get_files_implemented_count()
                messages = memory_agent.apply_memory_optimization(
                    current_system_message, messages, files_implemented_count
                )

        return await self._generate_pure_code_final_report_with_concise_agents(
            iteration, time.time() - start_time, code_agent, memory_agent
        )

    # ==================== 4. MCP Agent and LLM Communication Management (Communication Layer) ====================

    async def _initialize_mcp_agent(self, code_directory: str):
        """Initialize MCP agent and connect to code-implementation server"""
        try:
            self.mcp_agent = Agent(
                name="CodeImplementationAgent",
                instruction="You are a code implementation assistant, using MCP tools to implement paper code replication.",
                server_names=["code-implementation", "code-reference-indexer"],
            )

            await self.mcp_agent.__aenter__()
            from mcp_agent.workflows.llm.augmented_llm_openai import \
                OpenAIAugmentedLLM
            llm = await self.mcp_agent.attach_llm(OpenAIAugmentedLLM)

            # Set workspace to the target code directory
            workspace_result = await self.mcp_agent.call_tool(
                "set_workspace", {"workspace_path": code_directory}
            )
            self.logger.info(f"Workspace setup result: {workspace_result}")

            return llm

        except Exception as e:
            self.logger.error(f"Failed to initialize MCP agent: {e}")
            if self.mcp_agent:
                try:
                    await self.mcp_agent.__aexit__(None, None, None)
                except Exception:
                    pass
                self.mcp_agent = None
            raise

    async def _cleanup_mcp_agent(self):
        """Clean up MCP agent resources"""
        if self.mcp_agent:
            try:
                await self.mcp_agent.__aexit__(None, None, None)
                self.logger.info("MCP agent connection closed")
            except Exception as e:
                self.logger.warning(f"Error closing MCP agent: {e}")
            finally:
                self.mcp_agent = None

    async def _initialize_llm_client(self):
        """Initialize GPT-5 client using GPTClient"""
        from tools.gpt_client import GPTClient

        try:
            client = GPTClient()
            self.logger.info("Using GPT-5 with responses API")
            return client
        except Exception as e:
            self.logger.error(f"Failed to initialize GPTClient: {e}")
            raise ValueError(
                "No available LLM API - please check your OpenAI API key in configuration"
            )

    async def _call_llm_with_tools(
        self, client, system_message, messages, tools, max_tokens=20000
    ):
        """Call GPTClient with tools"""
        try:
            return await self._call_gpt_client_with_tools(
                client, system_message, messages, tools, max_tokens
            )
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise

    async def _call_gpt_client_with_tools(
        self, client, system_message, messages, tools, max_tokens
    ):
        """Call GPTClient with MCP tools using responses API"""
        validated_messages = self._validate_messages(messages)
        if not validated_messages:
            validated_messages = [
                {"role": "user", "content": "Please continue implementing code"}
            ]

        try:
            # Create combined input with system prompt and conversation
            messages_text = ""
            for msg in validated_messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages_text += f"{role}: {content}\n"

            combined_input = f"{system_message}\n\nConversation:\n{messages_text}"

            # Use new MCP tools support in responses API
            response = await client.call_with_mcp_tools(
                input_text=combined_input,
                mcp_tools=tools
            )

            # Return in expected format - response is now a string
            return {
                "content": response,
                "tool_calls": []  # MCP tool calls are handled internally by responses API
            }
        except Exception as e:
            self.logger.error(f"GPTClient MCP API call failed: {e}")
            raise

    # ==================== 5. Tools and Utility Methods (Utility Layer) ====================

    def _validate_messages(self, messages: List[Dict]) -> List[Dict]:
        """Validate and clean message list"""
        valid_messages = []
        for msg in messages:
            content = msg.get("content", "").strip()
            if content:
                valid_messages.append(
                    {"role": msg.get("role", "user"), "content": content}
                )
            else:
                self.logger.warning(f"Skipping empty message: {msg}")
        return valid_messages

    def _prepare_mcp_tool_definitions(self) -> List[Dict[str, Any]]:
        """Prepare tool definitions for MCP tools"""
        return get_mcp_tools("code_implementation")

    def _check_tool_results_for_errors(self, tool_results: List[Dict]) -> bool:
        """Check tool results for errors"""
        for result in tool_results:
            try:
                if hasattr(result["result"], "content") and result["result"].content:
                    content_text = result["result"].content[0].text
                    parsed_result = json.loads(content_text)
                    if parsed_result.get("status") == "error":
                        return True
                elif isinstance(result["result"], str):
                    if "error" in result["result"].lower():
                        return True
            except (json.JSONDecodeError, AttributeError, IndexError):
                result_str = str(result["result"])
                if "error" in result_str.lower():
                    return True
        return False

    # ==================== 6. User Interaction and Feedback (Interaction Layer) ====================

    def _generate_success_guidance(self, files_count: int) -> str:
        """Generate concise success guidance for continuing implementation"""
        return f"""✅ File implementation completed successfully!

📊 **Progress Status:** {files_count} files implemented

🎯 **Next Action:** Check if ALL files from the reproduction plan are implemented.

⚡ **Decision Process:**
1. **If ALL files are implemented:** Use `execute_python` or `execute_bash` to test the complete implementation, then respond "**implementation complete**" to end the conversation
2. **If MORE files need implementation:** Continue with dependency-aware workflow:
   - **Start with `read_code_mem`** to understand existing implementations and dependencies
   - **Optionally use `search_code_references`** for reference patterns (OPTIONAL - use for inspiration only, original paper specs take priority)
   - **Then `write_file`** to implement the new component
   - **Finally: Test** if needed

💡 **Key Point:** Always verify completion status before continuing with new file creation."""

    def _generate_error_guidance(self) -> str:
        """Generate error guidance for handling issues"""
        return """❌ Error detected during file implementation.

🔧 **Action Required:**
1. Review the error details above
2. Fix the identified issue
3. **Check if ALL files from the reproduction plan are implemented:**
   - **If YES:** Use `execute_python` or `execute_bash` to test the complete implementation, then respond "**implementation complete**" to end the conversation
   - **If NO:** Continue with proper development cycle for next file:
     - **Start with `read_code_mem`** to understand existing implementations
     - **Optionally use `search_code_references`** for reference patterns (OPTIONAL - for inspiration only)
     - **Then `write_file`** to implement properly
     - **Test** if needed
4. Ensure proper error handling in future implementations

💡 **Remember:** Always verify if all planned files are implemented before continuing with new file creation."""

    def _generate_no_tools_guidance(self, files_count: int) -> str:
        """Generate concise guidance when no tools are called"""
        return f"""⚠️ No tool calls detected in your response.

📊 **Current Progress:** {files_count} files implemented

🚨 **Action Required:** You must use tools. **FIRST check if ALL files from the reproduction plan are implemented:**

⚡ **Decision Process:**
1. **If ALL files are implemented:** Use `execute_python` or `execute_bash` to test the complete implementation, then respond "**implementation complete**" to end the conversation
2. **If MORE files need implementation:** Follow the development cycle:
   - **Start with `read_code_mem`** to understand existing implementations
   - **Optionally use `search_code_references`** for reference patterns (OPTIONAL - for inspiration only)
   - **Then `write_file`** to implement the new component
   - **Finally: Test** if needed

🚨 **Critical:** Always verify completion status first, then use appropriate tools - not just explanations!"""

    def _compile_user_response(self, tool_results: List[Dict], guidance: str) -> str:
        """Compile tool results and guidance into a single user response"""
        response_parts = []

        if tool_results:
            response_parts.append("🔧 **Tool Execution Results:**")
            for tool_result in tool_results:
                tool_name = tool_result["tool_name"]
                result_content = tool_result["result"]
                response_parts.append(
                    f"```\nTool: {tool_name}\nResult: {result_content}\n```"
                )

        if guidance:
            response_parts.append("\n" + guidance)

        return "\n\n".join(response_parts)

    # ==================== 7. Reporting and Output (Output Layer) ====================

    async def _generate_pure_code_final_report_with_concise_agents(
        self,
        iterations: int,
        elapsed_time: float,
        code_agent: CodeImplementationAgent,
        memory_agent: ConciseMemoryAgent,
    ):
        """Generate final report using concise agent statistics"""
        try:
            code_stats = code_agent.get_implementation_statistics()
            memory_stats = memory_agent.get_memory_statistics(
                code_stats["files_implemented_count"]
            )


            if self.mcp_agent:
                history_result = await self.mcp_agent.call_tool(
                    "get_operation_history", {"last_n": 100}
                )
                # Try to convert to dict if possible
                if isinstance(history_result, str):
                    try:
                        history_data = json.loads(history_result)
                    except Exception:
                        history_data = {"total_operations": 0, "history": []}
                elif isinstance(history_result, dict):
                    history_data = history_result
                else:
                    # Try to access as attribute or fallback
                    history_data = getattr(history_result, "__dict__", {"total_operations": 0, "history": []})
            else:
                history_data = {"total_operations": 0, "history": []}

            write_operations = 0
            files_created = []
            # Only operate if history_data is a dict and has 'history' as a key
            if isinstance(history_data, dict) and "history" in history_data:
                for item in history_data["history"]:
                    if isinstance(item, dict) and item.get("action") == "write_file":
                        write_operations += 1
                        file_path = item.get("details", {}).get("file_path", "unknown")
                        files_created.append(file_path)

            report = f"""
# Pure Code Implementation Completion Report (Write-File-Based Memory Mode)

## Execution Summary
- Implementation iterations: {iterations}
- Total elapsed time: {elapsed_time:.2f} seconds
- Files implemented: {code_stats['total_files_implemented']}
- File write operations: {write_operations}
- Total MCP operations: {history_data.get('total_operations', 0) if isinstance(history_data, dict) else 0}

## Read Tools Configuration
- Read tools enabled: {code_stats['read_tools_status']['read_tools_enabled']}
- Status: {code_stats['read_tools_status']['status']}
- Tools affected: {', '.join(code_stats['read_tools_status']['tools_affected'])}

## Agent Performance
### Code Implementation Agent
- Files tracked: {code_stats['files_implemented_count']}
- Technical decisions: {code_stats['technical_decisions_count']}
- Constraints tracked: {code_stats['constraints_count']}
- Architecture notes: {code_stats['architecture_notes_count']}
- Dependency analysis performed: {code_stats['dependency_analysis_count']}
- Files read for dependencies: {code_stats['files_read_for_dependencies']}
- Last summary triggered at file count: {code_stats['last_summary_file_count']}

### Concise Memory Agent (Write-File-Based)
- Last write_file detected: {memory_stats['last_write_file_detected']}
- Should clear memory next: {memory_stats['should_clear_memory_next']}
- Files implemented count: {memory_stats['implemented_files_tracked']}
- Current round: {memory_stats['current_round']}
- Concise mode active: {memory_stats['concise_mode_active']}
- Current round tool results: {memory_stats['current_round_tool_results']}
- Essential tools recorded: {memory_stats['essential_tools_recorded']}

## Files Created
"""
            for file_path in files_created[-20:]:
                report += f"- {file_path}\n"

            if len(files_created) > 20:
                report += f"... and {len(files_created) - 20} more files\n"

            report += """
## Architecture Features
✅ WRITE-FILE-BASED Memory Agent - Clear after each file generation
✅ After write_file: Clear history → Keep system prompt + initial plan + tool results
✅ Tool accumulation: read_code_mem, read_file, search_reference_code until next write_file
✅ Clean memory cycle: write_file → clear → accumulate → write_file → clear
✅ Essential tool recording with write_file detection
✅ Specialized agent separation for clean code organization
✅ MCP-compliant tool execution
✅ Production-grade code with comprehensive type hints
✅ Intelligent dependency analysis and file reading
✅ Automated read_file usage for implementation context
✅ Eliminates conversation clutter between file generations
✅ Focused memory for efficient next file generation
"""
            return report

        except Exception as e:
            self.logger.error(f"Failed to generate final report: {e}")
            return f"Failed to generate final report: {str(e)}"


async def main():
    """Main function for running the workflow"""
    # Configure root logger carefully to avoid duplicates
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

    workflow = CodeImplementationWorkflowWithIndex()

    print("=" * 60)
    print("Code Implementation Workflow with UNIFIED Reference Indexer")
    print("=" * 60)
    print("Select mode:")
    print("1. Test Code Reference Indexer Integration")
    print("2. Run Full Implementation Workflow")
    print("3. Run Implementation with Pure Code Mode")
    print("4. Test Read Tools Configuration")

    # mode_choice = input("Enter choice (1-4, default: 3): ").strip()

    # For testing purposes, we'll run the test first
    # if mode_choice == "4":
    #     print("Testing Read Tools Configuration...")

    #     # Create a test workflow normally
    #     test_workflow = CodeImplementationWorkflow()

    #     # Create a mock code agent for testing
    #     print("\n🧪 Testing with read tools DISABLED:")
    #     test_agent_disabled = CodeImplementationAgent(None, enable_read_tools=False)
    #     await test_agent_disabled.test_read_tools_configuration()

    #     print("\n🧪 Testing with read tools ENABLED:")
    #     test_agent_enabled = CodeImplementationAgent(None, enable_read_tools=True)
    #     await test_agent_enabled.test_read_tools_configuration()

    #     print("✅ Read tools configuration testing completed!")
    #     return

    # print("Running Code Reference Indexer Integration Test...")

    test_success = True
    if test_success:
        print("\n" + "=" * 60)
        print("🎉 UNIFIED Code Reference Indexer Integration Test PASSED!")
        print("🔧 Three-step process successfully merged into ONE tool")
        print("=" * 60)

        # Ask if user wants to continue with actual workflow
        print("\nContinuing with workflow execution...")

        # Use dynamic path detection to find the latest paper iteration
        plan_file = None
        target_directory = None

        # First, try to find papers directory
        paper_bases = ["deepcode_lab/papers", "papers"]
        project_root = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(project_root)

        for base in paper_bases:
            # Try relative path first
            papers_dir = Path(base)
            if not papers_dir.exists():
                # Try absolute path within project
                papers_dir = Path(parent_dir) / base.replace("/", os.sep)

            if papers_dir.exists():
                # Find the highest numbered directory with initial_plan.txt
                numbered_dirs = []
                for item in papers_dir.iterdir():
                    if item.is_dir() and item.name.isdigit():
                        plan_path = item / "initial_plan.txt"
                        if plan_path.exists():
                            numbered_dirs.append((int(item.name), str(item)))

                if numbered_dirs:
                    # Use the highest numbered directory
                    numbered_dirs.sort(reverse=True)
                    highest_num, highest_dir = numbered_dirs[0]
                    plan_file = str(Path(highest_dir) / "initial_plan.txt")
                    target_directory = str(Path(highest_dir))
                    break

        # Fallback to /1/ if no numbered directories found
        if not plan_file:
            plan_file = "deepcode_lab/papers/1/initial_plan.txt"
            target_directory = "deepcode_lab/papers/1/"

            if not os.path.exists(plan_file):
                plan_file = os.path.join(parent_dir, "deepcode_lab", "papers", "1", "initial_plan.txt")
                target_directory = os.path.join(parent_dir, "deepcode_lab", "papers", "1")

        print(f"📄 Plan file: {plan_file}")
        print(f"📂 Target directory: {target_directory}")
        print("Implementation Mode Selection:")
        print("1. Pure Code Implementation Mode (Recommended)")
        print("2. Iterative Implementation Mode")

        pure_code_mode = True
        mode_name = "Pure Code Implementation Mode with Memory Agent Architecture + Code Reference Indexer"
        print(f"Using: {mode_name}")

        # Configure read tools - modify this parameter to enable/disable read tools
        enable_read_tools = (
            True  # Set to False to disable read_file and read_code_mem tools
        )
        read_tools_status = "ENABLED" if enable_read_tools else "DISABLED"
        print(f"🔧 Read tools (read_file, read_code_mem): {read_tools_status}")

        # NOTE: To test without read tools, change the line above to:
        # enable_read_tools = False

        result = await workflow.run_workflow(
            plan_file,
            target_directory=target_directory,
            pure_code_mode=pure_code_mode,
            enable_read_tools=enable_read_tools,
        )

        print("=" * 60)
        print("Workflow Execution Results:")
        print(f"Status: {result['status']}")
        print(f"Mode: {mode_name}")

        if result["status"] == "success":
            print(f"Code Directory: {result['code_directory']}")
            print(f"MCP Architecture: {result.get('mcp_architecture', 'unknown')}")
            print("Execution completed!")
        else:
            print(f"Error Message: {result['message']}")

        print("=" * 60)
        print(
            "✅ Using Standard MCP Architecture with Memory Agent + Code Reference Indexer"
        )

    else:
        print("\n" + "=" * 60)
        print("❌ Code Reference Indexer Integration Test FAILED!")
        print("Please check the configuration and try again.")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
