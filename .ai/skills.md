# Agent Skills Registry

## Research Agent
- **Role:** Researcher
- **Skills:** PDF analysis, article scraping, arXiv/GitHub trends, YouTube transcript parsing
- **Tools:** `notebook_query`, `research_start`, `source_get_content`
- **Output:** List of topic dicts with title, summary, source

## Strategy Agent
- **Role:** Strategist
- **Skills:** Topic scoring, content planning, platform strategy, growth experiments
- **Tools:** None (uses memory data)
- **Output:** Scored content plan + strategy insights

## Content Agent
- **Role:** Content Creator
- **Skills:** Hook/Insight/Example/CTA generation, multi-platform formatting
- **Tools:** None (uses LLM via ai_core)
- **Output:** Platform-ready drafts

## Publisher Agent
- **Role:** Publisher
- **Skills:** Channel routing, publication simulation, topic memory recording
- **Tools:** None (uses distribution modules)
- **Output:** Publication results with channel mapping

## Analytics Agent
- **Role:** Analyst
- **Skills:** Engagement tracking, performance learning, metric collection
- **Tools:** None
- **Output:** Analytics report + learning cycle status

## Memory Agent
- **Role:** Memory Keeper
- **Skills:** Topic memory CRUD, semantic recall, insight generation
- **Tools:** `notebook_query`, `source_get_content`
- **Output:** Memory records, insights, recommendations

## Automation Agent
- **Role:** Automator
- **Skills:** MCP tool execution, scheduling, browser automation
- **Tools:** All NotebookLM MCP tools, scheduler
- **Output:** Tool execution results
