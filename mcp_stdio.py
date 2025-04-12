import sys
import json
import traceback
import uuid
import asyncio
from playwright.async_api import async_playwright
import aiohttp

# Security token, optional
TOKEN = "letmein"

# === HTML Fetcher ===
async def get_html(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()

# === Screenshot Generator ===
async def get_screenshot(url: str):
    path = f"/tmp/{uuid.uuid4()}.png"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.screenshot(path=path, full_page=True)
        await browser.close()
    with open(path, "rb") as f:
        return f.read()

# === Main Event Loop ===
async def handle_message(msg):
    print(f"[MCP] Received: {msg}", file=sys.stderr)

    try:
        payload = json.loads(msg)

        if payload.get("type") == "ping":
            print(json.dumps({"type": "pong"}))
            sys.stdout.flush()
            return

        tool = payload["name"]
        args = payload.get("input", {})

        if tool == "get_html":
            result = await get_html(args["url"])
            print(json.dumps({"type": "tool_result", "content": result}))
            sys.stdout.flush()

        elif tool == "get_screenshot":
            result = await get_screenshot(args["url"])
            print(json.dumps({
                "type": "tool_result",
                "content": {"mime_type": "image/png", "data": result.hex()}
            }))
            sys.stdout.flush()

        else:
            raise ValueError(f"Unknown tool: {tool}")

    except Exception as e:
        print(json.dumps({
            "type": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }))
        sys.stdout.flush()

async def main():
    print("[MCP] starting", file=sys.stderr)
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        await handle_message(line.strip())

if __name__ == "__main__":
    asyncio.run(main())
