"""Loading animation and ESC cancel support for BorsaCI (native terminal)"""

import asyncio
import sys
import termios
import tty
import select
from typing import TypeVar, Coroutine
from rich.console import Console
from rich.live import Live
from rich.text import Text


T = TypeVar('T')
ESC_KEY = '\x1b'  # ESC key ASCII code


class LoadingAnimation:
    """
    3-dot 'Hazırlanıyor...' animation for Rich display.

    Cycles through frames:
    - "Hazırlanıyor   "
    - "Hazırlanıyor.  "
    - "Hazırlanıyor.. "
    - "Hazırlanıyor..."
    """

    def __init__(self):
        self.message = "Hazırlanıyor"
        self.frames = ["   ", ".  ", ".. ", "..."]
        self.current_frame = 0
        self._cancelled = False

    def __rich__(self):
        """Render current frame for Rich"""
        if self._cancelled:
            return Text("")

        frame = self.frames[self.current_frame % len(self.frames)]
        text = Text(f"{self.message}{frame}", style="cyan")
        if not self._cancelled:
            text.append(" (ESC ile iptal)", style="dim")
        return text

    def next_frame(self):
        """Advance to next animation frame"""
        self.current_frame += 1

    def cancel(self):
        """Mark as cancelled"""
        self._cancelled = True


async def check_esc_key() -> bool:
    """
    Check if ESC key was pressed (non-blocking).

    Returns:
        True if ESC was pressed, False otherwise
    """
    try:
        # Check if input is available (non-blocking)
        if select.select([sys.stdin], [], [], 0)[0]:
            # Read one character
            char = sys.stdin.read(1)
            return char == ESC_KEY
        return False
    except Exception:
        return False


async def run_with_loading_and_cancel(
    coro: Coroutine[None, None, T],
    console: Console | None = None
) -> T:
    """
    Run a coroutine with loading animation and ESC cancel support.

    Uses native terminal handling (termios) to detect ESC key without
    requiring extra permissions (unlike pynput).

    Args:
        coro: Async coroutine to run
        console: Optional Rich console (creates new if None)

    Returns:
        Result from coroutine

    Raises:
        asyncio.CancelledError: If user presses ESC

    Example:
        >>> result = await run_with_loading_and_cancel(agent.run(query))
    """
    if console is None:
        console = Console()

    # Create animation
    animation = LoadingAnimation()

    # Save original terminal settings
    try:
        old_settings = termios.tcgetattr(sys.stdin)
        terminal_changed = True
    except Exception:
        # stdin not a terminal (e.g., piped input)
        terminal_changed = False
        old_settings = None

    # Create task from coroutine
    task = asyncio.create_task(coro)

    try:
        # Set terminal to raw mode if possible (for immediate ESC detection)
        if terminal_changed:
            tty.setraw(sys.stdin.fileno())

        # Display loading animation with ESC monitoring
        with Live(animation, console=console, refresh_per_second=3) as live:
            while not task.done():
                # Check for ESC key
                if terminal_changed and await check_esc_key():
                    animation.cancel()
                    live.update(animation)
                    task.cancel()
                    raise asyncio.CancelledError("İşlem kullanıcı tarafından iptal edildi (ESC)")

                # Update animation frame
                animation.next_frame()
                live.update(animation)

                # Wait a bit before next check (0.3s)
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=0.3)
                    break  # Task completed
                except asyncio.TimeoutError:
                    continue  # Keep waiting

        # Get result
        return await task

    finally:
        # Restore terminal settings
        if terminal_changed and old_settings is not None:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except Exception:
                pass

        # Cancel task if still running
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
