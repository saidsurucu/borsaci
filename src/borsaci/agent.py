"""Multi-agent orchestrator for BorsaCI - inspired by Dexter's architecture"""

from typing import Optional
from datetime import datetime
import os
import warnings

# Suppress Gemini additionalProperties warning (known Gemini limitation)
warnings.filterwarnings("ignore", message=".*additionalProperties.*Gemini.*")

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.usage import RunUsage

from .model import (
    create_planning_agent,
    create_action_agent,
    create_validation_agent,
    create_base_agent,
    get_answer_model,
)
from .schemas import TaskList, IsDone, Answer, Task, BaseResponse
from .prompts import (
    BASE_AGENT_PROMPT,
    PLANNING_PROMPT,
    ACTION_PROMPT,
    VALIDATION_PROMPT,
    get_answer_prompt,
)
from .mcp_tools import BorsaMCP, get_mcp_client
from .utils.charts import (
    create_candlestick_chart,
    create_candlestick_from_json,
    create_comparison_bar_chart,
    create_multi_line_chart,
    create_histogram,
)


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

        # Multi-agent setup (programmatic hand-off pattern)
        # Base agent for routing decisions (simple vs complex queries)
        self.base_agent = create_base_agent(
            output_type=BaseResponse,
            system_prompt=BASE_AGENT_PROMPT.format(current_date=self._get_date()),
        )

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

        # Create answer agent (no chart tools - charts rendered separately in CLI)
        self.answerer = Agent(
            model=get_answer_model(),
            system_prompt=get_answer_prompt(),
            retries=3,
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
    ) -> tuple[str, Optional[str], list[ModelMessage]]:
        """
        Execute agentic workflow with programmatic agent hand-off.

        Process (Programmatic Hand-off Pattern):
        0. Base agent: Route query (simple vs complex)
           - Simple (confidence > 0.7): Return direct answer
           - Complex: Proceed to multi-agent workflow
        1. Planning agent: Decompose into tasks
        2. Action agent: Execute tasks with MCP tools
        3. Validation agent: Check completion
        4. Answer agent: Synthesize final response

        Uses shared RunUsage across all agents for unified tracking.

        Args:
            query: User query in Turkish or English
            message_history: Optional conversation history from previous runs

        Returns:
            Tuple of (answer, chart, messages) where:
            - answer: Comprehensive answer with disclaimer
            - chart: Optional plotext chart (ANSI string) - rendered separately in CLI
            - messages: All messages including history, query, and answer

        Raises:
            RuntimeError: If max_steps exceeded or critical error
        """
        import sys
        import asyncio

        # Debug logging
        if "--debug" in sys.argv:
            print(f"[DEBUG] agent.run() called with query: {query[:50]}...")

        # Shared usage tracking (Pydantic AI pattern)
        usage = RunUsage()

        # Reset session state
        step_count = 0
        self.last_actions = []
        session_outputs = []

        # Step 0: Base agent routing (simple vs complex)
        print("🔍 Sorgu analiz ediliyor...")
        try:
            base_result = await asyncio.wait_for(
                self.base_agent.run(
                    query,
                    message_history=message_history,
                    usage=usage,  # Shared usage tracking
                ),
                timeout=30.0
            )

            if "--debug" in sys.argv:
                print(f"[DEBUG] Base agent decision: is_simple={base_result.output.is_simple}, confidence={base_result.output.confidence}")
                print(f"[DEBUG] Reasoning: {base_result.output.reasoning}")

            # Simple query with high confidence? Return direct answer
            if base_result.output.is_simple and base_result.output.confidence > 0.7:
                print(f"✅ Basit sorgu (güven: {base_result.output.confidence:.0%}) - direkt yanıt veriliyor")

                # Return answer from base agent (no chart for simple queries)
                return base_result.output.answer, None, base_result.all_messages()

            # Complex query: Proceed to multi-agent workflow
            print(f"🔧 Karmaşık sorgu (güven: {base_result.output.confidence:.0%}) - planlama başlatılıyor...")

        except asyncio.TimeoutError:
            print("⚠️  Base agent zaman aşımına uğradı, planlama workflow'una devam ediliyor...")

        # Step 1: Plan tasks (with conversation history)
        print("🔍 Görevler planlanıyor...")
        try:
            task_result = await asyncio.wait_for(
                self.planner.run(
                    query,
                    message_history=message_history,
                    usage=usage,  # Shared usage tracking
                ),
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
            answer, chart = await self._generate_answer(query, session_outputs, usage)

            # Create final response message
            final_message = ModelResponse(
                parts=[TextPart(content=answer)],
                timestamp=datetime.now(),
            )

            # Return answer, chart, and messages
            all_messages = planner_messages + [final_message]
            return answer, chart, all_messages

        print(f"✅ {len(tasks)} görev planlandı")
        for task in tasks:
            print(f"   {task.id}. {task.description}")

        # Step 2: Execute tasks
        for task in tasks:
            if step_count >= self.max_steps:
                print(f"⚠️  Global maksimum adım sayısına ulaşıldı ({self.max_steps})")
                break

            task_outputs = await self._execute_task(task, step_count, usage)
            session_outputs.extend(task_outputs)

            # Update step count (approximate)
            step_count += len(task_outputs)

        # Step 3: Generate final answer and chart (if applicable)
        print("📝 Yanıt oluşturuluyor...")
        answer, chart = await self._generate_answer(query, session_outputs, usage)

        # Step 4: Create final response message for conversation history
        final_message = ModelResponse(
            parts=[TextPart(content=answer)],
            timestamp=datetime.now(),
        )

        # Combine all messages: planner messages + final answer
        all_messages = planner_messages + [final_message]

        return answer, chart, all_messages

    async def _execute_task(self, task: Task, current_step: int, usage: RunUsage) -> list[str]:
        """
        Execute a single task with validation loop using Action Agent.

        The Action Agent has MCP tools registered as a toolset, so it will
        automatically select and call the appropriate tools.

        Args:
            task: Task to execute
            current_step: Current global step count
            usage: Shared RunUsage for tracking across all agents

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
                    self.actor.run(action_prompt, usage=usage),  # Shared usage tracking
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
            is_done = await self._validate_task(task, outputs, usage)

            if is_done.done:
                print(f"   ✅ Görev tamamlandı (güven: {is_done.confidence:.0%})")
                break

            if iteration == self.max_steps_per_task - 1:
                print(f"   ⚠️  Maksimum deneme sayısına ulaşıldı")

        return outputs

    async def _validate_task(self, task: Task, outputs: list[str], usage: RunUsage) -> IsDone:
        """
        Validate if task is complete.

        Args:
            task: Task being validated
            outputs: Outputs collected so far
            usage: Shared RunUsage for tracking

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
                self.validator.run(validation_prompt, usage=usage),  # Shared usage tracking
                timeout=60.0  # 60 second timeout for validation
            )
            return result.output
        except asyncio.TimeoutError:
            # If validation times out, assume done to avoid infinite loops
            return IsDone(done=True, reason="Doğrulama zaman aşımı - varsayılan olarak tamamlandı", confidence=0.5)
        except Exception as e:
            # If validation fails, assume not done
            return IsDone(done=False, reason=f"Doğrulama hatası: {str(e)}", confidence=0.3)

    async def _generate_answer(self, query: str, session_outputs: list[str], usage: RunUsage) -> tuple[str, Optional[str]]:
        """
        Generate final answer from collected data and create chart if requested.

        Args:
            query: Original user query
            session_outputs: All outputs from task executions
            usage: Shared RunUsage for tracking

        Returns:
            Tuple of (answer, chart) where:
            - answer: Formatted answer in Turkish with disclaimer
            - chart: Optional plotext chart (ANSI string) if graph requested
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
            import sys
            result = await asyncio.wait_for(
                self.answerer.run(answer_prompt, usage=usage),  # Shared usage tracking
                timeout=60.0  # 60 second timeout
            )

            # Get LLM answer
            answer = result.output

            # Create chart separately if requested
            chart = None
            chart_keywords = ['grafik', 'mum grafik', 'candlestick', 'chart', 'plot', 'görselleştir']
            needs_chart = any(keyword in query.lower() for keyword in chart_keywords)

            if needs_chart and session_outputs:
                # Try to create chart from collected data
                chart = self._create_chart_from_data(all_data, query)

            return answer, chart
        except asyncio.TimeoutError:
            error_answer = f"""
