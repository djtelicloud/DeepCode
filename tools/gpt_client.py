# gpt_client.py
# Minimal async OpenAI GPT-5 client for web search and structured response
import os
from typing import Any, Dict, List, Optional

import yaml
from openai import AsyncOpenAI


class GPTClient:
    def __init__(self, api_key=None, base_url=None):
        # Load configuration if not provided
        if api_key is None:
            config = self._load_config()
        else:
            config = {}

        self.api_key = api_key or config.get("openai", {}).get("api_key") or os.environ.get("OPENAI_API_KEY")

        # Use GPT-5 responses API endpoint by default
        self.base_url = base_url or "https://api.openai.com/v1"

        # Initialize client with responses API
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    def _load_config(self):
        """Load configuration from secrets file"""
        try:
            with open("mcp_agent.secrets.yaml", "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            # Try config file as fallback
            try:
                with open("mcp_agent.config.yaml", "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except FileNotFoundError:
                return {}

    async def web_search(self, query, model="gpt-5", tools=None):
        # Use OpenAI's responses API for web search
        kwargs = {
            "model": model,
            "input": [{"role": "user", "content": f"Please search the web for: {query}"}]
        }
        if tools is not None:
            kwargs["tools"] = tools
        response = await self.client.responses.create(**kwargs)

        # Parse the OpenAI Responses API format
        return self._parse_response(response)

    async def call_with_mcp_tools(self, input_text, mcp_tools=None, model="gpt-5"):
        """
        Call GPT-5 with MCP tools using the responses API

        Args:
            input_text: The input prompt/query
            mcp_tools: List of MCP tool definitions (will be converted to GPT-5 format)
            model: Model to use (default: gpt-5)

        Returns:
            str: The output text from the response
        """
        # Import converter
        from tools.gpt5_tool_converter import GPT5ToolConverter

        # Format input as array of messages for Responses API
        kwargs = {
            "model": model,
            "input": [{"role": "user", "content": input_text}]
        }

        if mcp_tools is not None:
            # Convert MCP tools to GPT-5 format if needed
            if mcp_tools and isinstance(mcp_tools[0], dict):
                # Check if already in GPT-5 format (has additionalProperties)
                if "parameters" in mcp_tools[0] and "additionalProperties" not in mcp_tools[0].get("parameters", {}):
                    # Convert to GPT-5 format
                    mcp_tools = GPT5ToolConverter.convert_mcp_tools_list(mcp_tools)

            kwargs["tools"] = mcp_tools

        response = await self.client.responses.create(**kwargs)

        # Parse the OpenAI Responses API format
        return self._parse_response(response)

    def _parse_response(self, response) -> str:
        """
        Parse GPT-5 Responses API response format

        Args:
            response: Response object from GPT-5 Responses API

        Returns:
            str: Parsed text content
        """
        try:
            # First, extract tool calls if they exist
            tool_calls = self._extract_tool_calls(response)

            # If we have tool calls, return a special format that code_implementation_workflow can understand
            if tool_calls:
                import json
                return json.dumps({
                    "tool_calls": tool_calls,
                    "content": "I'll help you with this task using the available tools."
                })

            # Otherwise proceed with normal text extraction
            if hasattr(response, 'output') and response.output:
                # Find the message output (not reasoning)
                for output_item in response.output:
                    if hasattr(output_item, 'type') and output_item.type == 'message':
                        if hasattr(output_item, 'content') and output_item.content:
                            # Content is a list of ResponseOutputText items
                            for content_item in output_item.content:
                                if hasattr(content_item, 'type') and content_item.type == 'output_text':
                                    if hasattr(content_item, 'text'):
                                        return content_item.text
                            # Fallback to first content item as string
                            return str(output_item.content[0])
                        elif hasattr(output_item, 'text'):
                            return output_item.text

                # If no message found, try first output item
                output_item = response.output[0]
                if hasattr(output_item, 'content') and output_item.content:
                    for content_item in output_item.content:
                        if hasattr(content_item, 'type') and content_item.type == 'output_text':
                            if hasattr(content_item, 'text'):
                                return content_item.text
                    return str(output_item.content[0])

            # Fallback: return string representation
            return str(response)

        except Exception as e:
            print(f"Error parsing response: {e}")
            return str(response)

    def _extract_tool_calls(self, response):
        """
        Extract tool calls from GPT-5 Responses API response format

        Args:
            response: Response object from GPT-5 Responses API

        Returns:
            list: List of tool calls or empty list if none found
        """
        tool_calls = []

        try:
            if hasattr(response, 'output') and response.output:
                for output_item in response.output:
                    # Look for tool_calls in the response
                    if hasattr(output_item, 'tool_calls') and output_item.tool_calls:
                        for tool_call in output_item.tool_calls:
                            if hasattr(tool_call, 'name') and hasattr(tool_call, 'input'):
                                tool_calls.append({
                                    "name": tool_call.name,
                                    "input": tool_call.input,
                                    "id": getattr(tool_call, 'id', f"tool_{len(tool_calls)}")
                                })
        except Exception as e:
            print(f"Error extracting tool calls: {e}")

        return tool_calls

    async def structured_response(self, input_text: str, schema: Dict[str, Any], model: str = "gpt-5") -> str:
        """
        Generate structured response using JSON schema with the Responses API.

        Args:
            input_text: The input prompt/query
            schema: Schema dictionary containing 'name', 'schema', and optionally 'strict'
            model: Model to use (default: gpt-5)

        Returns:
            str: The structured response text
        """
        response = await self.client.responses.create(
            model=model,
            input=[{"role": "user", "content": input_text}],
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema.get("name", "response"),
                    "strict": schema.get("strict", True),
                    "schema": schema["schema"]
                }
            }
        )

        # Parse the OpenAI Responses API format
        return self._parse_response(response)
