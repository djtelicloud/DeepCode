"""
GitHub Download Prompt
Downloads GitHub repositories to specified directory structure.
Updated for GPT-5 Responses API with MCP tool support.
"""

GITHUB_DOWNLOAD_PROMPT = """You are an expert GitHub repository downloader.

Task: Download GitHub repositories to specified directory structure.

Process:
1. For each repository:
   - Create directory: {paper_dir}/code_base/
   - Download repository to directory

Requirements:
- Use available tools to execute download operations
- Monitor execution output for errors/warnings
- Verify download status through tool responses

Output Format:
{
    "downloaded_repos": [
        {
            "reference_number": "1",
            "paper_title": "paper title",
            "repo_url": "github repository URL",
            "save_path": "{paper_dir}/code_base/name_of_repo",
            "status": "success|failed",
            "notes": "relevant notes about download"
        }
    ],
    "summary": "Brief summary of download process"
}"""

# Tool definitions for GPT-5 Responses API
def get_github_download_tools():
    """Get tool definitions for GitHub repository downloading"""
    from config.gpt5_mcp_tool_definitions import GPT5MCPToolDefinitions
    from config.mcp_tool_definitions_index import MCPToolDefinitions

    # Get relevant tools for GitHub downloading
    tools = []

    # Add execution tools for git operations
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['execute_bash', 'execute_python']
    ])

    # Add file operations for directory management
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['read_file', 'write_file']
    ])

    # Add file structure tools
    try:
        index_tools = MCPToolDefinitions.get_code_implementation_tools()
        tools.extend([
            tool for tool in index_tools
            if tool['name'] in ['get_file_structure']
        ])
    except:
        pass  # Fallback if index tools not available

    return tools

# Dynamic tool section for the prompt
GITHUB_DOWNLOAD_TOOL_SECTION = """
# AVAILABLE TOOLS

You have access to the following tools for GitHub repository downloading:

{{DYNAMIC_TOOLS_SECTION}}

Use these tools to:
- Execute git clone commands
- Create directory structures
- Monitor download progress
- Verify downloaded repositories
- Handle download errors and retries
"""

def get_enhanced_github_download_prompt():
    """Get the enhanced prompt with dynamic tool section"""
    tools = get_github_download_tools()

    # Generate tool descriptions
    tool_descriptions = []
    for tool in tools:
        tool_desc = f"- **{tool['name']}**: {tool['description']}"
        tool_descriptions.append(tool_desc)

    dynamic_section = "\n".join(tool_descriptions)

    # Combine prompt with tool section
    enhanced_prompt = GITHUB_DOWNLOAD_PROMPT + "\n\n" + GITHUB_DOWNLOAD_TOOL_SECTION.replace(
        "{{DYNAMIC_TOOLS_SECTION}}", dynamic_section
    )

    return enhanced_prompt, tools
