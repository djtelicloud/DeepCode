"""
Prompt templates for the DeepCode agent system.
REFACTORED: Individual prompts moved to prompts/individual/ directory.
UPDATED for GPT-5 Responses API with MCP tool support.

This file maintains backward compatibility while importing from individual files.

RECENT UPDATES:
1. Refactored into individual prompt files for better maintainability
2. Added GPT-5 Responses API support with dynamic tool sections
3. Updated MCP tool definitions with latest available tools
4. Enhanced prompts with intelligent tool usage patterns
5. Added dynamic tool section generation for each prompt
6. Maintained backward compatibility for existing imports

核心改进：
- Individual prompt files with tool definitions
- Dynamic tool sections for GPT-5 Responses API
- Enhanced MCP tool integration
- Backward compatibility maintained
"""

# Import all prompts from individual files
from .individual import (  # Basic prompts (backward compatibility); Enhanced prompts with GPT-5 tool support; Tool functions
    CHAT_AGENT_PLANNING_PROMPT, CODE_IMPLEMENTATION_PROMPT,
    CODE_PLANNING_PROMPT, CONVERSATION_SUMMARY_PROMPT,
    GENERAL_CODE_IMPLEMENTATION_SYSTEM_PROMPT, GITHUB_DOWNLOAD_PROMPT,
    PAPER_ALGORITHM_ANALYSIS_PROMPT, PAPER_CONCEPT_ANALYSIS_PROMPT,
    PAPER_DOWNLOADER_PROMPT, PAPER_INPUT_ANALYZER_PROMPT,
    PAPER_REFERENCE_ANALYZER_PROMPT, PURE_CODE_IMPLEMENTATION_SYSTEM_PROMPT,
    SLIDING_WINDOW_SYSTEM_PROMPT, STRUCTURE_GENERATOR_PROMPT,
    get_chat_agent_planning_tools, get_code_implementation_tools,
    get_code_planning_tools, get_conversation_summary_tools,
    get_enhanced_chat_agent_planning_prompt,
    get_enhanced_code_implementation_prompt, get_enhanced_code_planning_prompt,
    get_enhanced_conversation_summary_prompt,
    get_enhanced_general_code_implementation_prompt,
    get_enhanced_github_download_prompt,
    get_enhanced_paper_algorithm_analysis_prompt,
    get_enhanced_paper_concept_analysis_prompt,
    get_enhanced_paper_downloader_prompt,
    get_enhanced_paper_input_analyzer_prompt,
    get_enhanced_paper_reference_analyzer_prompt,
    get_enhanced_pure_code_implementation_prompt,
    get_enhanced_sliding_window_prompt,
    get_enhanced_structure_generator_prompt,
    get_general_code_implementation_tools, get_github_download_tools,
    get_paper_algorithm_analysis_tools, get_paper_concept_analysis_tools,
    get_paper_downloader_tools, get_paper_input_analyzer_tools,
    get_paper_reference_analyzer_tools, get_pure_code_implementation_tools,
    get_sliding_window_tools, get_structure_generator_tools)

# Backward compatibility aliases
PURE_CODE_IMPLEMENTATION_SYSTEM_PROMPT_INDEX = PURE_CODE_IMPLEMENTATION_SYSTEM_PROMPT

# GPT-5 Enhanced Prompt Functions
# These functions provide prompts with dynamic tool sections for GPT-5 Responses API

def get_prompt_with_tools(prompt_name):
    """
    Get enhanced prompt with tools for GPT-5 Responses API

    Args:
        prompt_name: Name of the prompt to enhance

    Returns:
        tuple: (enhanced_prompt, tools_list)
    """
    prompt_functions = {
        'paper_input_analyzer': get_enhanced_paper_input_analyzer_prompt,
        'paper_downloader': get_enhanced_paper_downloader_prompt,
        'paper_reference_analyzer': get_enhanced_paper_reference_analyzer_prompt,
        'github_download': get_enhanced_github_download_prompt,
        'paper_algorithm_analysis': get_enhanced_paper_algorithm_analysis_prompt,
        'paper_concept_analysis': get_enhanced_paper_concept_analysis_prompt,
        'code_planning': get_enhanced_code_planning_prompt,
        'pure_code_implementation': get_enhanced_pure_code_implementation_prompt,
        'general_code_implementation': get_enhanced_general_code_implementation_prompt,
        'chat_agent_planning': get_enhanced_chat_agent_planning_prompt,
        'structure_generator': get_enhanced_structure_generator_prompt,
        'code_implementation': get_enhanced_code_implementation_prompt,
        'conversation_summary': get_enhanced_conversation_summary_prompt,
        'sliding_window': get_enhanced_sliding_window_prompt,
    }

    if prompt_name in prompt_functions:
        return prompt_functions[prompt_name]()
    else:
        raise ValueError(f"Unknown prompt name: {prompt_name}")

def get_available_enhanced_prompts():
    """Get list of all available enhanced prompts with tool support"""
    return [
        'paper_input_analyzer',
        'paper_downloader',
        'paper_reference_analyzer',
        'github_download',
        'paper_algorithm_analysis',
        'paper_concept_analysis',
        'code_planning',
        'pure_code_implementation',
        'general_code_implementation',
        'chat_agent_planning',
        'structure_generator',
        'code_implementation',
        'conversation_summary',
        'sliding_window'
    ]

