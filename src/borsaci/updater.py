"""Auto-update functionality for BorsaCI from GitHub"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
import urllib.request
import json


GITHUB_REPO = "saidsurucu/borsaci"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/commits/main"
GITHUB_API_TIMEOUT = 300  # seconds


def is_git_repo() -> bool:
    """Check if running from a git repository."""
    try:
        # Find .git directory by going up from current file
        current = Path(__file__).parent
        while current != current.parent:
            if (current / ".git").exists():
                return True
            current = current.parent
        return False
    except Exception:
        return False


def get_git_root() -> Optional[Path]:
    """Get git repository root directory."""
    try:
        current = Path(__file__).parent
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return None
    except Exception:
        return None


def get_local_commit() -> Optional[str]:
    """Get local git commit hash."""
    try:
        git_root = get_git_root()
        if not git_root:
            return None

        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None


def get_remote_commit() -> Optional[str]:
    """Get remote commit hash from GitHub API."""
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "BorsaCI-Updater",
            }
        )

        with urllib.request.urlopen(req, timeout=GITHUB_API_TIMEOUT) as response:
            data = json.loads(response.read().decode())
            return data.get("sha")
    except Exception:
        return None


def perform_git_pull() -> bool:
    """Execute git pull to update repository."""
    try:
        git_root = get_git_root()
        if not git_root:
            return False

        # Fetch latest changes
        result = subprocess.run(
            ["git", "fetch", "origin", "main"],
            cwd=git_root,
            capture_output=True,
            timeout=300,
        )

        if result.returncode != 0:
            return False

        # Pull changes
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=git_root,
            capture_output=True,
            timeout=300,
        )

        return result.returncode == 0
    except Exception:
        return False


def restart_program():
    """Restart the current Python program with same arguments."""
    try:
        # Use os.execv to replace current process
        python = sys.executable
        os.execv(python, [python] + sys.argv)
    except Exception as e:
        print(f"Restart failed: {e}")
        sys.exit(1)


def check_and_auto_update(skip_update: bool = False, debug: bool = False) -> bool:
    """
    Check for updates and automatically update if available.

    Args:
        skip_update: If True, skip update check (for testing)
        debug: If True, print debug messages

    Returns:
        True if update was performed (program will restart)
        False if no update or update skipped
    """
    # Skip if --skip-update flag
    if skip_update:
        if debug:
            print("[DEBUG] Auto-update skipped (--skip-update flag)")
        return False

    # Skip if not a git repository
    if not is_git_repo():
        if debug:
            print("[DEBUG] Not a git repository, skipping update")
        return False

    try:
        from rich.console import Console
        from rich.spinner import Spinner
        from rich.live import Live

        console = Console()

        # Show checking message
        with Live(Spinner("dots", text="Güncelleme kontrol ediliyor..."), console=console, transient=True):
            # Get local commit
            local_commit = get_local_commit()
            if not local_commit:
                if debug:
                    console.print("[yellow]⚠️  Local commit alınamadı[/yellow]")
                return False

            # Get remote commit
            remote_commit = get_remote_commit()
            if not remote_commit:
                if debug:
                    console.print("[yellow]⚠️  GitHub API'ye erişilemedi[/yellow]")
                return False

            if debug:
                console.print(f"[dim]Local:  {local_commit[:7]}[/dim]")
                console.print(f"[dim]Remote: {remote_commit[:7]}[/dim]")

            # Check if update needed
            if local_commit == remote_commit:
                if debug:
                    console.print("[green]✅ Güncel versiyon kullanılıyor[/green]")
                return False

        # Update available - show message
        console.print("[cyan]🔄 Yeni versiyon bulundu! Güncelleme yapılıyor...[/cyan]")

        # Perform git pull
        with Live(Spinner("dots", text="Git pull yapılıyor..."), console=console, transient=True):
            success = perform_git_pull()

        if success:
            console.print("[bold green]✅ Güncelleme tamamlandı! Program yeniden başlatılıyor...[/bold green]")
            console.print()

            # Restart program
            restart_program()
            # If we reach here, restart failed
            return False
        else:
            console.print("[yellow]⚠️  Git pull başarısız oldu, mevcut versiyon ile devam ediliyor[/yellow]")
            return False

    except ImportError:
        # Rich not available, fail silently
        if debug:
            print("⚠️  Rich not available, skipping update UI")
        return False

    except Exception as e:
        if debug:
            print(f"⚠️  Update check failed: {e}")
        return False
