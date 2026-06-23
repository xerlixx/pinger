# parking-intelligence-pinger

A minimal FastAPI service that keeps the main [parking-intelligence-backend](https://parking-intelligence-backend.onrender.com) alive on Render's free tier by exchanging mutual HTTP pings every 30 seconds.

## How it works

```
Main Backend  ←──── /wake every 30s ────  This Pinger
     │                                         ↑
     └───── /wake every 30s ───────────────────┘
```

- Both services ping each other's `/wake` endpoint every 30 seconds.
- Neither service goes idle, so Render never spins them down.

## Endpoints

| Method | Path      | Description                        |
|--------|-----------|------------------------------------|
| GET    | `/health` | Render health-check                |
| GET    | `/wake`   | Keep-alive endpoint (called by main backend) |

## Deployment

1. Push this folder's contents to a **new GitHub repo**.
2. Create a new **Web Service** on [Render](https://render.com):
   - Connect the new repo
   - Runtime: **Python**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
   - Region: **Singapore** (same as main backend)
3. Set the environment variable:
   - `MAIN_BACKEND_URL` = `https://parking-intelligence-backend.onrender.com`
4. Note the deployed URL (e.g. `https://parking-intelligence-pinger.onrender.com`)
5. Go to the **main backend** service on Render and add:
   - `PINGER_URL` = `https://parking-intelligence-pinger.onrender.com`

## Local development

```bash
pip install -r requirements.txt
MAIN_BACKEND_URL=https://parking-intelligence-backend.onrender.com uvicorn main:app --reload --port 8001
```
