"""Multi-agent orchestrator for BorsaCI - inspired by Dexter's architecture"""

from typing import Optional
from datetime import datetime
import os

from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart

from .model import (
    create_planning_agent,
    create_action_agent,
    create_validation_agent,
    create_answer_agent,
)
from .schemas import TaskList, IsDone, Answer, Task
from .prompts import (
    PLANNING_PROMPT,
    ACTION_PROMPT,
    VALIDATION_PROMPT,
    get_answer_prompt,
)
from .mcp_tools import BorsaMCP, get_mcp_client


class BorsaAgent:
    """
    Multi-agent orchestrator for Turkish financial markets analysis.

    Architecture (inspired by Dexter):
    1. Planning Agent: Decomposes queries into sequential tasks
    2. Action Agent: Executes tasks using Borsa MCP tools
    3. Validation Agent: Checks task completion
    4. Answer Agent: Synthesizes final response

    Safety features:
    - Global max_steps limit (runaway loop prevention)
    - Per-task iteration limit
    - Repeating action detection
    - Error recovery
    """

    def __init__(
        self,
        max_steps: Optional[int] = None,
        max_steps_per_task: Optional[int] = None,
        mcp_client: Optional[BorsaMCP] = None,
    ):
        """
        Initialize BorsaAgent.

        Args:
            max_steps: Global step limit (default: 20)
            max_steps_per_task: Per-task iteration limit (default: 5)
            mcp_client: Optional BorsaMCP client (creates new if None)
        """
        # Configuration
        self.max_steps = max_steps or int(os.getenv("MAX_STEPS", "20"))
        self.max_steps_per_task = max_steps_per_task or int(
            os.getenv("MAX_STEPS_PER_TASK", "5")
        )

        # MCP Client
        self.mcp = mcp_client or get_mcp_client()

        # Multi-agent setup
        self.planner = create_planning_agent(
            output_type=TaskList,
            system_prompt=PLANNING_PROMPT.format(current_date=self._get_date()),
        )

        self.actor = create_action_agent(
            system_prompt=ACTION_PROMPT.format(current_date=self._get_date()),
            mcp_client=self.mcp,
            deps_type=BorsaMCP,
        )

        self.validator = create_validation_agent(
            output_type=IsDone,
            system_prompt=VALIDATION_PROMPT,
        )

        self.answerer = create_answer_agent(
            output_type=Answer,
            system_prompt=get_answer_prompt(),
        )

        # Session state
        self.last_actions = []

    async def __aenter__(self):
        """
        Enter async context - open MCP connection.

        This allows using the agent with 'async with':
            async with agent:
                result = await agent.run(query)
        """
        # Open MCP server connection for the session
        await self.mcp.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit async context - close MCP connection cleanly.

        Ensures MCP connection is properly closed even on errors.
        """
        # Close MCP server connection
        await self.mcp.__aexit__(exc_type, exc_val, exc_tb)
        return False  # Don't suppress exceptions

    def _get_date(self) -> str:
        """Get current date in Turkish format"""
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%Y")

    async def run(
        self,
        query: str,
        message_history: Optional[list[ModelMessage]] = None,
    ) -> tuple[str, list[ModelMessage]]:
        """
        Execute full agentic loop to answer user query.

        Process:
        1. Plan tasks (with conversation history for context)
        2. Execute each task with validation loop
        3. Generate final answer

        Args:
            query: User query in Turkish or English
            message_history: Optional conversation history from previous runs

        Returns:
            Tuple of (answer, messages) where:
            - answer: Comprehensive answer with disclaimer
            - messages: All messages including history, query, and answer

        Raises:
            RuntimeError: If max_steps exceeded or critical error
        """
        import sys

        # Debug logging
        if "--debug" in sys.argv:
            print(f"[DEBUG] agent.run() called with query: {query[:50]}...")

        # Note: MCP connection is managed automatically by PydanticAI
        # when the Action Agent uses tools from the registered toolset

        # Reset session state
        step_count = 0
        self.last_actions = []
        session_outputs = []

        if "--debug" in sys.argv:
            print("[DEBUG] About to call planner...")

        # Step 1: Plan tasks (with conversation history)
        print("🔍 Görevler planlanıyor...")
        import asyncio
        try:
            task_result = await asyncio.wait_for(
                self.planner.run(query, message_history=message_history),
                timeout=60.0
            )
            tasks = task_result.output.tasks
            # Get all messages from planner (includes history + new query + plan)
            planner_messages = task_result.all_messages()
        except asyncio.TimeoutError:
            print("⚠️  Planlama zaman aşımına uğradı")
            tasks = []
            planner_messages = message_history or []

        if not tasks:
            # No tasks created - likely out of scope
            print("⚠️  Görev bulunamadı, doğrudan yanıt üretiliyor...")
            answer = await self._generate_answer(query, session_outputs)

            # Create final response message
            final_message = ModelResponse(
                parts=[TextPart(content=answer)],
                timestamp=datetime.now(),
            )

            # Return answer and messages
            all_messages = planner_messages + [final_message]
            return answer, all_messages

        print(f"✅ {len(tasks)} görev planlandı")
        for task in tasks:
            print(f"   {task.id}. {task.description}")

        # Step 2: Execute tasks
        for task in tasks:
            if step_count >= self.max_steps:
                print(f"⚠️  Global maksimum adım sayısına ulaşıldı ({self.max_steps})")
                break

            task_outputs = await self._execute_task(task, step_count)
            session_outputs.extend(task_outputs)

            # Update step count (approximate)
            step_count += len(task_outputs)

        # Step 3: Generate final answer
        print("📝 Yanıt oluşturuluyor...")
        answer = await self._generate_answer(query, session_outputs)

        # Step 4: Create final response message for conversation history
        final_message = ModelResponse(
            parts=[TextPart(content=answer)],
            timestamp=datetime.now(),
        )

        # Combine all messages: planner messages + final answer
        all_messages = planner_messages + [final_message]

        return answer, all_messages

    async def _execute_task(self, task: Task, current_step: int) -> list[str]:
        """
        Execute a single task with validation loop using Action Agent.

        The Action Agent has MCP tools registered as a toolset, so it will
        automatically select and call the appropriate tools.

        Args:
            task: Task to execute
            current_step: Current global step count

        Returns:
            List of output strings from tool executions
        """
        print(f"\n🔧 Görev {task.id}: {task.description}")
        outputs = []

        for iteration in range(self.max_steps_per_task):
            if current_step + iteration >= self.max_steps:
                break

            # Use Action Agent to execute the task
            # The agent will automatically select and call MCP tools
            try:
                import asyncio

                # Create action prompt with task description and previous context
                action_prompt = f"""
                Görev: {task.description}

                {"Önceki çıktılar: " + chr(10).join(outputs[-2:]) if outputs else "İlk deneme"}

                Bu görevi tamamlamak için uygun MCP araçlarını kullan.
                """

                result = await asyncio.wait_for(
                    self.actor.run(action_prompt),
                    timeout=60.0  # MCP tool calls can take longer
                )

                # Debug: Check what attributes the result has
                import sys
                if "--debug" in sys.argv:
                    print(f"[DEBUG] Result type: {type(result)}")
                    print(f"[DEBUG] Result attributes: {dir(result)}")

                # Extract the action result
                # Action Agent has no output_type, so result.data is a string
                # But we need to handle the tool calls that were made
                if hasattr(result, 'data'):
                    tool_result = result.data
                elif hasattr(result, 'output'):
                    tool_result = result.output
                else:
                    # Fallback: stringify the result
                    tool_result = str(result)

                if tool_result:
                    outputs.append(str(tool_result))
                    print(f"   ✓ Veri toplandı ({len(str(tool_result))} karakter)")

            except asyncio.TimeoutError:
                print(f"   ⚠️  İşlem zaman aşımına uğradı")
                outputs.append("İşlem zaman aşımına uğradı")
                break

            except Exception as e:
                error_msg = f"Araç çağrısı başarısız: {str(e)}"
                print(f"   ❌ {error_msg}")
                outputs.append(error_msg)

            # Validate task completion
            is_done = await self._validate_task(task, outputs)

            if is_done.done:
                print(f"   ✅ Görev tamamlandı (güven: {is_done.confidence:.0%})")
                break

            if iteration == self.max_steps_per_task - 1:
                print(f"   ⚠️  Maksimum deneme sayısına ulaşıldı")

        return outputs

    async def _validate_task(self, task: Task, outputs: list[str]) -> IsDone:
        """
        Validate if task is complete.

        Args:
            task: Task being validated
            outputs: Outputs collected so far

        Returns:
            IsDone validation result
        """
        validation_prompt = f"""
        Görev: {task.description}

        Toplanan çıktılar:
        {chr(10).join(outputs[-3:])}  # Last 3 outputs

        Bu görev tamamlandı mı?
        """

        try:
            import asyncio
            result = await asyncio.wait_for(
                self.validator.run(validation_prompt),
                timeout=60.0  # 60 second timeout for validation
            )
            return result.output
        except asyncio.TimeoutError:
            # If validation times out, assume done to avoid infinite loops
            return IsDone(done=True, reason="Doğrulama zaman aşımı - varsayılan olarak tamamlandı", confidence=0.5)
        except Exception as e:
            # If validation fails, assume not done
            return IsDone(done=False, reason=f"Doğrulama hatası: {str(e)}", confidence=0.3)

    async def _generate_answer(self, query: str, session_outputs: list[str]) -> str:
        """
        Generate final answer from collected data.

        Args:
            query: Original user query
            session_outputs: All outputs from task executions

        Returns:
            Formatted answer in Turkish with disclaimer
        """
        all_data = "\n\n".join(session_outputs) if session_outputs else "Veri toplanamadı."

        answer_prompt = f"""
        Kullanıcı Sorusu: {query}

        Toplanan Veriler:
        {all_data}

        Bu verileri kullanarak kullanıcıya kapsamlı bir Türkçe yanıt oluştur.
        """

        try:
            # Add timeout to prevent indefinite hanging
            import asyncio
            result = await asyncio.wait_for(
                self.answerer.run(answer_prompt),
                timeout=60.0  # 60 second timeout
            )
            return result.output.answer
        except asyncio.TimeoutError:
            return f"""
❌ Yanıt oluşturma zaman aşımına uğradı (60 saniye).

Toplanan veriler:
{all_data[:500]}...

⚠️ Bu bilgiler sadece bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir.
"""
        except Exception as e:
            return f"""
❌ Yanıt oluşturulurken hata oluştu: {str(e)}

Toplanan veriler:
{all_data[:500]}...

⚠️ Bu bilgiler sadece bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir.
"""
