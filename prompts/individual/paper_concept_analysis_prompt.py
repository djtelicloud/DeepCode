"""
Paper Concept Analysis Prompt
Performs comprehensive analysis of research paper structure and implementation requirements.
Updated for GPT-5 Responses API with MCP tool support.
"""

PAPER_CONCEPT_ANALYSIS_PROMPT = """You are doing a COMPREHENSIVE analysis of a research paper to understand its complete structure, contributions, and implementation requirements.

# OBJECTIVE
Map out the ENTIRE paper structure and identify ALL components that need implementation for successful reproduction.

# INTELLIGENT DOCUMENT READING STRATEGY

## IMPORTANT: Use Segmented Reading for Optimal Performance
Instead of reading the entire document at once (which may hit token limits), use the intelligent segmentation system:

1. **Use read_document_segments tool** with these parameters:
   - query_type: "concept_analysis"
   - keywords: ["introduction", "overview", "architecture", "system", "framework", "concept", "method"]
   - max_segments: 3
   - max_total_chars: 6000

2. **This will automatically find and retrieve** the most relevant sections for concept analysis without token overflow

3. **If you need additional sections**, make follow-up calls with different keywords like ["experiment", "evaluation", "results"] or ["conclusion", "discussion"]

# COMPREHENSIVE ANALYSIS PROTOCOL

## 1. INTELLIGENT PAPER STRUCTURAL ANALYSIS
Use the segmented reading approach to create a complete map:

```yaml
paper_structure_map:
  title: "[Full paper title]"

  sections:
    1_introduction:
      main_claims: "[What the paper claims to achieve]"
      problem_definition: "[Exact problem being solved]"

    2_related_work:
      key_comparisons: "[Methods this work builds upon or competes with]"

    3_method:  # May have multiple subsections
      subsections:
        3.1: "[Title and main content]"
        3.2: "[Title and main content]"
      algorithms_presented: "[List all algorithms by name]"

    4_experiments:
      environments: "[All test environments/datasets]"
      baselines: "[All comparison methods]"
      metrics: "[All evaluation metrics used]"

    5_results:
      main_findings: "[Key results that prove the method works]"
      tables_figures: "[Important result tables/figures to reproduce]"
```

## 2. METHOD DECOMPOSITION
For the main method/approach:

```yaml
method_decomposition:
  method_name: "[Full name and acronym]"

  core_components:  # Break down into implementable pieces
    component_1:
      name: "[e.g., State Importance Estimator]"
      purpose: "[Why this component exists]"
      paper_section: "[Where it's described]"

    component_2:
      name: "[e.g., Policy Refinement Module]"
      purpose: "[Its role in the system]"
      paper_section: "[Where it's described]"

  component_interactions:
    - "[How component 1 feeds into component 2]"
    - "[Data flow between components]"

  theoretical_foundation:
    key_insight: "[The main theoretical insight]"
    why_it_works: "[Intuitive explanation]"
```

## 3. IMPLEMENTATION REQUIREMENTS MAPPING
Map paper content to code requirements:

```yaml
implementation_map:
  algorithms_to_implement:
    - algorithm: "[Name from paper]"
      section: "[Where defined]"
      complexity: "[Simple/Medium/Complex]"
      dependencies: "[What it needs to work]"

  models_to_build:
    - model: "[Neural network or other model]"
      architecture_location: "[Section describing it]"
      purpose: "[What this model does]"

  data_processing:
    - pipeline: "[Data preprocessing needed]"
      requirements: "[What the data should look like]"

  evaluation_suite:
    - metric: "[Metric name]"
      formula_location: "[Where it's defined]"
      purpose: "[What it measures]"
```

## 4. EXPERIMENT REPRODUCTION PLAN
Identify ALL experiments needed:

```yaml
experiments_analysis:
  main_results:
    - experiment: "[Name/description]"
      proves: "[What claim this validates]"
      requires: "[Components needed to run this]"
      expected_outcome: "[Specific numbers/trends]"

  ablation_studies:
    - study: "[What is being ablated]"
      purpose: "[What this demonstrates]"

  baseline_comparisons:
    - baseline: "[Method name]"
      implementation_required: "[Yes/No/Partial]"
      source: "[Where to find implementation]"
```

## 5. CRITICAL SUCCESS FACTORS
What defines successful reproduction:

```yaml
success_criteria:
  must_achieve:
    - "[Primary result that must be reproduced]"
    - "[Core behavior that must be demonstrated]"

  should_achieve:
    - "[Secondary results that validate the method]"

  validation_evidence:
    - "[Specific figure/table to reproduce]"
    - "[Qualitative behavior to demonstrate]"
```

# OUTPUT FORMAT
```yaml
comprehensive_paper_analysis:
  executive_summary:
    paper_title: "[Full title]"
    core_contribution: "[One sentence summary]"
    implementation_complexity: "[Low/Medium/High]"
    estimated_components: "[Number of major components to build]"

  complete_structure_map:
    [FULL SECTION BREAKDOWN AS ABOVE]

  method_architecture:
    [DETAILED COMPONENT BREAKDOWN]

  implementation_requirements:
    [ALL ALGORITHMS, MODELS, DATA, METRICS]

  reproduction_roadmap:
    phase_1: "[What to implement first]"
    phase_2: "[What to build next]"
    phase_3: "[Final components and validation]"

  validation_checklist:
    - "[ ] [Specific result to achieve]"
    - "[ ] [Behavior to demonstrate]"
    - "[ ] [Metric to match]"
```

BE THOROUGH. Miss nothing. The output should be a complete blueprint for reproduction."""

# Tool definitions for GPT-5 Responses API
def get_paper_concept_analysis_tools():
    """Get tool definitions for paper concept analysis"""
    from config.gpt5_mcp_tool_definitions import GPT5MCPToolDefinitions

    # Get relevant tools for concept analysis
    tools = []

    # Add file reading tools for comprehensive paper analysis
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['read_file', 'read_multiple_files']
    ])

    # Add execution tools for data processing and structure analysis
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['execute_python']
    ])

    return tools

# Dynamic tool section for the prompt
PAPER_CONCEPT_ANALYSIS_TOOL_SECTION = """
# AVAILABLE TOOLS

You have access to the following tools for comprehensive paper analysis:

{{DYNAMIC_TOOLS_SECTION}}

Use these tools to:
- Read paper sections with intelligent segmentation
- Search for specific concepts and methodologies
- Analyze paper structure and organization
- Cross-reference with existing code patterns
- Process and structure analysis results
"""

def get_enhanced_paper_concept_analysis_prompt():
    """Get the enhanced prompt with dynamic tool section"""
    tools = get_paper_concept_analysis_tools()

    # Generate tool descriptions
    tool_descriptions = []
    for tool in tools:
        tool_desc = f"- **{tool['name']}**: {tool['description']}"
        tool_descriptions.append(tool_desc)

    dynamic_section = "\n".join(tool_descriptions)

    # Combine prompt with tool section
    enhanced_prompt = PAPER_CONCEPT_ANALYSIS_PROMPT + "\n\n" + PAPER_CONCEPT_ANALYSIS_TOOL_SECTION.replace(
        "{{DYNAMIC_TOOLS_SECTION}}", dynamic_section
    )

    return enhanced_prompt, tools
