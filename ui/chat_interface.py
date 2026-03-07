"""JAN Chat Interface: interactive CLI loop."""
import sys
from core.jan_manager import JanManager

BANNER = r"""
     ██╗ █████╗ ███╗   ██╗
     ██║██╔══██╗████╗  ██║
     ██║███████║██╔██╗ ██║
██   ██║██╔══██║██║╚██╗██║
╚█████╔╝██║  ██║██║ ╚████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝

  Your AI Broadcasting Manager
  Brand: {brand}  |  LLM: llama3 (Ollama)  |  Topic Intelligence: ON
  Type 'help' for commands.
"""

HELP_TEXT = """
Available Commands:
  morning briefing    Read notes, research, score topics, build plan  (LLM)
  research <topic>    Research a topic and gather content ideas
  plan today          Build LLM+scored content plan from last research
  generate drafts     Generate LLM drafts (Hook / Insight / Example / CTA)
  publish drafts      Simulate publishing → records topic memory  (dry-run)
  topic insights      Show top performing, recent & recommended topics
  status              Show pipeline and memory state
  brand <name>        Switch active brand
  help                Show this help message
  exit                Quit JAN
"""


def print_separator():
    print("\n" + "─" * 60)


def _thinking(msg: str):
    print(f"\n  ⟳  {msg}", flush=True)


def run(brand: str = "janani_ai"):
    jan = JanManager(brand=brand)
    print(BANNER.format(brand=jan.brand))

    while True:
        try:
            raw = input("JAN ▶  ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            sys.exit(0)

        if not raw:
            continue

        full_cmd = raw.lower().strip()
        parts    = raw.split(maxsplit=1)
        cmd      = parts[0].lower()
        arg      = parts[1] if len(parts) > 1 else ""

        print_separator()

        if cmd in ("exit", "quit"):
            print("Goodbye! 👋")
            sys.exit(0)

        elif cmd == "help":
            print(HELP_TEXT)

        elif full_cmd == "morning briefing":
            _thinking("Reading notes + scoring topics + building strategy with LLM ...")
            print(jan.morning_briefing())

        elif cmd == "research":
            if not arg:
                print("⚠️  Usage: research <topic>")
            else:
                _thinking(f"Researching: {arg} ...")
                print(jan.research(arg))

        elif full_cmd == "plan today":
            _thinking("Scoring topics with Topic Intelligence + building LLM plan ...")
            print(jan.plan_today())

        elif full_cmd == "generate drafts":
            _thinking("Writing drafts with LLM (Hook / Insight / Example / CTA) ...")
            print(jan.generate_drafts())

        elif full_cmd == "publish drafts":
            _thinking("Simulating publish + recording topic memory ...")
            print(jan.publish_drafts(dry_run=True))

        elif full_cmd == "topic insights":
            print(jan.topic_insights())

        elif cmd == "status":
            print(jan.status())

        elif cmd == "brand":
            if not arg:
                print(f"Current brand: {jan.brand}")
            else:
                jan = JanManager(brand=arg)
                print(f"✅ Switched to brand: {arg}")

        else:
            print(f"❓ Unknown command: '{raw}'")
            print("   Type 'help' to see available commands.")

        print_separator()
