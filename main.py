"""
pinger/main.py
──────────────────────────────────────────────────────────────────────────────
Minimal FastAPI keep-alive service.

This pinger exists solely to keep the main backend (parking-intelligence-backend
on Render free tier) awake by exchanging mutual HTTP pings every 30 seconds.

Flow:
  1. On startup this service begins pinging MAIN_BACKEND_URL/wake every 30s.
  2. The main backend also pings THIS service's /wake endpoint every 30s.
  3. Either service receiving /wake responds with {"status": "awake"} immediately.
     The ping-back to the other service is handled by the respective service's
     own background loop — no recursive call chains are created.

Env vars (set in Render dashboard):
  MAIN_BACKEND_URL  – e.g. https://parking-intelligence-backend.onrender.com
  PING_INTERVAL     – seconds between pings (default: 30)
  PORT              – injected automatically by Render
"""

import asyncio
import logging
import os

import httpx
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

MAIN_BACKEND_URL = os.getenv("MAIN_BACKEND_URL", "").rstrip("/")
PING_INTERVAL = int(os.getenv("PING_INTERVAL", "30"))


async def ping_loop():
    """Background task: ping the main backend every PING_INTERVAL seconds."""
    if not MAIN_BACKEND_URL:
        log.warning("MAIN_BACKEND_URL not set — pinger loop will not run.")
        return

    await asyncio.sleep(10)  # brief startup delay before first ping

    async with httpx.AsyncClient(timeout=15) as client:
        while True:
            try:
                resp = await client.get(f"{MAIN_BACKEND_URL}/wake")
                log.info(
                    "Pinged main backend → %s %s",
                    resp.status_code,
                    resp.json() if resp.status_code == 200 else "",
                )
            except Exception as exc:
                log.warning("Ping to main backend failed: %s", exc)

            await asyncio.sleep(PING_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(ping_loop())
    log.info(
        "Pinger started — targeting %s every %ds",
        MAIN_BACKEND_URL or "(not configured)",
        PING_INTERVAL,
    )
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Keep-Alive Pinger",
    description="Mutual keep-alive service for parking-intelligence-backend on Render.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Render health-check endpoint."""
    return {"status": "ok", "service": "pinger"}


@app.get("/wake")
async def wake():
    """
    Called by the main backend to keep this service alive.
    Simply acknowledges — the main backend's own ping loop handles
    the return ping, so no recursive call is made here.
    """
    log.info("Received /wake from main backend — staying alive.")
    return {"status": "awake", "service": "pinger"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8001")),
        reload=False,
        log_level="info",
    )
