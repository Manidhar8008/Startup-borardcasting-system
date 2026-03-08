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
  Brand: {brand}  |  LLM: llama3 (Ollama)  |  Workflow Mode: ON
  Type 'help' or just:  do create 3 threads about AI agents
"""

HELP_TEXT = """
━━━  WORKFLOW (one command does everything)  ━━━━━━━━━━━━━━━━━━
  do <message>         Natural language — JAN handles the rest

  Examples:
    do create 3 reels about AI agents
    do write 2 linkedin posts on LLM fine tuning
    do make a tutorial on building RAG pipelines
    do research prompt engineering trends

━━━  STEP-BY-STEP COMMANDS  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  morning briefing     Read notes + score topics + LLM plan
  research <topic>     Research a topic
  plan today           Build scored + LLM content plan
  generate drafts      LLM drafts (Hook / Insight / Example / CTA)
  publish drafts       Simulate publishing → records topic memory
  topic insights       Top / recent / recommended topics

━━━  SYSTEM  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  status               Pipeline + memory state
  brand <name>         Switch brand
  help                 This menu
  exit                 Quit JAN
"""


def print_separator():
    print("\n" + "━" * 60)


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

        # ── Exit ──────────────────────────────────────────────────────────────
        if cmd in ("exit", "quit"):
            print("Goodbye! 👋")
            sys.exit(0)

        # ── Help ──────────────────────────────────────────────────────────────
        elif cmd == "help":
            print(HELP_TEXT)

        # ── Workflow shortcut: do <message> ───────────────────────────────────
        elif cmd == "do":
            if not arg:
                print(
                    "⚠️  Usage: do <message>\n"
                    "   Example: do create 3 reels about AI agents"
                )
            else:
                _thinking(f"Interpreting: \"{arg}\" ...")
                print(jan.execute_workflow(arg))

        # ── Morning briefing ──────────────────────────────────────────────────
        elif full_cmd == "morning briefing":
            _thinking("Reading notes + scoring topics + building strategy ...")
            print(jan.morning_briefing())

        # ── Research ──────────────────────────────────────────────────────────
        elif cmd == "research":
            if not arg:
                print("⚠️  Usage: research <topic>")
            else:
                _thinking(f"Researching: {arg} ...")
                print(jan.research(arg))

        # ── Plan ──────────────────────────────────────────────────────────────
        elif full_cmd == "plan today":
            _thinking("Scoring topics + building LLM plan ...")
            print(jan.plan_today())

        # ── Generate ──────────────────────────────────────────────────────────
        elif full_cmd == "generate drafts":
            _thinking("Writing drafts with LLM ...")
            print(jan.generate_drafts())

        # ── Publish ───────────────────────────────────────────────────────────
        elif full_cmd == "publish drafts":
            _thinking("Simulating publish + recording topic memory ...")
            print(jan.publish_drafts(dry_run=True))

        # ── Topic insights ────────────────────────────────────────────────────
        elif full_cmd == "topic insights":
            print(jan.topic_insights())

        # ── Status ────────────────────────────────────────────────────────────
        elif cmd == "status":
            print(jan.status())

        # ── Brand switch ──────────────────────────────────────────────────────
        elif cmd == "brand":
            if not arg:
                print(f"Current brand: {jan.brand}")
            else:
                jan = JanManager(brand=arg)
                print(f"✅ Switched to brand: {arg}")

        # ── Unknown ───────────────────────────────────────────────────────────
        else:
            print(f"❓ Unknown command: '{raw}'")
            print(f"   Tip: Try  do {raw}  to run it as a workflow.")

        print_separator()
