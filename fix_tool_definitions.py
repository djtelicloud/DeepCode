#!/usr/bin/env python3
"""
Quick script to fix tool definition formatting issues
"""

import re


def fix_tool_definitions():
    file_path = "config/mcp_tool_definitions_index.py"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix malformed additionalProperties placement
    # Remove malformed patterns like '"additionalProperties": False,\n\n                    },'
    content = re.sub(r'"additionalProperties": False,\s*\n\s*},', '},', content)

    # Fix patterns where additionalProperties is misplaced in properties
    content = re.sub(r'",\s*"additionalProperties": False,\s*\n\s*}', '"\n                    }', content)

    # Add additionalProperties at the right level (in parameters)
    # Find patterns like '"required": ["param"],' without additionalProperties
    def add_additional_properties(match):
        required_line = match.group(0)
        # Check if additionalProperties already exists nearby
        if '"additionalProperties"' in content[match.start()-200:match.end()+200]:
            return required_line
        return required_line + '\n                "additionalProperties": False'

    content = re.sub(r'"required": \[[^\]]+\],', add_additional_properties, content)

    # Convert remaining input_schema to parameters format
    content = re.sub(r'"input_schema":', '"parameters":', content)

    # Add type: function for tools missing it
    def add_type_function(match):
        tool_def = match.group(0)
        if '"type": "function"' not in tool_def:
            # Insert after the opening brace
            tool_def = tool_def.replace('return {\n', 'return {\n            "type": "function",\n')
        return tool_def

    content = re.sub(r'return \{[^}]*"name": "[^"]*"[^}]*"description": "[^"]*"[^}]*\}', add_type_function, content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Fixed tool definition formatting issues")

if __name__ == "__main__":
    fix_tool_definitions()
