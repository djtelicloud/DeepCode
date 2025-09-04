"""
Individual Prompts Module
Refactored prompts with GPT-5 Responses API and MCP tool support.
"""

from .chat_agent_planning_prompt import (
    CHAT_AGENT_PLANNING_PROMPT, get_chat_agent_planning_tools,
    get_enhanced_chat_agent_planning_prompt)
from .code_implementation_prompt import (
    CODE_IMPLEMENTATION_PROMPT, get_code_implementation_tools,
    get_enhanced_code_implementation_prompt)
from .code_planning_prompt import (CODE_PLANNING_PROMPT,
                                   get_code_planning_tools,
                                   get_enhanced_code_planning_prompt)
from .conversation_summary_prompt import (
    CONVERSATION_SUMMARY_PROMPT, get_conversation_summary_tools,
    get_enhanced_conversation_summary_prompt)
from .general_code_implementation_prompt import (
    GENERAL_CODE_IMPLEMENTATION_SYSTEM_PROMPT,
    get_enhanced_general_code_implementation_prompt,
    get_general_code_implementation_tools)
from .github_download_prompt import (GITHUB_DOWNLOAD_PROMPT,
                                     get_enhanced_github_download_prompt,
                                     get_github_download_tools)
from .paper_algorithm_analysis_prompt import (
    PAPER_ALGORITHM_ANALYSIS_PROMPT,
    get_enhanced_paper_algorithm_analysis_prompt,
    get_paper_algorithm_analysis_tools)
from .paper_concept_analysis_prompt import (
    PAPER_CONCEPT_ANALYSIS_PROMPT, get_enhanced_paper_concept_analysis_prompt,
    get_paper_concept_analysis_tools)
from .paper_downloader_prompt import (PAPER_DOWNLOADER_PROMPT,
                                      get_enhanced_paper_downloader_prompt,
                                      get_paper_downloader_tools)
# Import all individual prompts
from .paper_input_analyzer_prompt import (
    PAPER_INPUT_ANALYZER_PROMPT, get_enhanced_paper_input_analyzer_prompt,
    get_paper_input_analyzer_tools)
from .paper_reference_analyzer_prompt import (
    PAPER_REFERENCE_ANALYZER_PROMPT,
    get_enhanced_paper_reference_analyzer_prompt,
    get_paper_reference_analyzer_tools)
from .pure_code_implementation_prompt import (
    PURE_CODE_IMPLEMENTATION_SYSTEM_PROMPT,
    get_enhanced_pure_code_implementation_prompt,
    get_pure_code_implementation_tools)
from .sliding_window_system_prompt import (SLIDING_WINDOW_SYSTEM_PROMPT,
                                           get_enhanced_sliding_window_prompt,
                                           get_sliding_window_tools)
from .structure_generator_prompt import (
    STRUCTURE_GENERATOR_PROMPT, get_enhanced_structure_generator_prompt,
    get_structure_generator_tools)

__all__ = [
    # Basic prompts
    'PAPER_INPUT_ANALYZER_PROMPT',
    'PAPER_DOWNLOADER_PROMPT',
    'PAPER_REFERENCE_ANALYZER_PROMPT',
    'GITHUB_DOWNLOAD_PROMPT',
    'PAPER_ALGORITHM_ANALYSIS_PROMPT',
    'PAPER_CONCEPT_ANALYSIS_PROMPT',
    'CODE_PLANNING_PROMPT',
    'PURE_CODE_IMPLEMENTATION_SYSTEM_PROMPT',
    'GENERAL_CODE_IMPLEMENTATION_SYSTEM_PROMPT',
    'CHAT_AGENT_PLANNING_PROMPT',
    'STRUCTURE_GENERATOR_PROMPT',
    'CODE_IMPLEMENTATION_PROMPT',
    'CONVERSATION_SUMMARY_PROMPT',
    'SLIDING_WINDOW_SYSTEM_PROMPT',

    # Enhanced prompts with tools
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
]
