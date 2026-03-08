# -*- coding: utf-8 -*-
"""Automation Agent — Executes tasks through MCP tools, browser automation, and APIs.

Wraps MCP tool calls and automation workflows. Can schedule posts,
trigger publishing, and execute tool-based tasks.
"""

from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register
from agents import mcp_tools
from automation import scheduler


@register
class AutomationAgent(BaseAgent):
    name = "automation"
    role = "automator"
    description = (
        "Executes tasks through MCP tools, browser automation, APIs, and local scripts. "
        "Supports publishing, content scheduling, and data collection."
    )
    tools = list(mcp_tools.available_tools()) if mcp_tools.is_available() else []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Execute an automation action.

        Expected kwargs:
            action (str): 'mcp_call', 'schedule', 'list_tools' (default: 'list_tools')
            tool_name (str): MCP tool name (for mcp_call action).
            tool_args (dict): Arguments for the MCP tool.

        Returns:
            Dict with automation results.
        """
        action = kwargs.get("action", "list_tools")

        if action == "mcp_call":
            return self._call_mcp(
                tool_name=kwargs.get("tool_name", ""),
                tool_args=kwargs.get("tool_args", {}),
            )
        elif action == "schedule":
            return self._get_schedule()
        else:
            return self._list_tools()

    def _call_mcp(self, tool_name: str, tool_args: dict) -> Dict[str, Any]:
        """Execute an MCP tool call."""
        if not tool_name:
            return {"status": "error", "error": "No tool_name specified."}
        result = mcp_tools.call_tool(tool_name, **tool_args)
        return {"status": "success", "tool": tool_name, "result": result}

    def _get_schedule(self) -> Dict[str, Any]:
        """Get the default publishing schedule."""
        return {
            "status": "success",
            "schedule": scheduler.default_schedule(),
        }

    def _list_tools(self) -> Dict[str, Any]:
        """List available automation tools."""
        return {
            "status": "success",
            "mcp_available": mcp_tools.is_available(),
            "mcp_tools": mcp_tools.available_tools(),
        }

    def format_output(self, data: Any) -> str:
        if "tool" in data:
            return f"⚙️ MCP Tool '{data['tool']}': {data.get('result', {}).get('status', 'unknown')}"
        if "schedule" in data:
            import json
            return f"📅 Publishing Schedule:\n{json.dumps(data['schedule'], indent=2)}"
        if "mcp_tools" in data:
            tools = data.get("mcp_tools", [])
            lines = [f"🔧 Available Automation Tools ({len(tools)}):"]
            for t in tools:
                lines.append(f"  • {t}")
            if not tools:
                lines.append("  (No MCP tools installed)")
            return "\n".join(lines)
        return str(data)
