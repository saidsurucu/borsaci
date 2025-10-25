"""PydanticAI MCP client for Borsa MCP server integration"""

from pydantic_ai.mcp import MCPServerStreamableHTTP
from typing import Optional
import os


class BorsaMCP(MCPServerStreamableHTTP):
    """
    PydanticAI MCP client for Borsa MCP server.

    Provides async interface to 43+ financial market tools including:
    - BIST stocks and indices
    - TEFAS investment funds
    - BtcTurk & Coinbase cryptocurrency
    - Forex and commodities
    - Economic calendar and inflation data

    This class extends MCPServerStreamableHTTP and can be registered
    as a toolset with PydanticAI agents.
    """

    def __init__(self, server_url: Optional[str] = None, timeout: float = 30.0):
        """
        Initialize Borsa MCP client.

        Args:
            server_url: MCP server URL.
                       Defaults to BORSA_MCP_URL env var or hosted server at borsamcp.fastmcp.app
            timeout: Connection timeout in seconds (default: 30.0)
        """
        if server_url is None:
            # Check environment variable first
            server_url = os.getenv("BORSA_MCP_URL")

        if server_url is None:
            # Use hosted FastMCP server as default
            server_url = "https://borsamcp.fastmcp.app/mcp"

        # Initialize parent MCPServerStreamableHTTP with timeout
        super().__init__(server_url, timeout=timeout)

        self.server_url = server_url
        self.tools_cache = []
        self._initialized = False

    async def initialize(self) -> list[dict]:
        """
        Initialize connection and discover available tools.

        Note: When used as a toolset with PydanticAI agents, connection
        is managed automatically. This method is kept for CLI compatibility.

        Returns:
            List of tool metadata dicts
        """
        if self._initialized:
            return self.tools_cache

        try:
            # Use context manager to connect
            async with self:
                # List tools from MCP server
                tools = await self.list_tools()
                self.tools_cache = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": getattr(tool, 'inputSchema', {})
                    }
                    for tool in tools
                ]
                self._initialized = True

        except Exception as e:
            # Add more detailed error info
            error_msg = f"MCP initialization failed: {type(e).__name__}: {str(e)}"
            raise RuntimeError(error_msg) from e

        return self.tools_cache

    async def get_tool_schema(self, tool_name: str) -> Optional[dict]:
        """
        Get input schema for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool input schema or None if not found
        """
        if not self._initialized:
            await self.initialize()

        for tool in self.tools_cache:
            if tool["name"] == tool_name:
                return tool.get("input_schema")

        return None

    async def search_tools(self, keyword: str) -> list[dict]:
        """
        Search tools by keyword in name or description.

        Args:
            keyword: Search keyword (case-insensitive)

        Returns:
            List of matching tools
        """
        if not self._initialized:
            await self.initialize()

        keyword_lower = keyword.lower()
        return [
            tool for tool in self.tools_cache
            if keyword_lower in tool["name"].lower()
            or keyword_lower in tool["description"].lower()
        ]

    def get_tools_summary(self) -> str:
        """
        Get formatted summary of all available tools.

        Returns:
            Human-readable tool list
        """
        if not self.tools_cache:
            return "MCP not initialized. Call initialize() first."

        lines = [f"📊 Borsa MCP Tools ({len(self.tools_cache)} total):\n"]

        # Group by category (inferred from name prefix)
        categories = {}
        for tool in self.tools_cache:
            # Simple categorization based on name patterns
            name = tool["name"]
            if "bist" in name or "company" in name or "stock" in name:
                cat = "BIST Stocks"
            elif "fund" in name or "tefas" in name:
                cat = "Investment Funds"
            elif "btcturk" in name or "coinbase" in name or "crypto" in name:
                cat = "Cryptocurrency"
            elif "forex" in name or "commodity" in name or "fuel" in name:
                cat = "Forex & Commodities"
            elif "inflation" in name or "economic" in name or "calendar" in name:
                cat = "Economic Data"
            elif "kap" in name or "news" in name:
                cat = "News & Disclosures"
            else:
                cat = "Other"

            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tool)

        # Format output
        for cat, tools in sorted(categories.items()):
            lines.append(f"\n{cat}:")
            for tool in tools:
                lines.append(f"  - {tool['name']}: {tool['description'][:80]}...")

        return "\n".join(lines)


# Singleton instance for easy import
_mcp_instance: Optional[BorsaMCP] = None


def get_mcp_client() -> BorsaMCP:
    """Get or create singleton BorsaMCP client instance"""
    global _mcp_instance
    if _mcp_instance is None:
        _mcp_instance = BorsaMCP()
    return _mcp_instance
