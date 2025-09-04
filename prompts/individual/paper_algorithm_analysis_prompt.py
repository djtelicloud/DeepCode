"""
Paper Algorithm Analysis Prompt
Extracts complete implementation details from research papers.
Updated for GPT-5 Responses API with MCP tool support.
"""

PAPER_ALGORITHM_ANALYSIS_PROMPT = """You are extracting COMPLETE implementation details from a research paper. Your goal is to capture EVERY algorithm, formula, and technical detail needed for perfect reproduction.

# INTELLIGENT DOCUMENT READING STRATEGY

## IMPORTANT: Use Segmented Reading for Algorithm Extraction
To avoid token limits and efficiently extract algorithm details, use the intelligent segmentation system:

1. **Primary Algorithm Extraction** - Use read_document_segments tool with:
   - query_type: "algorithm_extraction"
   - keywords: ["algorithm", "method", "procedure", "formula", "equation", "implementation"]
   - max_segments: 3
   - max_total_chars: 6000

2. **Supplementary Details** - Make additional calls if needed with:
   - keywords: ["hyperparameter", "training", "optimization", "loss", "objective"]
   - keywords: ["experiment", "setup", "configuration", "parameter"]

3. **This approach ensures** you get the most algorithm-relevant content without missing critical details

# DETAILED EXTRACTION PROTOCOL

## 1. INTELLIGENT ALGORITHM SCAN
Use the segmented reading approach to focus on algorithm sections:
- Method/Algorithm sections (captured automatically by segmentation)
- Implementation Details (targeted retrieval)
- Hyperparameters and training details (focused extraction)

## 2. ALGORITHM DEEP EXTRACTION
For EVERY algorithm/method/procedure mentioned:

### Algorithm Structure
```yaml
algorithm_name: "[Exact name from paper]"
section: "[e.g., Section 3.2]"
algorithm_box: "[e.g., Algorithm 1 on page 4]"

pseudocode: |
  [COPY THE EXACT PSEUDOCODE FROM PAPER]
  Input: ...
  Output: ...
  1. Initialize ...
  2. For each ...
     2.1 Calculate ...
  [Keep exact formatting and numbering]

mathematical_formulation:
  - equation: "[Copy formula EXACTLY, e.g., L = L_task + λ*L_explain]"
    equation_number: "[e.g., Eq. 3]"
    where:
      L_task: "task loss"
      L_explain: "explanation loss"
      λ: "weighting parameter (default: 0.5)"

step_by_step_breakdown:
  1. "[Detailed explanation of what step 1 does]"
  2. "[What step 2 computes and why]"

implementation_details:
  - "Uses softmax temperature τ = 0.1"
  - "Gradient clipping at norm 1.0"
  - "Initialize weights with Xavier uniform"
```

## 3. COMPONENT EXTRACTION
For EVERY component/module mentioned:

### Component Details
```yaml
component_name: "[e.g., Mask Network, Critic Network]"
purpose: "[What this component does in the system]"
architecture:
  input: "[shape and meaning]"
  layers:
    - "[Conv2d(3, 64, kernel=3, stride=1)]"
    - "[ReLU activation]"
    - "[BatchNorm2d(64)]"
  output: "[shape and meaning]"

special_features:
  - "[Any unique aspects]"
  - "[Special initialization]"
```

## 4. TRAINING PROCEDURE
Extract the COMPLETE training process:

```yaml
training_loop:
  outer_iterations: "[number or condition]"
  inner_iterations: "[number or condition]"

  steps:
    1. "Sample batch of size B from buffer"
    2. "Compute importance weights using..."
    3. "Update policy with loss..."

  loss_functions:
    - name: "policy_loss"
      formula: "[exact formula]"
      components: "[what each term means]"

  optimization:
    optimizer: "Adam"
    learning_rate: "3e-4"
    lr_schedule: "linear decay to 0"
    gradient_norm: "clip at 0.5"
```

## 5. HYPERPARAMETERS HUNT
Search EVERYWHERE (text, tables, captions) for:

```yaml
hyperparameters:
  # Training
  batch_size: 64
  buffer_size: 1e6
  discount_gamma: 0.99

  # Architecture
  hidden_units: [256, 256]
  activation: "ReLU"

  # Algorithm-specific
  explanation_weight: 0.5
  exploration_bonus_scale: 0.1
  reset_probability: 0.3

  # Found in:
  location_references:
    - "batch_size: Table 1"
    - "hidden_units: Section 4.1"
```

# OUTPUT FORMAT
```yaml
complete_algorithm_extraction:
  paper_structure:
    method_sections: "[3, 3.1, 3.2, 3.3, 4]"
    algorithm_count: "[total number found]"

  main_algorithm:
    [COMPLETE DETAILS AS ABOVE]

  supporting_algorithms:
    - [EACH SUPPORTING ALGORITHM WITH FULL DETAILS]

  components:
    - [EVERY COMPONENT WITH ARCHITECTURE]

  training_details:
    [COMPLETE TRAINING PROCEDURE]

  all_hyperparameters:
    [EVERY PARAMETER WITH VALUE AND SOURCE]

  implementation_notes:
    - "[Any implementation hint from paper]"
    - "[Tricks mentioned in text]"

  missing_but_critical:
    - "[What's not specified but essential]"
    - "[With suggested defaults]"
```

BE EXHAUSTIVE. A developer should be able to implement the ENTIRE paper using only your extraction."""

# Tool definitions for GPT-5 Responses API
def get_paper_algorithm_analysis_tools():
    """Get tool definitions for paper algorithm analysis"""
    from config.gpt5_mcp_tool_definitions import GPT5MCPToolDefinitions

    # Get relevant tools for algorithm analysis
    tools = []

    # Add file reading tools for paper analysis
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['read_file', 'read_multiple_files']
    ])

    # Add execution tools for data processing
    tools.extend([
        tool for tool in GPT5MCPToolDefinitions.get_code_implementation_tools()
        if tool['name'] in ['execute_python']
    ])

    return tools

# Dynamic tool section for the prompt
PAPER_ALGORITHM_ANALYSIS_TOOL_SECTION = """
# AVAILABLE TOOLS

You have access to the following tools for algorithm analysis:

{{DYNAMIC_TOOLS_SECTION}}

Use these tools to:
- Read paper content with selective line ranges
- Search for specific algorithm sections and mathematical formulas
- Extract hyperparameters from tables and text
- Process and structure extracted information (use `.venv\\Scripts\\python` for Python scripts)
- Cross-reference with indexed code patterns

**IMPORTANT**: Always use `.venv\\Scripts\\python` for Python execution when processing data or running analysis scripts.
"""

def get_enhanced_paper_algorithm_analysis_prompt():
    """Get the enhanced prompt with dynamic tool section"""
    tools = get_paper_algorithm_analysis_tools()

    # Generate tool descriptions
    tool_descriptions = []
    for tool in tools:
        tool_desc = f"- **{tool['name']}**: {tool['description']}"
        tool_descriptions.append(tool_desc)

    dynamic_section = "\n".join(tool_descriptions)

    # Combine prompt with tool section
    enhanced_prompt = PAPER_ALGORITHM_ANALYSIS_PROMPT + "\n\n" + PAPER_ALGORITHM_ANALYSIS_TOOL_SECTION.replace(
        "{{DYNAMIC_TOOLS_SECTION}}", dynamic_section
    )

    return enhanced_prompt, tools
