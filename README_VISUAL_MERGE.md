# UPIShield Visual Frontend Merge

This build keeps the existing UPIShield FastAPI/SQLite/NetworkX/risk/cash-out/alerts functionality and applies the visual direction from the Lovable UPIShield Command Center concept.

## Visual direction

- Warm off-white / cream workspace
- UPIShield green as the primary action color
- Orange used for prediction / attention signals
- Restrained red for critical response states
- Editorial oversized command-centre typography
- 3D UPIShield / rupee / hotspot / ATM visual language on the command centre
- Light GIS treatment rather than the previous dark cyberpunk map
- Dense but readable investigation tables
- Rounded controls and surfaces used selectively rather than a generic card grid

## Routes

- `/` — Command Centre
- `/cases/[id]` — Case Investigation
- `/cashout` — Cash-Out Surveillance
- `/alerts` — Alert Dispatch

## Important

The frontend still reads from the existing API client in `frontend/src/lib/api.ts`. No API endpoints or backend contracts were replaced by the visual redesign.

The project continues to use synthetic data only. It does not connect to live UPI/NPCI/banking systems.

## Run

### Backend

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000`.

If the API runs on another host/port, set:

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

before starting Next.js.
