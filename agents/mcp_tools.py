# -*- coding: utf-8 -*-
"""MCP Tools — Thin wrapper for invoking NotebookLM MCP tools from agents.

Provides a unified call_tool() interface that any agent can import.
The underlying MCP server is accessed via the notebooklm_mcp package.

Usage:
    from agents.mcp_tools import call_tool
    result = call_tool("notebook_list", max_results=10)
"""

import logging
from typing import Any, Dict

logger = logging.getLogger("agent.mcp")

# Try to import the NotebookLM server functions
try:
    from notebooklm_mcp.server import (
        notebook_list,
        notebook_create,
        notebook_get,
        notebook_describe,
        notebook_add_text,
        notebook_add_url,
        notebook_query,
        research_start,
        research_status,
        research_import,
        source_get_content,
        source_describe,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("notebooklm_mcp not available. MCP tools will return stubs.")

# Registry of callable MCP tools
_TOOL_MAP: Dict[str, Any] = {}

if MCP_AVAILABLE:
    _TOOL_MAP = {
        "notebook_list": notebook_list,
        "notebook_create": notebook_create,
        "notebook_get": notebook_get,
        "notebook_describe": notebook_describe,
        "notebook_add_text": notebook_add_text,
        "notebook_add_url": notebook_add_url,
        "notebook_query": notebook_query,
        "research_start": research_start,
        "research_status": research_status,
        "research_import": research_import,
        "source_get_content": source_get_content,
        "source_describe": source_describe,
    }


def call_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Call an MCP tool by name with keyword arguments.

    Args:
        tool_name: Name of the MCP tool (e.g. 'notebook_list').
        **kwargs: Arguments to pass to the tool function.

    Returns:
        Tool result dict. On error or unavailability, returns a status dict.
    """
    if not MCP_AVAILABLE:
        return {"status": "error", "error": "MCP tools not installed."}

    func = _TOOL_MAP.get(tool_name)
    if func is None:
        return {
            "status": "error",
            "error": f"Unknown tool '{tool_name}'. Available: {list(_TOOL_MAP.keys())}",
        }

    try:
        result = func(**kwargs)
        logger.info("MCP tool '%s' executed successfully.", tool_name)
        return result
    except Exception as exc:
        logger.error("MCP tool '%s' failed: %s", tool_name, exc)
        return {"status": "error", "error": str(exc)}


def available_tools() -> list:
    """List all available MCP tool names."""
    return list(_TOOL_MAP.keys())


def is_available() -> bool:
    """Check if MCP tools are installed and accessible."""
    return MCP_AVAILABLE
