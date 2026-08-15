# Contributor Map

## System purpose

Startup Broadcasting System is an AI-powered manager/automation platform for solopreneurs.

## Existing high-level areas

- `agents/` — agent implementations
- `accounts/` — account/configuration definitions
- `.ai/` — AI instructions, rules, skills, architecture, workflows
- `agent_server.py` — server entry point
- `README.md` — project overview

## Recommended contribution flow

Issue -> branch -> implementation -> test -> PR -> review -> merge.

## Where to add new work

### New agent
Add it under `agents/`, register it through the existing agent registry, and document its role.

### New workflow
Document the trigger, inputs, processing stages, outputs, failures, and external dependencies.

### New integration
Keep credentials in environment variables and isolate the provider client from business logic.

### New UI / application surface
Create a clearly named module rather than mixing UI logic into core agents.

## Do not

- Commit secrets.
- Rewrite unrelated architecture during a small task.
- Add a dependency without documenting why it is needed.
- Make an agent impossible to test independently.
