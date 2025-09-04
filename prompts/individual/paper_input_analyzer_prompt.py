"""
Paper Input Analyzer Prompt
Analyzes input text and identifies file paths/URLs to determine appropriate input type.
Updated for GPT-5 Responses API with MCP tool support.
"""

PAPER_INPUT_ANALYZER_PROMPT = """You are a precise input analyzer for paper-to-code tasks. You MUST return only a JSON object with no additional text.

Task: Analyze input text and identify file paths/URLs to determine appropriate input type.

Input Analysis Rules:
1. Path Detection:
   - Scan input text for file paths or URLs
   - Use first valid path/URL if multiple found
   - Treat as text input if no valid path/URL found

2. Path Type Classification:
   - URL (starts with http:// or https://): input_type = "url", path = "detected URL"
   - PDF file path: input_type = "file", path = "detected file path"
   - Directory path: input_type = "directory", path = "detected directory path"
   - No path/URL detected: input_type = "text", path = null

3. Requirements Analysis:
   - Extract ONLY requirements from additional_input
   - DO NOT modify or interpret requirements

CRITICAL OUTPUT RESTRICTIONS:
- RETURN ONLY RAW JSON - NO TEXT BEFORE OR AFTER
- NO markdown code blocks (```json)
- NO explanatory text or descriptions
- NO tool call information
- NO analysis summaries
- JUST THE JSON OBJECT BELOW

{
    "input_type": "text|file|directory|url",
    "path": "detected path or URL or null",
    "paper_info": {
        "title": "N/A for text input",
        "authors": ["N/A for text input"],
        "year": "N/A for text input"
    },
    "requirements": [
        "exact requirement from additional_input"
    ]
}"""

# Tool definitions for GPT-5 Responses API
def get_paper_input_analyzer_tools():
    """Get tool definitions for paper input analysis"""
    from config.gpt5_mcp_tool_definitions import GPT5MCPToolDefinitions

    # Get relevant tools for input analysis
    tools = []

    # Add file operations tools
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['read_file', 'read_multiple_files']
    ])

    # Add search tools if needed
    # Note: Search tools would be added from mcp_tool_definitions_index if needed

    return tools

# Dynamic tool section for the prompt
PAPER_INPUT_ANALYZER_TOOL_SECTION = """
# AVAILABLE TOOLS

You have access to the following tools for analyzing input:

{{DYNAMIC_TOOLS_SECTION}}

Use these tools to:
- Read file paths when detected
- Validate file existence
- Extract metadata from documents
"""

def get_enhanced_paper_input_analyzer_prompt():
    """Get the enhanced prompt with dynamic tool section"""
    tools = get_paper_input_analyzer_tools()

    # Generate tool descriptions
    tool_descriptions = []
    for tool in tools:
        tool_desc = f"- **{tool['name']}**: {tool['description']}"
        tool_descriptions.append(tool_desc)

    dynamic_section = "\n".join(tool_descriptions)

    # Combine prompt with tool section
    enhanced_prompt = PAPER_INPUT_ANALYZER_PROMPT + "\n\n" + PAPER_INPUT_ANALYZER_TOOL_SECTION.replace(
        "{{DYNAMIC_TOOLS_SECTION}}", dynamic_section
    )

    return enhanced_prompt, tools
