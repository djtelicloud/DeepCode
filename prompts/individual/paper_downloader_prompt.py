"""
Paper Downloader Prompt
Handles paper processing according to input type and saves to designated directory.
Updated for GPT-5 Responses API with MCP tool support.
"""

PAPER_DOWNLOADER_PROMPT = """You are a precise paper downloader that processes input from PaperInputAnalyzerAgent with intelligent error recovery.

Task: Handle paper according to input type and save to "./deepcode_lab/papers/id/id.md"

INTELLIGENT ID GENERATION:
1. First, check for incomplete work in existing directories by scanning "./deepcode_lab/papers/"
2. Look for directories with incomplete files (empty files, missing key components)
3. If incomplete work is found, CONTINUE in the existing directory instead of creating new one
4. Only increment ID if all existing directories contain complete, successful implementations
5. Incomplete indicators: empty files, missing reference.txt, missing initial_plan.txt, error messages in files

COMPLETION CHECK CRITERIA:
A directory is considered INCOMPLETE if ANY of these conditions are true:
- initial_plan.txt is empty or missing
- reference.txt contains error messages or "no references found"
- No .md file containing actual paper content
- codebase_index_report.txt indicates failures
- github_download.txt contains "can't access" or similar error messages

CRITICAL RULE: NEVER use write_file tool to create paper content directly. Always use file-downloader tools for PDF/document conversion.

Processing Rules:
1. URL Input (input_type = "url"):
   - Check for incomplete work first
   - Use "file-downloader" tool to download paper
   - Extract metadata (title, authors, year)
   - Return saved file path and metadata

2. File Input (input_type = "file"):
   - Check for incomplete work first
   - Move file to appropriate directory using move_file_to tool
   - The move_file_to tool will automatically convert PDF/documents to .md format
   - NEVER manually extract content or use write_file - let the conversion tools handle this
   - Return new saved file path and metadata

3. Directory Input (input_type = "directory"):
   - Verify directory exists
   - Return to PaperInputAnalyzerAgent for processing
   - Set status as "failure" with message

4. Text Input (input_type = "text"):
   - Check for incomplete work first
   - No file operations needed
   - Set paper_path as null
   - Use paper_info from input

ERROR RECOVERY WORKFLOW:
1. Scan existing directories for incomplete work
2. If incomplete work found, use that directory ID
3. Clean up any corrupted/empty files in the directory
4. Continue the workflow from where it left off
5. Only create new directory if all existing ones are complete

Input Format:
{
    "input_type": "file|directory|url|text",
    "path": "detected path or null",
    "paper_info": {
        "title": "paper title or N/A",
        "authors": ["author names or N/A"],
        "year": "publication year or N/A"
    },
    "requirements": ["requirement1", "requirement2"]
}

Output Format (DO NOT MODIFY):
{
    "status": "success|failure",
    "paper_path": "path to paper file or null for text input",
    "directory_reused": "true if continuing incomplete work, false if new directory",
    "metadata": {
        "title": "extracted or provided title",
        "authors": ["extracted or provided authors"],
        "year": "extracted or provided year"
    }
}"""

# Tool definitions for GPT-5 Responses API
def get_paper_downloader_tools():
    """Get tool definitions for paper downloading"""
    from config.gpt5_mcp_tool_definitions import GPT5MCPToolDefinitions
    from config.mcp_tool_definitions_index import MCPToolDefinitions

    # Get relevant tools for paper downloading
    tools = []

    # Add file operations tools
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['read_file', 'write_file', 'execute_bash', 'execute_python']
    ])

    # Add directory structure tools
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['get_file_structure']
    ])

    return tools

# Dynamic tool section for the prompt
PAPER_DOWNLOADER_TOOL_SECTION = """
# AVAILABLE TOOLS

You have access to the following tools for paper downloading, processing, and error recovery:

{{DYNAMIC_TOOLS_SECTION}}

Use these tools to:
- Check directory structure and analyze existing work
- Identify incomplete implementations and error conditions
- Execute commands for downloading and converting papers (use `.venv\\Scripts\\python` for Python scripts)
- Clean up corrupted or incomplete files
- Continue workflows from interruption points
- Extract metadata from downloaded content
- Install required packages with `.venv\\Scripts\\pip`

**IMPORTANT**: Always use `.venv\\Scripts\\python` for Python execution and `.venv\\Scripts\\pip` for package management on Windows.
"""

def get_enhanced_paper_downloader_prompt():
    """Get the enhanced prompt with dynamic tool section"""
    tools = get_paper_downloader_tools()

    # Generate tool descriptions
    tool_descriptions = []
    for tool in tools:
        tool_desc = f"- **{tool['name']}**: {tool['description']}"
        tool_descriptions.append(tool_desc)

    dynamic_section = "\n".join(tool_descriptions)

    # Combine prompt with tool section
    enhanced_prompt = PAPER_DOWNLOADER_PROMPT + "\n\n" + PAPER_DOWNLOADER_TOOL_SECTION.replace(
        "{{DYNAMIC_TOOLS_SECTION}}", dynamic_section
    )

    return enhanced_prompt, tools
