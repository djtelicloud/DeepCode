"""
Code Planning Prompt
Creates detailed reproduction plans by integrating comprehensive analysis results.
Updated for GPT-5 Responses API with MCP tool support.
"""

CODE_PLANNING_PROMPT = """You are creating a DETAILED, COMPLETE reproduction plan by integrating comprehensive analysis results.

# INPUT
You receive two exhaustive analyses:
1. **Comprehensive Paper Analysis**: Complete paper structure, components, and requirements
2. **Complete Algorithm Extraction**: All algorithms, formulas, pseudocode, and technical details

Plus you can use segmented reading to access any specific paper sections needed for planning.

# INTELLIGENT DOCUMENT ACCESS

## IMPORTANT: Use Segmented Reading for Detailed Planning
When you need additional details beyond the provided analyses, use the intelligent segmentation system:

1. **Use read_document_segments tool** with these parameters:
   - query_type: "code_planning"
   - keywords: Specific to what you need, e.g., ["implementation", "code", "experiment", "setup", "configuration"]
   - max_segments: 3
   - max_total_chars: 8000

2. **This approach ensures** you access the most planning-relevant content without token limits

# OBJECTIVE
Create an implementation plan so detailed that a developer can reproduce the ENTIRE paper without reading it.

# CONTENT LENGTH CONTROL
⚠️ IMPORTANT: Generate a COMPLETE plan that includes ALL 5 sections without being cut off by token limits.

## Content Balance Guidelines:
- **Section 1 (File Structure)**: Brief overview (10% of content) - Focus on CORE implementation files only
- **Section 2 (Implementation Components)**: Detailed but concise (40% of content) - This is the PRIORITY section
- **Section 3 (Validation)**: Moderate detail (25% of content) - Essential experiments and tests
- **Section 4 (Environment)**: Brief but complete (10% of content) - All necessary dependencies
- **Section 5 (Implementation Strategy)**: Moderate detail (15% of content) - Step-by-step approach

## File Priority Guidelines:
🔧 **Implementation Priority Order**:
1. **FIRST**: Core algorithm/model files (highest priority)
2. **SECOND**: Supporting modules and utilities
3. **THIRD**: Experiment and evaluation scripts
4. **FOURTH**: Configuration and data handling
5. **LAST**: Documentation files (README.md, requirements.txt) - These should be created AFTER core implementation

Note: README and requirements.txt are maintenance files that depend on the final implementation, so plan them last.

# DETAILED SYNTHESIS PROCESS

## 1. MERGE ALL INFORMATION
Combine EVERYTHING from both analyses:
- Every algorithm with its pseudocode
- Every component with its architecture
- Every hyperparameter with its value
- Every experiment with expected results

## 2. MAP CONTENT TO IMPLEMENTATION

For each component you identify, specify how it will be implemented:

```
# DESIGN YOUR MAPPING: Connect paper content to code organization
[For each algorithm/component/method in the paper]:
  - What it does and where it's described in the paper
  - How you'll organize the code (files, classes, functions - your choice)
  - What specific formulas, algorithms, or procedures need implementation
  - Dependencies and relationships with other components
  - Implementation approach that makes sense for this specific paper
```

## 3. EXTRACT ALL TECHNICAL DETAILS

Identify every technical detail that needs implementation:

```
# COMPREHENSIVE TECHNICAL EXTRACTION:
[Gather all implementation-relevant details from the paper]:
  - All algorithms with complete pseudocode and mathematical formulations
  - All parameters, hyperparameters, and configuration values
  - All architectural details (if applicable to your paper type)
  - All experimental procedures and evaluation methods
  - Any implementation hints, tricks, or special considerations mentioned
```

# COMPREHENSIVE OUTPUT FORMAT

```yaml
complete_reproduction_plan:
  paper_info:
    title: "[Full paper title]"
    core_contribution: "[Main innovation being reproduced]"

  # SECTION 1: File Structure Design

  # DESIGN YOUR OWN STRUCTURE: Create a file organization that best serves this specific paper
  # - Analyze what the paper contains (algorithms, models, experiments, systems, etc.)
  # - Organize files and directories in the most logical way for implementation
  # - Create meaningful names and groupings based on paper content
  # - Keep it clean, intuitive, and focused on what actually needs to be implemented
  # - EXCLUDE documentation files (README.md, requirements.txt) - these come last

  file_structure: |
    [Design and specify your own project structure here - KEEP THIS BRIEF]
    [Focus ONLY on core implementation files, NOT documentation files]
    [Organize based on what this paper actually contains and needs]
    [Create directories and files that make sense for this specific implementation]
    [EXCLUDE: README.md, requirements.txt - these come last in implementation]

  # SECTION 2: Implementation Components

  # IDENTIFY AND SPECIFY: What needs to be implemented based on this paper
  # - List all algorithms, models, systems, or components mentioned
  # - Map each to implementation details and file locations
  # - Include formulas, pseudocode, and technical specifications
  # - Organize in whatever way makes sense for this paper

  implementation_components: |
    [List and specify all components that need implementation]
    [For each component: purpose, location, algorithms, formulas, technical details]
    [Organize and structure this based on the paper's actual content]

  # SECTION 3: Validation & Evaluation

  # DESIGN VALIDATION: How to verify the implementation works correctly
  # - Define what experiments, tests, or proofs are needed
  # - Specify expected results from the paper (figures, tables, theorems)
  # - Design validation approach appropriate for this paper's domain
  # - Include setup requirements and success criteria

  validation_approach: |
    [Design validation strategy appropriate for this paper]
    [Specify experiments, tests, or mathematical verification needed]
    [Define expected results and success criteria]
    [Include any special setup or evaluation requirements]

  # SECTION 4: Environment & Dependencies

  # SPECIFY REQUIREMENTS: What's needed to run this implementation
  # - Programming language and version requirements
  # - External libraries and exact versions (if specified in paper)
  # - Hardware requirements (GPU, memory, etc.)
  # - Any special setup or installation steps

  environment_setup: |
    [List all dependencies and environment requirements for this specific paper]
    [Include versions where specified, reasonable defaults where not]
    [Note any special hardware or software requirements]

  # SECTION 5: Implementation Strategy

  # PLAN YOUR APPROACH: How to implement this paper step by step
  # - Break down implementation into logical phases
  # - Identify dependencies between components
  # - Plan verification and testing at each stage
  # - Handle missing details with reasonable defaults

  implementation_strategy: |
    [Design your implementation approach for this specific paper]
    [Break into phases that make sense for this paper's components]
    [Plan testing and verification throughout the process]
    [Address any missing details or ambiguities in the paper]
```

BE EXHAUSTIVE. Every algorithm, every formula, every parameter, every file should be specified in complete detail."""

