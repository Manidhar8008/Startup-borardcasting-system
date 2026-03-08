"""JAN Chat Interface v4: Department-style CLI (Gemini powered)."""
import sys
from pathlib import Path
from core.jan_manager import JanManager

BANNER = r"""
     ██╗ █████╗ ███╗   ██╗
     ██║██╔══██╗████╗  ██║
     ██║███████║██╔██╗ ██║
██   ██║██╔══██║██║╚██╗██║
╚█████╔╝██║  ██║██║ ╚████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝

  JAN AI Media Manager v4  |  Brand: {brand}
  LLM: {llm}  |  14 Agents  |  8 Departments
"""

HELP_TEXT = """
━━━  DEPARTMENTS  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  intake                    📥 Read founder's PDFs + research notes
  morning briefing          ☀️  Full pipeline: intake → research → plan

━━━  IDEA INTELLIGENCE  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  trends                    📊 Scan trends → rank → generate ideas
  trends <query>            📊 Trend intelligence for specific query
  ideas <topic>             💡 Generate content ideas for a topic
  decide <question>         🤝 Multi-agent consensus on a decision

━━━  PLATFORM WRITERS  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  write linkedin <topic>    📝 Professional LinkedIn post
  write twitter <topic>     🐦 Twitter/X thread (5 tweets)
  write instagram <topic>   📸 Instagram caption + hashtags
  write youtube <topic>     🎬 YouTube video script
  write newsletter <topic>  📧 Newsletter with subject line

━━━  CONTENT MULTIPLICATION  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  multiply <topic>          🔄 1 idea → 22 assets × 9 platforms

━━━  QUALITY + PUBLISHING  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  review                    🔍 Run QC on current drafts (auto-revise)
  publish drafts            📤 Simulate publishing (dry-run)

━━━  PIPELINE (auto-detects)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  <message>                 Type naturally — JAN routes to agents
  research <topic>          📡 Live research (RSS + Perplexity)
  plan today                🧠 Build scored content plan
  generate drafts           ✏️  Generate via content factory

━━━  SYSTEM  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  status                    📊 Pipeline + costs + memory
  topic insights            🧠 Top / recommended topics
  cost                      💰 API usage report
  brand <name>              🔀 Switch brand
  api                       🌐 Start API server (port 8000)
  help                      📖 This menu
  exit                      👋 Quit
"""


def print_separator():
    print("\n" + "━" * 60)


def _thinking(msg: str):
    print(f"\n  ⟳  {msg}", flush=True)


def _get_llm_info() -> str:
    try:
        from ai_core.llm_router import get_active_provider
        return get_active_provider()
    except Exception:
        return "ollama"


