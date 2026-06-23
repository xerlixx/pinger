---
title: Pinger
emoji: 🏓
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# parking-intelligence-pinger

A minimal FastAPI service that keeps the main [parking-intelligence-backend](https://parking-intelligence-backend.onrender.com) alive on Render's free tier by exchanging mutual HTTP pings every 30 seconds.

## How it works

```
Main Backend  ←──── /wake every 30s ────  This Pinger
     │                                         ↑
     └───── /wake every 30s ───────────────────┘
```

- Both services ping each other's `/wake` endpoint every 30 seconds.
- Neither service goes idle or sleeps.

## Endpoints

| Method | Path      | Description                                  |
|--------|-----------|----------------------------------------------|
| GET    | `/health` | Health-check endpoint                        |
| GET    | `/wake`   | Keep-alive endpoint (called by main backend) |

## Environment Variables

| Key               | Description                                      | Default |
|-------------------|--------------------------------------------------|---------|
| `MAIN_BACKEND_URL`| URL of the main backend to ping (required)       | —       |
| `PING_INTERVAL`   | Seconds between pings                            | `30`    |

## Local Development

```bash
pip install -r requirements.txt
MAIN_BACKEND_URL=https://parking-intelligence-backend.onrender.com uvicorn main:app --reload --port 7860
```