"""AnythingLLM MCP Server (MVP).

Exposes one tool `ask_workspace(message)` that asks the single local
AnythingLLM workspace and returns the AI answer grounded in its documents.

Env vars (all optional, sensible defaults provided):
  ANYTHINGLLM_BASE_URL  default http://localhost:3001
  ANYTHINGLLM_API_KEY    default (the local instance key)
  MCP_PORT               default 8080

Run:
  python server.py
Endpoint: POST http://127.0.0.1:8080/mcp  (Streamable HTTP, protocol 2026-07-28)
"""
import os
import uuid

import httpx
from mcp.server.mcpserver import MCPServer

BASE_URL = os.environ.get("ANYTHINGLLM_BASE_URL", "http://localhost:3001")
API_KEY = os.environ.get("ANYTHINGLLM_API_KEY", "8FT8RX4-N1BMPS2-MBBHYCY-Z0Q9FFZ")
PORT = int(os.environ.get("MCP_PORT", "8080"))

mcp = MCPServer(
    name="anythingllm",
    description="Ask the local AnythingLLM workspace and get an AI answer.",
)


def _headers() -> dict:
    return {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


@mcp.tool(
    name="ask_workspace",
    description=(
        "Ask the AnythingLLM workspace a question. Returns the AI answer "
        "grounded in the workspace documents, plus source titles if any."
    ),
)
async def ask_workspace(message: str) -> str:
    """Ask a question to the single AnythingLLM workspace."""
    try:
        async with httpx.AsyncClient(
            base_url=BASE_URL, headers=_headers(), timeout=120
        ) as client:
            # The instance has exactly one workspace; auto-discover its slug.
            ws = (await client.get("/api/v1/workspaces")).json()
            slug = ws["workspaces"][0]["slug"]
            resp = await client.post(
                f"/api/v1/workspace/{slug}/chat",
                json={
                    "message": message,
                    "mode": "chat",
                    "sessionId": str(uuid.uuid4()),
                },
            )
            data = resp.json()
            if resp.status_code >= 400:
                err = data.get("error") or data
                return f"AnythingLLM error {resp.status_code}: {err}"
            text = (data.get("textResponse") or "").strip()
            sources = [
                s.get("title")
                for s in data.get("sources", [])
                if s.get("title")
            ]
            if sources:
                text += "\n\n来源:\n" + "\n".join(f"- {t}" for t in sources)
            return text or "No response from workspace."
    except Exception as e:  # surface errors to the client, never swallow
        return f"ask_workspace failed: {e}"


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=PORT,
        streamable_http_path="/mcp",
        json_response=True,      # plain JSON responses, no SSE
        stateless_http=True,     # 2026-07-28 stateless core, no sessions
    )
