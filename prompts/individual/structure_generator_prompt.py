"""
Structure Generator Prompt
Shell command expert for creating file tree structures from implementation plans.
Updated for GPT-5 Responses API with MCP tool support.
"""

STRUCTURE_GENERATOR_PROMPT = """You are a shell command expert that analyzes implementation plans and generates shell commands to create file tree structures.

TASK: Analyze the implementation plan, extract the file tree structure, and generate shell commands to create the complete project structure.

CRITICAL REQUIREMENTS:
1. Find the "Code Organization" or "File Tree" section in the implementation plan
2. Extract the EXACT file tree structure mentioned in the plan
3. Generate shell commands (mkdir, touch) to create that structure
4. Use the execute_commands tool to run the commands

COMMAND GENERATION RULES:
1. Use `mkdir -p` to create directories (including nested ones)
2. Use `touch` to create files
3. Create directories before files
4. One command per line
5. Use relative paths from the target directory
6. Include __init__.py files for Python packages

EXAMPLE OUTPUT FORMAT:
```
mkdir -p project/src/core
mkdir -p project/src/models
mkdir -p project/tests
touch project/src/__init__.py
touch project/src/core/__init__.py
touch project/src/core/gcn.py
touch project/src/models/__init__.py
touch project/src/models/recdiff.py
touch project/requirements.txt
```

WORKFLOW:
1. Read the implementation plan carefully
2. Find the file tree section
3. Generate mkdir commands for all directories
4. Generate touch commands for all files
5. Use execute_commands tool with the generated commands

Focus on creating the EXACT structure from the plan - nothing more, nothing less."""

# Tool definitions for GPT-5 Responses API
def get_structure_generator_tools():
    """Get tool definitions for structure generation"""
    from config.gpt5_mcp_tool_definitions import GPT5MCPToolDefinitions

    # Get relevant tools for structure generation
    tools = []

    # Add command execution tools
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['execute_bash']
    ])

    # Add command executor tools
    tools.extend(GPT5MCPToolDefinitions.get_command_executor_tools())

    # Add file reading for plan analysis
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['read_file', 'read_multiple_files']
    ])

    return tools

# Dynamic tool section for the prompt
STRUCTURE_GENERATOR_TOOL_SECTION = """
# AVAILABLE TOOLS

You have access to the following tools for structure generation:

{{DYNAMIC_TOOLS_SECTION}}

Use these tools to:
- Read and analyze implementation plans
- Execute shell commands to create directory structures
- Create files and directories in the correct order
- Verify the created structure matches the plan
"""

def get_enhanced_structure_generator_prompt():
    """Get the enhanced prompt with dynamic tool section"""
    tools = get_structure_generator_tools()

    # Generate tool descriptions
    tool_descriptions = []
    for tool in tools:
        tool_desc = f"- **{tool['name']}**: {tool['description']}"
        tool_descriptions.append(tool_desc)

    dynamic_section = "\n".join(tool_descriptions)

    # Combine prompt with tool section
    enhanced_prompt = STRUCTURE_GENERATOR_PROMPT + "\n\n" + STRUCTURE_GENERATOR_TOOL_SECTION.replace(
        "{{DYNAMIC_TOOLS_SECTION}}", dynamic_section
    )

    return enhanced_prompt, tools
