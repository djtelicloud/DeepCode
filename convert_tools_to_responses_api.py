#!/usr/bin/env python3
"""
Script to convert MCP tool definitions from Chat Completions format to Responses API format.

Changes:
1. Add "type": "function" at top level
2. Rename "input_schema" to "parameters"
3. Add "additionalProperties": False for strict mode
"""

import os
import re


def convert_tool_definition(content):
    """Convert tool definition from old format to new format."""

    # Pattern to match tool definitions
    pattern = r'(\s+return\s+{\s*\n\s+"name":\s*"[^"]+",\s*\n\s+"description":\s*"[^"]+",\s*\n\s+"input_schema":\s*{[^}]+(?:{[^}]*}[^}]*)*}\s*,?\s*\n\s+})'

    def replace_tool(match):
        tool_def = match.group(1)

        # Add "type": "function" after the opening brace
        tool_def = re.sub(
            r'(\s+return\s+{\s*\n)',
            r'\1            "type": "function",\n',
            tool_def
        )

        # Replace "input_schema" with "parameters"
        tool_def = tool_def.replace('"input_schema":', '"parameters":')

        # Add additionalProperties: False before the closing brace of parameters
        # Look for the parameters section and add additionalProperties
        tool_def = re.sub(
            r'(\s+"required":\s*\[[^\]]*\],?\s*\n)(\s+)(}\s*,?\s*\n\s+})',
            r'\1\2"additionalProperties": False,\n\2\3',
            tool_def
        )

        # If there's no required field, add additionalProperties before the closing parameters brace
        if '"additionalProperties"' not in tool_def:
            tool_def = re.sub(
                r'(\s+)(}\s*,?\s*\n\s+})',
                r'\1"additionalProperties": False,\n\1\2',
                tool_def
            )

        return tool_def

    # Apply the transformation
    converted = re.sub(pattern, replace_tool, content, flags=re.DOTALL)

    return converted

def convert_file(file_path):
    """Convert a single file."""
    print(f"Converting {file_path}...")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        converted_content = convert_tool_definition(content)

        # Only write if there were changes
        if converted_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(converted_content)
            print(f"✅ Updated {file_path}")
        else:
            print(f"ℹ️ No changes needed in {file_path}")

    except Exception as e:
        print(f"❌ Error converting {file_path}: {e}")

def main():
    """Main conversion function."""
    print("🔄 Converting MCP tool definitions to Responses API format...")

    # Files to convert
    files_to_convert = [
        "config/mcp_tool_definitions.py",
        "config/mcp_tool_definitions_index.py"
    ]

    for file_path in files_to_convert:
        if os.path.exists(file_path):
            convert_file(file_path)
        else:
            print(f"⚠️ File not found: {file_path}")

    print("\n🎉 Conversion complete!")
    print("\nNote: This is a basic conversion. You may need to manually verify complex tool definitions.")

if __name__ == "__main__":
    main()
