import json
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.mcp_tool_definitions import MCPToolDefinitions


def debug_tool_format():
    """Debug the tool format to see what's being generated"""
    print("🔍 Debugging MCP Tool Format")
    print("=" * 50)

    tool_defs = MCPToolDefinitions()
    tools = tool_defs.get_code_implementation_tools()

    print(f"Number of tools: {len(tools)}")

    for i, tool in enumerate(tools):
        print(f"\n--- Tool {i+1}: {tool.get('name', 'UNNAMED')} ---")
        print(f"Tool structure: {json.dumps(tool, indent=2)}")

        # Check required fields
        required_fields = ['type', 'name', 'description', 'parameters']
        missing_fields = []

        for field in required_fields:
            if field not in tool:
                missing_fields.append(field)

        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        else:
            print(f"✅ All required fields present")

        # Check for old format
        if 'input_schema' in tool:
            print(f"⚠️  WARNING: Old 'input_schema' format detected!")

    # Test the first tool specifically for the API call
    if tools:
        first_tool = tools[0]
        print(f"\n🧪 First tool for API test:")
        print(f"Type: {first_tool.get('type', 'MISSING')}")
        print(f"Name: {first_tool.get('name', 'MISSING')}")
        print(f"Has parameters: {'parameters' in first_tool}")

        if 'parameters' in first_tool:
            params = first_tool['parameters']
            print(f"Parameters type: {params.get('type', 'MISSING')}")
            print(f"AdditionalProperties: {params.get('additionalProperties', 'MISSING')}")

if __name__ == "__main__":
    debug_tool_format()
