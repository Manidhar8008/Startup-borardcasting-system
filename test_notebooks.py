import asyncio
from notebooklm_mcp.api_client import NotebookLMClient
from notebooklm_mcp.server import get_cookies

async def main():
    try:
        client = NotebookLMClient(get_cookies())
        notebooks = await client.list_notebooks()
        print(f"Successfully retrieved {len(notebooks)} notebooks:")
        for nb in notebooks:
            if hasattr(nb, 'title'):
                print(f"- {nb.title}")
            elif isinstance(nb, dict):
                print(f"- {nb.get('title', 'Unknown')}")
            else:
                print(f"- {nb}")
    except Exception as e:
        print(f"Error fetching notebooks: {e}")

if __name__ == "__main__":
    asyncio.run(main())
