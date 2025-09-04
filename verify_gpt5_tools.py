#!/usr/bin/env python3
"""
Verify GPT-5 Tool Schema Compatibility
Checks all tool definitions for required GPT-5 responses API properties
"""

import json

from config.gpt5_mcp_tool_definitions import GPT5MCPToolDefinitions
from tools.gpt5_tool_converter import GPT5ToolConverter


def verify_tool_schema(tool):
    """Verify tool schema meets GPT-5 requirements"""
    issues = []

    # Check for type: function
    if not tool.get("type") == "function":
        issues.append(f"Missing or incorrect 'type' field (should be 'function')")

    # Check for name
    if not tool.get("name"):
        issues.append("Missing 'name' field")

    # Check for description
    if not tool.get("description"):
        issues.append("Missing 'description' field")

    # Check parameters
    params = tool.get("parameters", {})
    if not params:
        issues.append("Missing 'parameters' field")
    else:
        # Check type
        if not params.get("type") == "object":
            issues.append("Parameters 'type' must be 'object'")

        # Check properties
        if not params.get("properties"):
            issues.append("Missing 'properties' in parameters")

        # Check required vs properties consistency
        required = params.get("required", [])
        properties = params.get("properties", {})
        for req in required:
            if req not in properties:
                issues.append(f"Required parameter '{req}' not defined in properties")

        # Check additionalProperties
        if "additionalProperties" not in params:
            issues.append("Missing 'additionalProperties' in parameters (required by GPT-5)")

    return issues


def main():
    print("🔍 Verifying GPT-5 Tool Compatibility")
    print("="*50)

    # Get all tools
    all_tools = GPT5MCPToolDefinitions.get_all_tools()

    print(f"Found {len(all_tools)} tools to verify\n")

    # Verify each tool
    all_valid = True
    for i, tool in enumerate(all_tools, 1):
        tool_name = tool.get("name", f"UnknownTool-{i}")

        issues = verify_tool_schema(tool)

        if issues:
            all_valid = False
            print(f"❌ {tool_name}: INVALID")
            for issue in issues:
                print(f"   - {issue}")
            print(f"   Tool definition:")
            print(f"   {json.dumps(tool, indent=2)[:200]}...\n")
        else:
            print(f"✅ {tool_name}: Valid")

    print("\nSummary:")
    if all_valid:
        print("🎉 All tools are valid for GPT-5 Responses API!")
    else:
        print("⚠️ Some tools have issues that need to be fixed!")

    # Test creating a payload
    print("\n📋 Example of a valid GPT-5 Responses API payload:")
    sample_tool = all_tools[0] if all_tools else {
        "type": "function",
        "name": "sample",
        "description": "Sample",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False}
    }

    payload = GPT5ToolConverter.create_responses_api_payload(
        model="gpt-5",
        input_text="Test input",
        tools=[sample_tool]
    )

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