❌ Yanıt oluşturma zaman aşımına uğradı (60 saniye).

Toplanan veriler:
{all_data[:500]}...

⚠️ Bu bilgiler sadece bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir.
"""
            return error_answer, None
        except Exception as e:
            error_answer = f"""
❌ Yanıt oluşturulurken hata oluştu: {str(e)}

Toplanan veriler:
{all_data[:500]}...

⚠️ Bu bilgiler sadece bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir.
"""
            return error_answer, None

    def _create_chart_from_data(self, data: str, query: str) -> Optional[str]:
        """
        Create plotext chart from collected data.

        Args:
            data: Collected data string (may contain JSON)
            query: User query for title extraction

        Returns:
            ANSI chart string or None if chart couldn't be created
        """
        try:
            import json
            import re
            import sys

            # Debug: Show what we received
            if "--debug" in sys.argv:
                print(f"\n[DEBUG] Chart data (first 1000 chars):")
                print(data[:1000])
                print(f"\n[DEBUG] Looking for JSON array...")

            # Try JSON first
            json_match = re.search(r'\[\s*\{[^}]*"date"[^}]*"open"[^}]*"high"[^}]*"low"[^}]*"close"[^}]*\}[^\]]*\]', data, re.DOTALL | re.IGNORECASE)

            if json_match:
                json_str = json_match.group(0)

                if "--debug" in sys.argv:
                    print(f"[DEBUG] Found JSON! Length: {len(json_str)}")

                ticker_match = re.search(r'\b([A-Z]{4,6})\b', query.upper())
                title = f"{ticker_match.group(1)} Fiyat Grafiği" if ticker_match else "Fiyat Grafiği"

                chart = create_candlestick_from_json(json_str, title=title)
                return chart

            # Fallback: Parse markdown table
            if "--debug" in sys.argv:
                print(f"[DEBUG] No JSON found, trying markdown table parse...")

            # Try both date formats and column orders since LLM output varies
            # Format 1: YYYY-MM-DD with Open | High | Low | Close
            table_rows = re.findall(r'\|\s*\*?\*?(\d{4}-\d{2}-\d{2})\*?\*?\s*\|\s*([\d.,]+)\s*\|\s*([\d.,]+)\s*\|\s*([\d.,]+)\s*\|\s*([\d.,]+)\s*\|', data)
            format_type = "YYYY-MM-DD"

            # Format 2: DD.MM.YYYY if first format didn't match
            if not table_rows:
                table_rows = re.findall(r'\|\s*\*?\*?(\d{2}\.\d{2}\.\d{4})\*?\*?\s*\|\s*([\d.,]+)\s*\|\s*([\d.,]+)\s*\|\s*([\d.,]+)\s*\|\s*([\d.,]+)\s*\|', data)
                format_type = "DD.MM.YYYY"

            if table_rows:
                if "--debug" in sys.argv:
                    print(f"[DEBUG] Found {len(table_rows)} rows in markdown table (format: {format_type})")

                # Detect column order by looking at table header
                # Common patterns: "Açılış | En Yüksek | En Düşük" or "Açılış | En Düşük | En Yüksek"
                is_high_before_low = bool(re.search(r'Açılış.*En Yüksek.*En Düşük', data, re.IGNORECASE))

                # Build JSON from table
                json_data = []
                for row in table_rows:
                    date_str = row[0]

                    # Convert date to YYYY-MM-DD if needed
                    if format_type == "DD.MM.YYYY":
                        day, month, year = date_str.split('.')
                        date_iso = f"{year}-{month}-{day}"
                    else:
                        date_iso = date_str

                    # Parse values based on detected column order
                    if is_high_before_low:
                        # Open | High | Low | Close
                        acilis, yuksek, dusuk, kapanis = row[1], row[2], row[3], row[4]
                    else:
                        # Open | Low | High | Close
                        acilis, dusuk, yuksek, kapanis = row[1], row[2], row[3], row[4]

                    # Remove thousands separator
                    json_data.append({
                        "date": date_iso,
                        "open": float(acilis.replace(',', '')),
                        "low": float(dusuk.replace(',', '')),
                        "high": float(yuksek.replace(',', '')),
                        "close": float(kapanis.replace(',', ''))
                    })

                json_str = json.dumps(json_data)

                if "--debug" in sys.argv:
                    print(f"[DEBUG] Created JSON from table: {json_str[:200]}...")

                ticker_match = re.search(r'\b([A-Z]{4,6})\b', query.upper())
                title = f"{ticker_match.group(1)} Fiyat Grafiği" if ticker_match else "Fiyat Grafiği"

                chart = create_candlestick_from_json(json_str, title=title)
                return chart

            if "--debug" in sys.argv:
                print(f"[DEBUG] No parseable data found")

            return None

        except Exception as e:
            import sys
            if "--debug" in sys.argv:
                print(f"[DEBUG] Chart creation failed: {e}")
                import traceback
                traceback.print_exc()
            return None
