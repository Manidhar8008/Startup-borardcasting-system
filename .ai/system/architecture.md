# AI Infrastructure Architecture

## Project Structure

```text
Startup_broadcasting_engine/
├── agents/             # Core agent logic and routing
├── ai_core/            # LLM interfaces and shared prompts
├── analytics_engine/   # Metrics collection and strategy feedback
├── automation/         # Workflow execution and MCP tool usage
├── brain_input/        # Ingestion of PDFs, notes, transcripts, etc.
├── content_engine/     # Generation of posts, scripts, outlines
├── core/               # App configuration and core utilities
├── databases/          # Relational and document databases
├── decision_engine/    # Orchestrator and task routing
├── distribution/       # Outbound channels
├── knowledge_base/     # Static and dynamic knowledge
├── logs/               # System and agent logs
├── media_assets/       # Images, video, audio
├── media_engine/       # Media processing and generation
├── memory/             # Vector memory storage representations
├── memory_engine/      # Semantic retrieval and context expansion
├── network_engine/     # API connectors and integrations
├── research/           # Idea extraction and insight generation
├── tools_connectors/   # MCP tools and API wrappers
└── ui/                 # Frontend interfaces
```

## Agent Architecture

A multi-agent system designed for the Creator Intelligence Platform and Personal Media Manager.

### Core Agents

1. **Controller Agent**: The main orchestrator layer (agent_router, workflow_manager, task_queue).
2. **Research Agent**: Analyzes PDFs, notes, bookmarks, transcripts, and articles to extract ideas, insights, trends, and hooks.
3. **Strategy Agent**: Determines content topics, platform strategy, posting schedules, and growth experiments.
4. **Content Agent**: Generates platform-specific content (LinkedIn posts, Twitter threads, IG captions, Reels/Shorts scripts, blog outlines).
5. **Automation Agent**: Executes tasks through MCP tools, browser automation, API connectors, and local scripts.
6. **Publishing Agent**: Formats content, posts to platforms, and schedules publishing.
7. **Analytics Agent**: Collects impressions, engagement, and performance metrics. Feeds results into the Strategy Agent.
8. **Memory Agent**: Manages vector memory for past posts, research knowledge, user preferences, and performance analytics.

## Workflow Orchestration

Execution pipeline example:
`research` → `strategy` → `content` → `automation` → `publishing` → `analytics`

Agents do not run randomly. All actions must pass through the orchestrator. Let MCP tool availability guide implementation before writing pure code from scratch.
