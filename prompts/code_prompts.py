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
