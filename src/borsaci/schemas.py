"""Pydantic models for BorsaCI agent system"""

from pydantic import BaseModel, Field
from typing import Optional


class Task(BaseModel):
    """Individual task in task list"""
    id: int = Field(..., description="Task ID")
    description: str = Field(..., description="Task description in Turkish")
    done: bool = Field(default=False, description="Whether task is completed")
    tool_name: Optional[str] = Field(None, description="MCP tool to use for this task")
    depends_on: list[int] = Field(
        default_factory=list,
        description="List of task IDs this task depends on (empty if independent)"
    )


class TaskList(BaseModel):
    """List of tasks decomposed from user query"""
    tasks: list[Task] = Field(..., description="Sequential list of tasks to complete")
    reasoning: Optional[str] = Field(None, description="Why these tasks were chosen")


class IsDone(BaseModel):
    """Validation result for task completion"""
    done: bool = Field(..., description="Whether the task is complete")
    reason: str = Field(..., description="Explanation of why task is done or not done")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this assessment")


class ToolExecution(BaseModel):
    """Result of a tool execution"""
    tool_name: str = Field(..., description="Name of the MCP tool called")
    arguments: dict = Field(..., description="Arguments passed to the tool")
    result: str = Field(..., description="String representation of tool output")
    success: bool = Field(..., description="Whether tool execution succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")


class Answer(BaseModel):
    """Final answer to user query"""
    answer: str = Field(..., description="Comprehensive answer in Turkish")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the answer")
    data_sources: list[str] = Field(
        default_factory=list,
        description="List of MCP tools used to gather data"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Any warnings or disclaimers (e.g., investment advice warning)"
    )


class OptimizedToolArgs(BaseModel):
    """Optimized arguments for tool execution"""
    arguments: dict = Field(..., description="Refined tool arguments")
    reasoning: str = Field(..., description="Why these arguments were chosen")


class BaseResponse(BaseModel):
    """Base agent routing decision - determines if query needs multi-agent workflow"""
    is_simple: bool = Field(..., description="Can be answered without MCP tools or planning")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this routing decision")
    answer: Optional[str] = Field(None, description="Direct answer if simple (only if is_simple=True)")
    reasoning: str = Field(..., description="Explanation of why query is simple or complex")