# Tool definitions for GPT-5 Responses API
def get_code_planning_tools():
    """Get tool definitions for code planning"""
    from config.gpt5_mcp_tool_definitions import GPT5MCPToolDefinitions
    from config.mcp_tool_definitions_index import MCPToolDefinitions

    # Get relevant tools for code planning
    tools = []

    # Add file operations for reading analysis results
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['read_file', 'read_multiple_files', 'write_file']
    ])

    # Add search and reference tools
    try:
        index_tools = MCPToolDefinitions.get_code_implementation_tools()
        tools.extend([
            tool for tool in index_tools
            if tool['name'] in ['search_code_references', 'get_indexes_overview', 'get_file_structure']
        ])
    except:
        pass  # Fallback if index tools not available

    # Add execution tools for processing and validation
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['execute_python']
    ])

    return tools

# Dynamic tool section for the prompt
CODE_PLANNING_TOOL_SECTION = """
# AVAILABLE TOOLS

You have access to the following tools for code planning:

{{DYNAMIC_TOOLS_SECTION}}

Use these tools to:
- Read and integrate analysis results from previous steps
- Search for implementation patterns and references
- Access code structure templates and examples
- Validate planning decisions with test implementations
- Generate and refine implementation blueprints
"""

def get_enhanced_code_planning_prompt():
    """Get the enhanced prompt with dynamic tool section"""
    tools = get_code_planning_tools()

    # Generate tool descriptions
    tool_descriptions = []
    for tool in tools:
        tool_desc = f"- **{tool['name']}**: {tool['description']}"
        tool_descriptions.append(tool_desc)

    dynamic_section = "\n".join(tool_descriptions)

    # Combine prompt with tool section
    enhanced_prompt = CODE_PLANNING_PROMPT + "\n\n" + CODE_PLANNING_TOOL_SECTION.replace(
        "{{DYNAMIC_TOOLS_SECTION}}", dynamic_section
    )

    return enhanced_prompt, tools
