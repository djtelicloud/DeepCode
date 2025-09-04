#!/usr/bin/env python3
"""
GPT-5 Responses API Tool Converter
Converts existing MCP tool definitions to GPT-5 Responses API format
"""

import json
from typing import Any, Dict, List, Optional


class GPT5ToolConverter:
    """Convert MCP tools to GPT-5 Responses API format"""

    @staticmethod
    def convert_mcp_tool_to_gpt5(mcp_tool: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a single MCP tool definition to GPT-5 Responses API format

        Args:
            mcp_tool: MCP tool definition

        Returns:
            GPT-5 compatible tool definition
        """
        # Extract basic information
        tool_name = mcp_tool.get("name", "unknown_tool")
        description = mcp_tool.get("description", "")

        # Handle parameters
        parameters = mcp_tool.get("parameters", {})

        # Ensure additionalProperties is set (GPT-5 requirement)
        if "additionalProperties" not in parameters:
            parameters["additionalProperties"] = False

        # Convert to GPT-5 format
        gpt5_tool = {
            "type": "function",
            "name": tool_name,
            "description": description,
            "parameters": parameters
        }

        return gpt5_tool

    @staticmethod
    def convert_mcp_tools_list(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert a list of MCP tools to GPT-5 format

        Args:
            mcp_tools: List of MCP tool definitions

        Returns:
            List of GPT-5 compatible tool definitions
        """
        return [
            GPT5ToolConverter.convert_mcp_tool_to_gpt5(tool)
            for tool in mcp_tools
        ]

    @staticmethod
    def create_structured_output_schema(
        name: str,
        properties: Dict[str, Any],
        required: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a structured output schema for GPT-5 Responses API

        Args:
            name: Schema name
            properties: Schema properties
            required: Required fields (optional)
            description: Schema description (optional)

        Returns:
            GPT-5 structured output schema
        """
        schema = {
            "name": name,
            "strict": True,
            "schema": {
                "type": "object",
                "properties": properties,
                "additionalProperties": False
            }
        }

        if required:
            schema["schema"]["required"] = required

        if description:
            schema["description"] = description

        return schema

    @staticmethod
    def create_responses_api_payload(
        model: str,
        input_text: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        structured_output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a complete payload for GPT-5 Responses API

        Args:
            model: Model name (e.g., "gpt-5")
            input_text: Input text/prompt
            tools: List of tools (optional)
            structured_output: Structured output schema (optional)

        Returns:
            Complete API payload
        """
        payload: Dict[str, Any] = {
            "model": model,
            "input": input_text
        }

        if tools:
            payload["tools"] = tools

        if structured_output:
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    **structured_output
                }
            }

        return payload

# Example usage and test functions
def test_tool_conversion():
    """Test the tool conversion functionality"""

    # Example MCP tool (from your codebase)
    mcp_tool = {
        "type": "function",
        "name": "read_file",
        "description": "Read file content, supports specifying line number range",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "File path, relative to workspace"
                },
                "start_line": {
                    "type": "integer",
                    "description": "Start line number (1-based, optional)"
                },
                "end_line": {
                    "type": "integer",
                    "description": "End line number (1-based, optional)"
                }
            },
            "required": ["file_path"]
        }
    }

    # Convert to GPT-5 format
    gpt5_tool = GPT5ToolConverter.convert_mcp_tool_to_gpt5(mcp_tool)
    print("🔄 Converted MCP Tool to GPT-5 Format:")
    print(json.dumps(gpt5_tool, indent=2))

    # Create structured output schema
    person_schema = GPT5ToolConverter.create_structured_output_schema(
        name="person",
        properties={
            "name": {
                "type": "string",
                "minLength": 1
            },
            "age": {
                "type": "number",
                "minimum": 0,
                "maximum": 130
            }
        },
        required=["name", "age"]
    )

    print("\n📋 Example Structured Output Schema:")
    print(json.dumps(person_schema, indent=2))

    # Create complete API payload
    payload = GPT5ToolConverter.create_responses_api_payload(
        model="gpt-5",
        input_text="Please analyze this code file",
        tools=[gpt5_tool],
        structured_output=person_schema
    )

    print("\n🚀 Complete API Payload:")
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    print("🛠️  GPT-5 Responses API Tool Converter")
    print("="*50)
    test_tool_conversion()
