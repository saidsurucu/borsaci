"""Colored logging utilities for BorsaCI"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.ansi import AnsiDecoder
from typing import Optional
import re


class Logger:
    """Rich-based logger for beautiful terminal output"""

    def __init__(self):
        self.console = Console()

    def log_user_query(self, query: str):
        """Log user query in a panel"""
        self.console.print()
        self.console.print(
            Panel(
                f"[bold cyan]{query}[/bold cyan]",
                title="[bold]💬 Kullanıcı Sorusu[/bold]",
                border_style="cyan",
            )
        )

    def log_task_list(self, tasks: list[dict]):
        """Log planned tasks in a table"""
        if not tasks:
            self.console.print("[yellow]⚠️  Görev bulunamadı[/yellow]")
            return

        table = Table(
            title="📋 Planlanan Görevler",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("ID", style="dim", width=6)
        table.add_column("Görev", style="white")
        table.add_column("Araç", style="cyan")

        for task in tasks:
            table.add_row(
                str(task.get("id", "?")),
                task.get("description", ""),
                task.get("tool_name", "TBD"),
            )

        self.console.print(table)

    def log_task_start(self, description: str):
        """Log when a task starts"""
        self.console.print(f"\n🔧 [bold]{description}[/bold]")

    def log_task_done(self, description: str):
        """Log when a task is completed"""
        self.console.print(f"   ✅ [green]Tamamlandı: {description}[/green]")

    def log_tool_run(self, tool_name: str, result: str):
        """Log tool execution"""
        # Truncate long results
        result_preview = result[:100] + "..." if len(result) > 100 else result
        self.console.print(
            f"   🔨 [cyan]{tool_name}[/cyan]: [dim]{result_preview}[/dim]"
        )

    def log_summary(self, answer: str):
        """Log final answer with markdown rendering and ANSI chart support"""
        self.console.print()
        self.console.print("[bold green]📊 Sonuç[/bold green]")
        self.console.print()

        # Check if answer contains ANSI escape codes (plotext charts)
        # ANSI codes start with ESC (0x1b or \x1b or \033)
        has_ansi = bool(re.search(r'\x1b\[', answer))

        if has_ansi:
            # Split answer into text and chart parts
            # plotext charts are typically large blocks of ANSI-encoded content
            # We'll render ANSI parts as-is and markdown parts with Markdown()
            decoder = AnsiDecoder()

            # For now, render the whole answer with ANSI decoder
            # This preserves plotext colors while still showing text
            decoded = decoder.decode(answer)
            for segment in decoded:
                self.console.print(segment)
        else:
            # No ANSI codes, use normal markdown rendering
            self.console.print(Markdown(answer))

        self.console.print()

    def log_error(self, error: str):
        """Log error message"""
        self.console.print(f"\n[bold red]❌ Hata:[/bold red] {error}")

    def log_warning(self, warning: str):
        """Log warning message"""
        self.console.print(f"[bold yellow]⚠️  Uyarı:[/bold yellow] {warning}")

    def log_info(self, message: str):
        """Log info message"""
        self.console.print(f"[blue]ℹ️  {message}[/blue]")

    def log_success(self, message: str):
        """Log success message"""
        self.console.print(f"[bold green]✅ {message}[/bold green]")

    def _log(self, message: str, style: Optional[str] = None):
        """Internal logging method"""
        if style:
            self.console.print(f"[{style}]{message}[/{style}]")
        else:
            self.console.print(message)
