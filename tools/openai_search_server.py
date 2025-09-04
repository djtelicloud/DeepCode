import json
import os
import sys
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools.gpt_client import GPTClient

load_dotenv()


# Initialize FastMCP server
server = FastMCP(
    "openai-search-mcp",
    instructions="""
# OpenAI Search MCP Server

This server provides tools for searching the web and generating structured responses using OpenAI GPT-5.
It allows you to get enhanced search details from billions of web documents, and to extract structured information using JSON schema.

## Available Tools

### 1. openai_web_search
Search the web using OpenAI GPT-5's native web search tool (web_search_preview) and get enhanced search details from billions of web documents, including page titles, URLs, summaries, site names, publication dates, and more.

### 2. openai_ai_search
Use OpenAI GPT-5 to generate structured responses using a provided JSON schema, or fallback to web search if no schema is provided.

## Output Format

All search results will be formatted as text with clear sections for each
result item, including:

- Web search: Title, URL, Description, Published date, and Site name
- AI search: Structured JSON response if schema is provided, otherwise same as web search
""",
)



@server.tool()
async def openai_web_search(
    query: str, freshness: str = "noLimit", count: int = 10
) -> str:
    """Search the web using OpenAI GPT-5's native web_search_preview tool and return formatted results.
    Args:
        query: Search query (required)
        freshness: Not used (kept for compatibility)
        count: Not used (kept for compatibility)
    Returns:
        str: Formatted web search results from OpenAI GPT-5
    """
    client = GPTClient()
    try:
        result = await client.web_search(query)
        return result
    except Exception as e:
        return f"Error using OpenAI GPT-5 web search: {str(e)}"



@server.tool()
async def openai_ai_search(
    query: str, freshness: str = "noLimit", count: int = 10, schema: Optional[dict] = None
) -> str:
    """Use OpenAI GPT-5 to generate a structured response if a JSON schema is provided, otherwise perform a web search.
    Args:
        query: Search query or input text (required)
        freshness: Not used (kept for compatibility)
        count: Not used (kept for compatibility)
        schema: Optional JSON schema for structured response
    Returns:
        str: Structured JSON response or formatted web search results from OpenAI GPT-5
    """
    client = GPTClient()
    try:
        if schema:
            result = await client.structured_response(query, schema)
        else:
            result = await client.web_search(query)
        return result
    except Exception as e:
        return f"Error using OpenAI GPT-5 AI search: {str(e)}"


def main():
    """Initialize and run the MCP server."""
    print("Starting openai Search MCP server...", file=sys.stderr)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
