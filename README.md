# 🧠 JAN AI — Creator Intelligence OS

> **Your AI-powered media manager that automates content creation, distribution, and learning.**

JAN AI is a multi-agent AI platform built for founders, CEOs, CMOs, and creators who want to automate their entire social media pipeline — from reading research notes to publishing platform-optimized content across LinkedIn, Twitter, Instagram, YouTube, and newsletters.

---

## ✨ What It Does

```
📥 Morning Input    →  Read PDFs, notes, research
📊 Trend Scanning   →  RSS, YouTube, Reddit, Google News
🧠 Topic Ranking    →  Score by velocity, relevance, engagement
💡 Idea Generation  →  Post ideas, video ideas, podcast angles
✏️  Content Writing  →  Platform-specific drafts (5 platforms)
🔍 Quality Control  →  Tone, style, engagement, fact checks
🔄 Auto-Revision    →  Failed drafts get rewritten automatically
📤 Publishing       →  Multi-platform distribution
📈 Learning         →  Tracks engagement, learns best schedules
```

---

## 🏗️ Architecture

The system follows a **department-style multi-agent architecture** with 18 AI agents organized into specialized departments:

```
┌─────────────────────────────────────────────────────┐
│                   CONTROLLER AGENT                   │
│              Natural language routing                 │
└─────────────┬───────────────────────┬───────────────┘
              │                       │
  ┌───────────▼──────────┐   ┌───────▼────────────┐
  │  Morning Intake Dept │   │  Trend Intelligence │
  │  • PDF reader        │   │  • TrendAgent       │
  │  • Note ingestion    │   │  • TopicRanker      │
  └───────────┬──────────┘   │  • IdeaGenerator    │
              │              └───────┬────────────┘
              │                      │
  ┌───────────▼──────────────────────▼────────────┐
  │              STRATEGY DEPARTMENT               │
  │  • Content planning  • Topic scoring           │
  └───────────────────────┬───────────────────────┘
                          │
  ┌───────────────────────▼────────────────────────┐
  │              CONTENT FACTORY                    │
  │  LinkedIn │ Twitter │ Instagram │ YouTube │ NL  │
  └───────────────────────┬────────────────────────┘
                          │
  ┌───────────────────────▼────────────────────────┐
  │  Quality Control → Auto-Revision (max 2 rounds)│
  └───────────────────────┬────────────────────────┘
                          │
  ┌───────────────────────▼────────────────────────┐
  │  Publishing → Analytics → Learning Engine       │
  └────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
jan-ai/
├── agents/                    # 🤖 AI Agents (18 total)
│   ├── base_agent.py          #    Base class with Observe→Think→Act→Evaluate loop
│   ├── controller_agent.py    #    Natural language command router
│   ├── morning_intake_agent.py#    PDF & research note reader
│   ├── trend_agent.py         #    Multi-source trend detection
│   ├── topic_ranker.py        #    5-dimension topic scoring
│   ├── idea_generator.py      #    Content idea factory
│   ├── research_agent.py      #    RSS + Perplexity research
│   ├── strategy_agent.py      #    Content plan & scoring
│   ├── content_agent.py       #    Multi-format draft generation
│   ├── review_agent.py        #    QC with auto-revision loop
│   ├── publisher_agent.py     #    Multi-platform publishing
│   ├── analytics_agent.py     #    Engagement tracking
│   ├── memory_agent.py        #    Vector memory management
│   ├── automation_agent.py    #    Scheduled workflows
│   └── writers/               #    Platform-specific writers
│       ├── linkedin_writer.py
│       ├── twitter_writer.py
│       ├── instagram_writer.py
│       ├── youtube_writer.py
│       └── newsletter_writer.py
│
├── ai_core/                   # 🧬 AI Intelligence Layer
│   ├── llm_router.py          #    LLM provider routing (Gemini)
│   ├── gemini_brain.py        #    Gemini API integration
│   ├── cost_controller.py     #    API cost tracking & limits
│   ├── consensus_engine.py    #    Multi-agent weighted consensus
│   ├── performance_learner.py #    Schedule + template + growth learning
│   ├── topic_scorer.py        #    Topic ranking engine
│   └── workflow_interpreter.py#    Natural language → pipeline
│
├── core/                      # ⚙️ Core System
│   └── jan_manager.py         #    Main orchestrator (JanManager)
│
├── orchestrator/              # 🔀 Pipeline Routing
│   └── agent_router.py        #    Step → Agent mapping (22 steps)
│
├── api/                       # 🌐 REST API (FastAPI)
│   └── server.py              #    9 endpoints + dashboard serving
│
├── dashboard/                 # 🎨 Web Dashboard
│   ├── index.html             #    8-page SPA
│   ├── style.css              #    Dark glassmorphism theme
│   └── app.js                 #    API integration + interactivity
│
├── ui/                        # 💻 CLI Interface
│   └── chat_interface.py      #    Interactive terminal chat
│
├── decision_engine/           # ✅ Approval & Routing
│   └── approval_queue.py      #    Draft review queue
│
├── memory_engine/             # 🗄️ Vector Memory (ChromaDB)
│   └── vector_store.py
│
├── brain_input/               # 📄 Input Sources
│   └── (PDFs, notes, research)
│
├── knowledge_base/            # 📚 Stored Knowledge
├── prompts/                   # 📝 Prompt Templates
├── analytics_engine/          # 📊 Engagement Analytics
├── content_engine/            # 📦 Content Processing
├── network_engine/            # 🌍 External Integrations
├── distribution/              # 📤 Publishing Connectors
├── media_engine/              # 🖼️ Media Processing
├── logs/                      # 📋 System Logs
│
├── main.py                    # 🚀 CLI Entry Point
├── run_jan.py                 # 🚀 Alternative Entry Point
├── requirements.txt           # 📦 Dependencies
├── .env.example               # 🔑 Environment template
└── .env                       # 🔑 Your API keys (not in git)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install google-generativeai chromadb pdfplumber
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Run the CLI

```bash
python main.py chat
```

### 4. Run the Dashboard

```bash
python -m uvicorn api.server:app --reload --port 8000
# Open http://localhost:8000
```

---

## 💬 CLI Commands

| Command | Description |
|---|---|
| `trends` | Scan trends → rank → generate ideas |
| `trends <query>` | Trend intelligence for a specific query |
| `ideas <topic>` | Generate content ideas |
| `decide <question>` | Multi-agent consensus |
| `write linkedin <topic>` | Write a LinkedIn post |
| `write twitter <topic>` | Write a Twitter thread |
| `write instagram <topic>` | Write an Instagram caption |
| `write youtube <topic>` | Write a YouTube script |
| `write newsletter <topic>` | Write a newsletter |
| `multiply <topic>` | 1 idea → content for all platforms |
| `morning briefing` | Full pipeline: intake → research → plan |
| `review` | Quality control on drafts |
| `publish drafts` | Publish (dry-run) |
| `status` | System status |
| `api` | Start the API server |

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Dashboard UI |
| `/status` | GET | System status |
| `/trends` | GET | Trend signals |
| `/ideas` | GET | Idea feed |
| `/drafts` | GET | Current drafts |
| `/queue` | GET | Approval queue |
| `/calendar` | GET | Content calendar |
| `/analytics` | GET | Learning data |
| `/generate` | POST | Generate content |
| `/decide` | POST | Multi-agent consensus |

---

## 🤖 Agent System

**18 agents** with an **Observe → Think → Act → Evaluate** reasoning loop:

| Agent | Department | Purpose |
|---|---|---|
| Controller | Gateway | Routes natural language commands |
| Morning Intake | Intake | Reads PDFs & research notes |
| Trend Agent | Intelligence | Multi-source trend detection |
| Topic Ranker | Intelligence | 5-dimension topic scoring |
| Idea Generator | Intelligence | Content angles & ideas |
| Research Agent | Research | RSS, YouTube, Perplexity |
| Strategy Agent | Strategy | Content plan & scoring |
| Content Agent | Factory | Multi-format drafts |
| LinkedIn Writer | Factory | Professional posts |
| Twitter Writer | Factory | Threads & tweets |
| Instagram Writer | Factory | Captions & hashtags |
| YouTube Writer | Factory | Scripts & descriptions |
| Newsletter Writer | Factory | Email content |
| Review Agent | QC | Style, tone, engagement, facts |
| Publisher Agent | Distribution | Multi-platform publishing |
| Analytics Agent | Analytics | Engagement tracking |
| Memory Agent | Memory | Vector store management |
| Automation Agent | System | Scheduled workflows |

---

## 🧬 Key Features

- **Trend Intelligence** — Scans RSS, YouTube, Reddit, Google News for trending topics
- **5-Dimension Topic Scoring** — Velocity, relevance, founder interest, engagement, recency
- **Multi-Agent Consensus** — Multiple agents vote on decisions with weighted scoring
- **Auto-Revision Loop** — Failed drafts get rewritten up to 2 times before flagging
- **Learning Engine** — Learns optimal posting schedules, winning content templates, growth metrics
- **Cost Controller** — Tracks and limits API spend per day
- **Vector Memory** — ChromaDB-powered semantic search across all content
- **Natural Language CLI** — Type naturally, JAN routes to the right agent

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| LLM | Google Gemini |
| Vector DB | ChromaDB |
| API | FastAPI + Uvicorn |
| Frontend | HTML + CSS + Vanilla JS |
| CLI | Python (Interactive) |
| PDF Reading | pdfplumber |
| Research | RSS (feedparser) + BeautifulSoup |

---

## 📊 Dashboard

The web dashboard provides a visual command center with:

- **Dark glassmorphism** design with ambient gradient effects
- **8 pages**: Dashboard, Trends, Ideas, Content Factory, Queue, Calendar, Analytics, Agents
- **Real-time API** connection to all backend agents
- **Keyboard shortcuts** (1-8) for instant navigation
- **Fully responsive** — works on desktop and mobile

---

## 🗺️ Roadmap

- [ ] Real-time publishing connectors (LinkedIn API, Twitter API)
- [ ] Webhook-based approval flow
- [ ] Multi-brand management dashboard
- [ ] Scheduled content automation (cron-based)
- [ ] A/B testing for content variations
- [ ] Team collaboration features
- [ ] Mobile app (React Native)

---

## 📄 License

Private — Manidhar Intelligence System

---

*Built with ❤️ by the JAN AI team*
