# System Workflows

## Named Pipelines

All workflows are defined in `orchestrator/workflow_manager.py` and executed through the orchestrator.

### `full` — Complete Pipeline
```
research → strategy → content → publish → analytics
```
End-to-end: gather topics, build strategy, generate content, publish, collect analytics.

### `research_only`
```
research
```
Just gather and rank research topics.

### `plan_only`
```
research → strategy
```
Research and build a scored content plan without generating drafts.

### `create_content`
```
research → strategy → content
```
Full content creation pipeline without publishing.

### `publish_flow`
```
publish → analytics
```
Publish existing drafts and collect analytics.

## How Workflows Execute

1. `WorkflowManager.execute("full", initial_input={...})`
2. For each step, `AgentRouter.route(step)` finds the registered agent
3. Agent's `run(**data)` executes with the accumulated pipeline data
4. Agent output is merged into the data dict and passed to the next step
5. Execution log records timing and status for each step

## Adding New Workflows

1. Add the pipeline definition to `PIPELINES` in `workflow_manager.py`
2. Ensure all step names have a mapping in `agent_router.py`
3. Ensure the corresponding agent is registered via `@register`

## CLI Integration

The existing `jan_manager.py` and `chat_interface.py` continue to work as the primary user interface. The orchestrator is available as the architectural backbone for new workflows and API integrations.