def run(brand: str = "janani_ai"):
    jan = JanManager(brand=brand)
    llm = _get_llm_info()
    print(BANNER.format(brand=jan.brand, llm=llm))

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

        elif cmd == "help":
            print(HELP_TEXT)

        # ── Intake ────────────────────────────────────────────────────────────
        elif cmd == "intake":
            _thinking("Reading PDFs + research notes...")
            print(jan.intake(pdf_path=arg))

        # ── Platform Writers ──────────────────────────────────────────────────
        elif full_cmd.startswith("write linkedin"):
            topic = raw[len("write linkedin"):].strip()
            if not topic:
                print("⚠️  Usage: write linkedin <topic>")
            else:
                _thinking(f"Writing LinkedIn post: {topic}")
                print(jan.write_linkedin(topic))

        elif full_cmd.startswith("write twitter"):
            topic = raw[len("write twitter"):].strip()
            if not topic:
                print("⚠️  Usage: write twitter <topic>")
            else:
                _thinking(f"Writing Twitter thread: {topic}")
                print(jan.write_twitter(topic))

        elif full_cmd.startswith("write instagram"):
            topic = raw[len("write instagram"):].strip()
            if not topic:
                print("⚠️  Usage: write instagram <topic>")
            else:
                _thinking(f"Writing Instagram caption: {topic}")
                print(jan.write_instagram(topic))

        elif full_cmd.startswith("write youtube"):
            topic = raw[len("write youtube"):].strip()
            if not topic:
                print("⚠️  Usage: write youtube <topic>")
            else:
                _thinking(f"Writing YouTube script: {topic}")
                print(jan.write_youtube(topic))

        elif full_cmd.startswith("write newsletter"):
            topic = raw[len("write newsletter"):].strip()
            if not topic:
                print("⚠️  Usage: write newsletter <topic>")
            else:
                _thinking(f"Writing newsletter: {topic}")
                print(jan.write_newsletter(topic))

        # ── Multiply ─────────────────────────────────────────────────────────
        elif cmd == "multiply":
            if not arg:
                print("⚠️  Usage: multiply <topic>")
            else:
                _thinking(f"Multiplying across 9 platforms: \"{arg}\"")
                print(jan.multiply(arg))

        # ── Review ────────────────────────────────────────────────────────────
        elif cmd == "review":
            _thinking("Running quality control on drafts...")
            print(jan.review_drafts())

        # ── Idea Intelligence ─────────────────────────────────────────────────
        elif cmd == "trends":
            _thinking(f"Scanning trends{': ' + arg if arg else ''}...")
            print(jan.trends(query=arg or "AI and technology"))

        elif cmd == "ideas":
            if not arg:
                print("⚠️  Usage: ideas <topic>")
            else:
                _thinking(f"Generating ideas for: {arg}")
                print(jan.ideas(arg))

        elif cmd == "decide":
            if not arg:
                print("⚠️  Usage: decide <question>")
            else:
                _thinking(f"Multi-agent consensus: {arg}")
                print(jan.decide(arg))

        # ── Morning briefing ──────────────────────────────────────────────────
        elif full_cmd == "morning briefing":
            _thinking("Intake → Research → Learning → Strategy...")
            print(jan.morning_briefing())

        elif cmd == "research":
            if not arg:
                print("⚠️  Usage: research <topic>")
            else:
                _thinking(f"Researching: {arg}")
                print(jan.research(arg))

        elif full_cmd == "plan today":
            _thinking("Building strategy...")
            print(jan.plan_today())

        elif full_cmd == "generate drafts":
            _thinking("Writing drafts via content factory...")
            print(jan.generate_drafts())

        elif full_cmd == "publish drafts":
            _thinking("Simulating publish...")
            print(jan.publish_drafts(dry_run=True))

        elif full_cmd == "topic insights":
            print(jan.topic_insights())

        elif cmd == "status":
            print(jan.status())

        elif cmd == "cost":
            try:
                from ai_core.cost_controller import get_controller
                print(get_controller().usage_report())
            except Exception as e:
                print(f"⚠️  Cost controller: {e}")

        elif cmd == "api":
            print("🌐 Starting API server on http://localhost:8000")
            print("   Endpoints: /status /ideas /trends /drafts /queue /calendar /analytics")
            print("   POST: /generate /decide")
            import subprocess
            subprocess.Popen(
                ["python", "-m", "uvicorn", "api.server:app", "--reload", "--port", "8000"],
                cwd=str(Path(__file__).resolve().parent.parent),
            )
            print("   Server starting in background...")

        elif cmd == "brand":
            if not arg:
                print(f"Current brand: {jan.brand}")
            else:
                jan = JanManager(brand=arg)
                print(f"✅ Switched to brand: {arg}")

        elif cmd == "do":
            if not arg:
                print("⚠️  Usage: do <message>")
            else:
                _thinking(f"Interpreting: \"{arg}\"")
                print(jan.execute_workflow(arg))

        # ── Fallback: Natural Language ────────────────────────────────────────
        else:
            _thinking(f"Interpreting: \"{raw}\"")
            print(jan.execute_workflow(raw))

        print_separator()
