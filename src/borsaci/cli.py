"""CLI entry point for BorsaCI - Interactive REPL for Turkish financial markets"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style

from .agent import BorsaAgent
from .utils.ui import print_banner, print_goodbye, print_help, print_error_banner
from .utils.logger import Logger
from .utils.loading import run_with_loading_and_cancel
from .updater import check_and_auto_update


# Custom prompt style
prompt_style = Style.from_dict({
    'prompt': '#00aa00 bold',
})


def write_openrouter_key_to_env(api_key: str):
    """
    Write OpenRouter API key to .env file, creating from template if needed.

    Args:
        api_key: OpenRouter API key to save
    """
    env_path = Path(".env")
    env_example_path = Path(".env.example")

    if env_path.exists():
        # .env exists, update the key
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(env_path, "w", encoding="utf-8") as f:
            found = False
            for line in lines:
                if line.startswith("OPENROUTER_API_KEY="):
                    f.write(f"OPENROUTER_API_KEY={api_key}\n")
                    found = True
                else:
                    f.write(line)

            # If key wasn't in file, add it
            if not found:
                f.write(f"\nOPENROUTER_API_KEY={api_key}\n")

    else:
        # .env doesn't exist, create from template
        if env_example_path.exists():
            with open(env_example_path, "r", encoding="utf-8") as f:
                template = f.read()

            # Replace placeholder with actual key
            content = template.replace(
                "OPENROUTER_API_KEY=sk-or-v1-your_key_here",
                f"OPENROUTER_API_KEY={api_key}"
            )

            with open(env_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            # No template, create minimal .env
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("# BorsaCI Environment Variables\n")
                f.write(f"OPENROUTER_API_KEY={api_key}\n")
                f.write("\n# Optional: OpenRouter app info\n")
                f.write("# HTTP_REFERER=https://borsaci.app\n")
                f.write("# X_TITLE=BorsaCI\n")


async def check_and_setup_openrouter_key(logger: Logger) -> bool:
    """
    Check if OPENROUTER_API_KEY exists, if not prompt user and save to .env.

    Args:
        logger: Logger instance for output

    Returns:
        True if key is valid, False otherwise
    """
    # Check if key exists in environment
    api_key = os.getenv("OPENROUTER_API_KEY")

    # Debug logging
    if "--debug" in sys.argv:
        print(f"[DEBUG] OpenRouter key from env: {api_key[:10] + '...' if api_key else 'None'}")
        print(f"[DEBUG] Key is truthy: {bool(api_key)}")
        if api_key:
            print(f"[DEBUG] Key is not placeholder: {api_key != 'sk-or-v1-your_key_here'}")

    if api_key and api_key != "sk-or-v1-your_key_here":
        # Key exists and is not placeholder
        return True

    # Key missing or is placeholder
    logger.log_warning("OPENROUTER_API_KEY bulunamadı!")
    logger.log_info("OpenRouter API key'inizi alın: https://openrouter.ai/keys")
    print()

    # Create async prompt session
    from prompt_toolkit.shortcuts import PromptSession as AsyncPromptSession

    session = AsyncPromptSession()

    # Prompt user for OpenRouter key
    while True:
        try:
            # Use async prompt
            api_key = await session.prompt_async(
                "OpenRouter API Key: ",
                is_password=True,  # Mask input like password
            )

            # Strip whitespace
            api_key = api_key.strip()

            if not api_key:
                logger.log_error("API key boş olamaz!")
                continue

            # Validate format (OpenRouter keys start with sk-or-v1-)
            if not api_key.startswith("sk-or-v1-"):
                logger.log_error("Geçersiz format! Key 'sk-or-v1-' ile başlamalı.")
                logger.log_info("Örnek: sk-or-v1-xxxxxxxxxxxxxxxxxxxx")
                continue

            # Key looks valid
            break

        except KeyboardInterrupt:
            logger.log_warning("\nKurulum iptal edildi. Program sonlandırılıyor.")
            return False

    # Save to .env file
    try:
        write_openrouter_key_to_env(api_key)
        logger.log_success("OpenRouter API key .env dosyasına kaydedildi!")

        # Load into current environment
        os.environ["OPENROUTER_API_KEY"] = api_key

        return True

    except Exception as e:
        logger.log_error(f".env dosyasına yazılırken hata: {str(e)}")
        logger.log_info("API key'i manuel olarak .env dosyasına ekleyin")
        return False


async def async_main():
    """Async main function for CLI"""
    # Check for updates and auto-update if available
    # (will restart program if update found)
    skip_update = "--skip-update" in sys.argv
    debug = "--debug" in sys.argv
    check_and_auto_update(skip_update=skip_update, debug=debug)

    # Print welcome banner
    print_banner()

    # Load environment variables
    load_dotenv()

    # Initialize logger
    logger = Logger()

    # Check and setup OpenRouter API key if needed
    if not await check_and_setup_openrouter_key(logger):
        logger.log_error("OpenRouter API key gereklidir. Program sonlandırılıyor.")
        sys.exit(1)

    print()  # Empty line for spacing

    # Create agent
    try:
        agent = BorsaAgent()
        logger.log_info("BorsaCI başlatılıyor...")
        logger.log_info(f"MCP Server: {agent.mcp.server_url}")

    except Exception as e:
        print_error_banner(f"Başlatma hatası: {str(e)}")
        logger.log_error("OPENROUTER_API_KEY veya model ayarlarını kontrol edin")

        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()

        sys.exit(1)

    # Create prompt session with history
    session = PromptSession(
        history=InMemoryHistory(),
        style=prompt_style,
    )

    # Main REPL loop with persistent MCP connection
    async with agent:
        logger.log_success("BorsaCI hazır! (MCP bağlantısı kuruldu)")

        # Conversation history stored across queries
        conversation_history = []

        while True:
            try:
                # Prompt for user input
                query = await session.prompt_async([('class:prompt', '>> ')])

                # Handle empty input
                if not query.strip():
                    continue

                # Handle special commands
                query_lower = query.lower().strip()

                if query_lower in ["exit", "quit", "çık", "q"]:
                    print_goodbye()
                    break

                if query_lower in ["help", "yardım", "h", "?"]:
                    print_help()
                    continue

                if query_lower in ["tools", "araçlar"]:
                    logger.log_info(agent.mcp.get_tools_summary())
                    continue

                if query_lower in ["clear", "temizle"]:
                    # Clear screen and conversation history
                    import os
                    os.system('clear' if os.name != 'nt' else 'cls')
                    print_banner()
                    conversation_history = []  # Reset conversation
                    logger.log_info("Sohbet geçmişi temizlendi")
                    continue

                # Process query with agent
                try:
                    logger.log_user_query(query)

                    # Debug logging
                    if "--debug" in sys.argv:
                        print(f"[DEBUG] Calling agent.run() with query: {query[:50]}...")
                        print(f"[DEBUG] Conversation history has {len(conversation_history)} messages")

                    # Run agent with conversation history + loading animation + ESC cancel
                    answer, chart, messages = await run_with_loading_and_cancel(
                        agent.run(query, message_history=conversation_history)
                    )

                    # Update conversation history for next query
                    conversation_history = messages

                    if "--debug" in sys.argv:
                        print(f"[DEBUG] agent.run() returned, answer length: {len(answer)}")
                        print(f"[DEBUG] Chart present: {chart is not None}")
                        print(f"[DEBUG] Updated history now has {len(conversation_history)} messages")

                    # Display answer first
                    logger.log_summary(answer)

                    # Display chart separately if present (rendered directly to terminal)
                    if chart:
                        print()  # Empty line for spacing
                        print(chart)
                        print()  # Empty line after chart

                except asyncio.CancelledError:
                    logger.log_warning("⚠️  İşlem iptal edildi (ESC)")
                    continue

                except KeyboardInterrupt:
                    logger.log_warning("Sorgu iptal edildi")
                    continue

                except Exception as e:
                    logger.log_error(f"Sorgu işlenirken hata: {str(e)}")
                    import traceback
                    if "--debug" in sys.argv:
                        traceback.print_exc()

            except KeyboardInterrupt:
                # Ctrl+C pressed
                logger.log_warning("\nÇıkmak için 'exit' yazın")
                continue

            except EOFError:
                # Ctrl+D pressed
                print_goodbye()
                break

            except Exception as e:
                logger.log_error(f"Beklenmeyen hata: {str(e)}")
                if "--debug" in sys.argv:
                    import traceback
                    traceback.print_exc()


def main():
    """
    Main entry point for BorsaCI CLI.

    Usage:
        borsaci              - Start interactive mode
        borsaci --debug      - Start with debug output
        borsaci --help       - Show help
    """
    # Handle command line arguments
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
BorsaCI - Türk Finans Piyasaları için AI Agent

Kullanım:
    borsaci                  Interactive mode başlat
    borsaci --debug          Debug çıktısı ile başlat
    borsaci --skip-update    Otomatik güncellemeyi atla
    borsaci --help           Bu yardım mesajını göster

Ortam Değişkenleri:
    OPENROUTER_API_KEY   OpenRouter API key (zorunlu)
    HTTP_REFERER         OpenRouter app info (opsiyonel)
    X_TITLE              OpenRouter app başlığı (opsiyonel)
    MAX_STEPS            Maksimum adım sayısı (varsayılan: 20)
    MAX_STEPS_PER_TASK   Görev başına maksimum adım (varsayılan: 5)

Daha fazla bilgi:
    https://github.com/saidsurucu/borsaci
        """)
        sys.exit(0)

    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 veya üzeri gereklidir")
        sys.exit(1)

    # Run async main
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n\nHoşçakalın! 👋")
        sys.exit(0)


if __name__ == "__main__":
    main()
