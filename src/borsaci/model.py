"""PydanticAI agent factory with Multi-Model OpenRouter support"""

from pydantic_ai import Agent
from typing import Any, Optional
import os


def get_planning_model() -> str:
    """
    Get OpenRouter model for Planning Agent.

    Returns:
        Gemini 2.5 Pro - Strong reasoning for task decomposition
    """
    return "openrouter:google/gemini-2.5-pro"


def get_action_model() -> str:
    """
    Get OpenRouter model for Action Agent.

    Returns:
        Gemini 2.5 Flash - Optimized for tool calling
    """
    return "openrouter:google/gemini-2.5-flash-preview-09-2025"


def get_validation_model() -> str:
    """
    Get OpenRouter model for Validation Agent.

    Returns:
        Gemini 2.5 Flash - Simple validation tasks
    """
    return "openrouter:google/gemini-2.5-flash-preview-09-2025"


def get_answer_model() -> str:
    """
    Get OpenRouter model for Answer Agent.

    Returns:
        Gemini 2.5 Flash Preview - Fast, high-quality responses
    """
    return "openrouter:google/gemini-2.5-flash-preview-09-2025"


def create_agent(
    model: str,
    system_prompt: str,
    output_type: Optional[type] = None,
    tools: Optional[list] = None,
    deps_type: Optional[type] = None,
    retries: int = 3,
) -> Agent:
    """
    Create a PydanticAI agent with specified OpenRouter model.

    Args:
        model: OpenRouter model string (e.g., from get_planning_model())
        system_prompt: System prompt for the agent
        output_type: Optional Pydantic model for structured output
        tools: Optional list of tools/functions the agent can use
        deps_type: Optional type for dependency injection context
        retries: Number of retries for tool calls and model requests (default: 3)

    Returns:
        Configured PydanticAI Agent

    Example:
        >>> from borsaci.schemas import Answer
        >>> agent = create_agent(
        ...     get_answer_model(),
        ...     "You are a financial analyst",
        ...     output_type=Answer
        ... )
        >>> result = await agent.run("Analyze ASELS stock")
    """
    return Agent(
        model=model,
        system_prompt=system_prompt,
        output_type=output_type,
        tools=tools or [],
        deps_type=deps_type,
        retries=retries,
    )


def create_planning_agent(output_type: type, system_prompt: str) -> Agent:
    """
    Create planning agent for task decomposition.

    Uses Gemini 2.5 Pro for strong reasoning capabilities.

    Args:
        output_type: Pydantic model for task list output
        system_prompt: System prompt with planning instructions

    Returns:
        Planning agent with 3 retries
    """
    return create_agent(
        model=get_planning_model(),
        system_prompt=system_prompt,
        output_type=output_type,
        retries=3,
    )


def create_action_agent(
    system_prompt: str,
    mcp_client: Any,
    deps_type: Optional[type] = None,
) -> Agent:
    """
    Create action agent with MCP tool access.

    Uses Gemini 2.5 Flash optimized for tool calling.

    Args:
        system_prompt: System prompt for tool selection
        mcp_client: BorsaMCP client instance (MCPServerStreamableHTTP)
        deps_type: Type for dependency injection

    Returns:
        Action agent with tool calling capabilities via MCP toolset (3 retries)
    """
    # Register MCP client as toolset
    # The agent will automatically discover and use MCP tools
    return Agent(
        model=get_action_model(),
        system_prompt=system_prompt,
        toolsets=[mcp_client],  # MCP server registered as toolset
        deps_type=deps_type,
        retries=3,  # MCP tools can fail temporarily, allow retries
    )


def create_validation_agent(output_type: type, system_prompt: str) -> Agent:
    """
    Create validation agent for task completion checking.

    Uses Gemini 2.5 Flash for simple validation tasks.

    Args:
        output_type: Pydantic model for validation result (IsDone)
        system_prompt: System prompt with validation criteria

    Returns:
        Validation agent with 3 retries
    """
    return create_agent(
        model=get_validation_model(),
        system_prompt=system_prompt,
        output_type=output_type,
        retries=3,
    )


def create_answer_agent(output_type: type, system_prompt: str) -> Agent:
    """
    Create answer generation agent.

    Uses Gemini 2.5 Flash Preview for fast, high-quality final responses.

    Args:
        output_type: Pydantic model for answer output (Answer)
        system_prompt: System prompt for answer generation

    Returns:
        Answer agent with 3 retries
    """
    return create_agent(
        model=get_answer_model(),
        system_prompt=system_prompt,
        output_type=output_type,
        retries=3,
    )
