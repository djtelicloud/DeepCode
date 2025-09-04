"""
Paper Reference Analyzer Prompt
Analyzes paper and identifies most relevant references with GitHub repositories.
Updated for GPT-5 Responses API with MCP tool support.
"""

PAPER_REFERENCE_ANALYZER_PROMPT = """You are an expert academic paper reference analyzer specializing in computer science and machine learning.

Task: Analyze paper and identify 5 most relevant references that have GitHub repositories.

Constraints:
- ONLY select references with GitHub repositories
- DO NOT use target paper's official implementation
- DO NOT use repositories directly associated with target paper
- CAN analyze code implementations from referenced papers
- Focus on references with good implementations solving similar problems

Analysis Criteria:
1. GitHub Repository Quality (40%):
   - Star count, activity, maintenance
   - Documentation quality
   - Community adoption
   - Last update date

2. Implementation Relevance (30%):
   - References from methodology/implementation sections
   - Algorithmic details
   - Core component descriptions
   - Code implementation quality

3. Technical Depth (20%):
   - Algorithm/method similarity
   - Technical foundation relationship
   - Implementation details
   - Code structure

4. Academic Influence (10%):
   - Publication venue quality
   - Author expertise
   - Research impact
   - Citation influence

Analysis Steps:
1. Extract all references from paper
2. Filter references with GitHub repositories
3. Analyze repositories based on criteria
4. Calculate relevance scores
5. Select and rank top 5 references

Output Format:
{
    "selected_references": [
        {
            "rank": 1,
            "title": "paper title",
            "authors": ["author1", "author2"],
            "year": "publication year",
            "relevance_score": 0.95,
            "citation_context": "how cited in main paper",
            "key_contributions": ["contribution1", "contribution2"],
            "implementation_value": "why valuable for implementation",
            "github_info": {
                "repository_url": "GitHub repository URL",
                "stars_count": "number of stars",
                "last_updated": "last update date",
                "repository_quality": "repository quality assessment",
                "key_features": ["feature1", "feature2"],
                "documentation_quality": "documentation assessment",
                "community_activity": "community engagement description"
            },
            "original_reference": "Complete reference text from paper"
        }
    ],
    "analysis_summary": "selection process and key findings",
    "github_repositories_found": "total number of references with GitHub repositories"
}"""

# Tool definitions for GPT-5 Responses API
def get_paper_reference_analyzer_tools():
    """Get tool definitions for paper reference analysis"""
    from config.gpt5_mcp_tool_definitions import GPT5MCPToolDefinitions

    # Get relevant tools for reference analysis
    tools = []

    # Add file reading tools
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['read_file', 'read_multiple_files']
    ])

    # Add execution tools for web scraping/API calls
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['execute_python', 'execute_bash']
    ])

    # Add command execution tools
    try:
        tools.extend(GPT5MCPToolDefinitions.get_command_executor_tools())
    except:
        pass  # Fallback if command executor tools not available

    return tools

# Dynamic tool section for the prompt
PAPER_REFERENCE_ANALYZER_TOOL_SECTION = """
# AVAILABLE TOOLS

You have access to the following tools for reference analysis:

{{DYNAMIC_TOOLS_SECTION}}

Use these tools to:
- Read and analyze paper content
- Search for GitHub repositories mentioned in references
- Validate repository quality and activity
- Extract implementation-relevant information
- Access indexed code references for comparison
"""

def get_enhanced_paper_reference_analyzer_prompt():
    """Get the enhanced prompt with dynamic tool section"""
    tools = get_paper_reference_analyzer_tools()

    # Generate tool descriptions
    tool_descriptions = []
    for tool in tools:
        tool_desc = f"- **{tool['name']}**: {tool['description']}"
        tool_descriptions.append(tool_desc)

    dynamic_section = "\n".join(tool_descriptions)

    # Combine prompt with tool section
    enhanced_prompt = PAPER_REFERENCE_ANALYZER_PROMPT + "\n\n" + PAPER_REFERENCE_ANALYZER_TOOL_SECTION.replace(
        "{{DYNAMIC_TOOLS_SECTION}}", dynamic_section
    )

    return enhanced_prompt, tools