# Traditional prompt definitions (non-segmented versions)
PAPER_ALGORITHM_ANALYSIS_PROMPT_TRADITIONAL = """You are extracting COMPLETE implementation details from a research paper. Your goal is to capture EVERY algorithm, formula, and technical detail needed for perfect reproduction.

# DOCUMENT READING STRATEGY

## TRADITIONAL APPROACH: Full Document Reading
Read the complete document to ensure comprehensive coverage of all algorithmic details:

1. **Locate and read the markdown (.md) file** in the paper directory
2. **Analyze the entire document** to capture all algorithms, methods, and formulas
3. **Extract complete implementation details** without missing any components

# DETAILED EXTRACTION PROTOCOL

## 1. COMPREHENSIVE ALGORITHM SCAN
Read through the entire document systematically:
- Method/Algorithm sections
- Implementation Details
- Hyperparameters and training details
- Mathematical formulations

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

PAPER_CONCEPT_ANALYSIS_PROMPT_TRADITIONAL = """You are doing a COMPREHENSIVE analysis of a research paper to understand its complete structure, contributions, and implementation requirements.

# OBJECTIVE
Map out the ENTIRE paper structure and identify ALL components that need implementation for successful reproduction.

# DOCUMENT READING STRATEGY

## TRADITIONAL APPROACH: Complete Document Analysis
Read the entire document systematically to ensure comprehensive understanding:

1. **Locate and read the markdown (.md) file** in the paper directory
2. **Analyze the complete document structure** from introduction to conclusion
3. **Extract all conceptual frameworks** and implementation requirements

# COMPREHENSIVE ANALYSIS PROTOCOL

## 1. COMPLETE PAPER STRUCTURAL ANALYSIS
Create a full map of the document:

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

CODE_PLANNING_PROMPT_TRADITIONAL = """You are creating a DETAILED, COMPLETE reproduction plan by integrating comprehensive analysis results.

# INPUT
You receive two exhaustive analyses:
1. **Comprehensive Paper Analysis**: Complete paper structure, components, and requirements
2. **Complete Algorithm Extraction**: All algorithms, formulas, pseudocode, and technical details

Plus you can access the complete paper document by reading the markdown file directly.

# TRADITIONAL DOCUMENT ACCESS

## Direct Paper Reading
For any additional details needed beyond the provided analyses:

1. **Read the complete markdown (.md) file** in the paper directory
2. **Access any section directly** without token limitations for smaller documents
3. **Cross-reference information** across the entire document as needed

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

# Export all available items
__all__ = [
    # Basic prompts for backward compatibility
    'PAPER_INPUT_ANALYZER_PROMPT',
    'PAPER_DOWNLOADER_PROMPT',
    'PAPER_REFERENCE_ANALYZER_PROMPT',
    'GITHUB_DOWNLOAD_PROMPT',
    'PAPER_ALGORITHM_ANALYSIS_PROMPT',
    'PAPER_CONCEPT_ANALYSIS_PROMPT',
    'CODE_PLANNING_PROMPT',
    'PURE_CODE_IMPLEMENTATION_SYSTEM_PROMPT',
    'PURE_CODE_IMPLEMENTATION_SYSTEM_PROMPT_INDEX',
    'GENERAL_CODE_IMPLEMENTATION_SYSTEM_PROMPT',
    'CHAT_AGENT_PLANNING_PROMPT',
    'STRUCTURE_GENERATOR_PROMPT',
    'CODE_IMPLEMENTATION_PROMPT',
    'CONVERSATION_SUMMARY_PROMPT',
    'SLIDING_WINDOW_SYSTEM_PROMPT',

    # Traditional prompts
    'PAPER_ALGORITHM_ANALYSIS_PROMPT_TRADITIONAL',
    'PAPER_CONCEPT_ANALYSIS_PROMPT_TRADITIONAL',
    'CODE_PLANNING_PROMPT_TRADITIONAL',

    # Enhanced prompt functions
    'get_enhanced_paper_input_analyzer_prompt',
    'get_enhanced_paper_downloader_prompt',
    'get_enhanced_paper_reference_analyzer_prompt',
    'get_enhanced_github_download_prompt',
    'get_enhanced_paper_algorithm_analysis_prompt',
    'get_enhanced_paper_concept_analysis_prompt',
    'get_enhanced_code_planning_prompt',
    'get_enhanced_pure_code_implementation_prompt',
    'get_enhanced_general_code_implementation_prompt',
    'get_enhanced_chat_agent_planning_prompt',
    'get_enhanced_structure_generator_prompt',
    'get_enhanced_code_implementation_prompt',
    'get_enhanced_conversation_summary_prompt',
    'get_enhanced_sliding_window_prompt',

    # Tool functions
    'get_paper_input_analyzer_tools',
    'get_paper_downloader_tools',
    'get_paper_reference_analyzer_tools',
    'get_github_download_tools',
    'get_paper_algorithm_analysis_tools',
    'get_paper_concept_analysis_tools',
    'get_code_planning_tools',
    'get_pure_code_implementation_tools',
    'get_general_code_implementation_tools',
    'get_chat_agent_planning_tools',
    'get_structure_generator_tools',
    'get_code_implementation_tools',
    'get_conversation_summary_tools',
    'get_sliding_window_tools',

    # Utility functions
    'get_prompt_with_tools',
    'get_available_enhanced_prompts',
]
