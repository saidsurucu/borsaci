"""UI utilities for BorsaCI - banner, progress indicators, etc."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box


console = Console()


def print_banner():
    """Print BorsaCI welcome banner"""
    banner_text = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ██████╗  ██████╗ ██████╗ ███████╗ █████╗  ██████╗██╗   ║
║   ██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝██║   ║
║   ██████╔╝██║   ██║██████╔╝███████╗███████║██║     ██║   ║
║   ██╔══██╗██║   ██║██╔══██╗╚════██║██╔══██║██║     ██║   ║
║   ██████╔╝╚██████╔╝██║  ██║███████║██║  ██║╚██████╗██║   ║
║   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝   ║
║                                                          ║
║         Türk Finans Piyasaları için AI Agent             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""

    info = """
[bold cyan]Hoş geldiniz![/bold cyan] 👋

BorsaCI, Borsa MCP ile entegre 43 finansal araç kullanarak
Türk ve global piyasalara dair sorularınızı yanıtlar.

[bold]Kapsam:[/bold]
  📈 BIST hisseleri ve endeksler (758 şirket)
  💼 TEFAS yatırım fonları (800+ fon)
  ₿ Kripto paralar (BtcTurk, Coinbase)
  💱 Döviz kurları ve emtia fiyatları
  📊 Makro ekonomik veriler ve enflasyon

[bold]Kullanım:[/bold]
  >> Sorularınızı Türkçe yazın
  >> Çıkmak için: exit, quit, çık

[dim]Models: Multi-Agent Setup via OpenRouter[/dim]
[dim]  Planning: Gemini 2.5 Pro | Others: Gemini 2.5 Flash[/dim]
"""

    console.print(banner_text, style="bold green")
    console.print(
        Panel(
            info,
            border_style="cyan",
            box=box.ROUNDED,
        )
    )
    console.print()


def print_goodbye():
    """Print goodbye message"""
    console.print()
    console.print(
        Panel(
            "[bold cyan]Hoşçakalın! 👋[/bold cyan]\n\n"
            "BorsaCI'yi kullandığınız için teşekkürler.\n"
            "[dim]github.com/saidsurucu/borsaci[/dim]",
            border_style="green",
            box=box.ROUNDED,
        )
    )


def print_error_banner(error: str):
    """Print error in a panel"""
    console.print()
    console.print(
        Panel(
            f"[bold red]Hata:[/bold red]\n\n{error}",
            title="❌ Error",
            border_style="red",
        )
    )


def print_help():
    """Print help information"""
    help_text = """
[bold cyan]BorsaCI Yardım[/bold cyan]

[bold]Temel Komutlar:[/bold]
  exit, quit, çık     - Programdan çık
  help, yardım        - Bu yardım mesajını göster
  clear, temizle      - Ekranı ve sohbet geçmişini temizle
  tools, araçlar      - Mevcut MCP araçlarını listele

[bold]Örnek Sorular:[/bold]
  • "ASELS hissesinin son çeyrek gelir büyümesi nedir?"
  • "En iyi performans gösteren 5 A tipi fonu listele"
  • "Bitcoin TRY fiyatı ve son 24 saatteki değişim"
  • "Teknoloji sektöründeki şirketleri karşılaştır"
  • "Son enflasyon rakamları ve döviz kurları"

[bold]Özellikler:[/bold]
  ✓ 43 Borsa MCP aracı
  ✓ Multi-agent task planning
  ✓ Türkçe native support
  ✓ Real-time financial data
  ✓ Safety limits & error recovery

[dim]Daha fazla bilgi: github.com/saidsurucu/borsaci[/dim]
"""
    console.print(
        Panel(
            help_text,
            border_style="blue",
            box=box.ROUNDED,
        )
    )


def show_thinking():
    """Show thinking indicator"""
    console.print("[dim]🤔 Düşünüyor...[/dim]")


def show_progress(message: str):
    """Show progress message"""
    console.print(f"[dim]{message}[/dim]")
