# UPIShield: Proactive Cybercrime Intelligence & Cash-Out Prediction Framework

> **SIH Problem Statement SIH26184 — Working Prototype**  
> *Note: This software uses 100% synthetic/simulated transaction and cybercrime data. It does **NOT** connect to live banking networks, UPI/NPCI gateways, production NCRP databases, or real personal financial records.*

---

## 📌 1. Project Overview & SIH26184 Context

Financial cyber fraud across UPI is characterized by rapid, multi-hop money routing through layered "mule" bank accounts, followed by swift physical cash withdrawals at ATMs and Customer Service Points (CSPs / BC Agents) before law enforcement or banks can respond.

**UPIShield (SIH26184 Edition)** introduces a proactive intelligence and interception pipeline:
1. **NCRP / 1930 Complaint Ingestion & Case Convergence**: Aggregates incident reports to discover multi-victim fraud operations converging onto shared mule hubs.
2. **UPIShield Dual-Layer Risk Engine**: Computes financial risk scores combining cold-start resilient general rules (for newly created accounts) and statistical behavioral profiling (for account takeovers).
3. **NetworkX Multi-Hop Entity Graph**: Maps victim payments, Layer-1 convergent mule hubs, Layer-2 distribution accounts, and terminal runner tokens.
4. **Gradient-Boosted Cash-Out Location Predictor**: Uses machine learning to rank candidate ATM/CSP locations based on routing velocity, spatial proximity, and historical syndicate withdrawal density.
5. **Interactive Leaflet GIS Hotspot Surveillance**: Displays high-risk withdrawal geofences and predicted locations on an interactive dark-mode map.
6. **Actionable LEA / Bank / I4C Alert Dispatch**: Simulates real-time tactical alert transmission with debit freeze codes and field interception instructions.

---

## 🏗️ 2. System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 UPIShield Frontend (Next.js 14 + Tailwind)                        │
│                                                                                                  │
│  ┌───────────────────────┐  ┌────────────────────────┐  ┌────────────────────────────────────┐  │
│  │   Command Dashboard   │  │   Case Investigation    │  │   ATM/CSP Cashout Predictor & GIS  │  │
│  │   (/)                 │  │   (/cases/[id])         │  │   (/cashout)                       │  │
│  └───────────┬───────────┘  └───────────┬────────────┘  └─────────────────┬──────────────────┘  │
└──────────────┼──────────────────────────┼─────────────────────────────────┼─────────────────────┘
               │                          │                                 │
               ▼                          ▼                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  FastAPI Backend (Port 8000)                                     │
│                                                                                                  │
│   • /api/dashboard               • /api/complaints              • /api/locations                 │
│   • /api/cases                   • /api/cases/{id}/network      • /api/cases/{id}/predict-cashout│
│   • /api/alerts                  • /api/health                                                   │
└──────┬───────────────────────┬───────────────────────────────┬────────────────────────────┬──────┘
       │                       │                               │                            │
       ▼                       ▼                               ▼                            ▼
┌──────────────┐       ┌──────────────┐                ┌──────────────┐             ┌──────────────┐
│  UPIShield   │       │   NetworkX   │                │ scikit-learn │             │    SQLite    │
│  Risk Engine │       │ Multi-Hop    │                │ GradientTree │             │  Relational  │
│ (src/ modules)│      │ Mule Graph   │                │ Cashout Model│             │  Database    │
└──────────────┘       └──────────────┘                └──────────────┘             └──────────────┘
```

---

## 🎯 3. Core Demonstration Flow (Vertical Slice)

1. **Operational Command Dashboard (`http://localhost:3000`)**:
   - Live metrics: Total Complaints, High-Risk Cases, Amount at Risk (INR), Active ATM Hotspots.
   - GIS Heatmap showing NCRP complaints and flagged ATM/CSP nodes across Delhi-NCR.
   - Priority investigation list showing **Demo Case `#4401`**.

2. **Case Investigation View (`http://localhost:3000/cases/CASE-2026-4401`)**:
   - **UPIShield Financial Risk Gauge**: Displays real-time 0–100 score (e.g., 95/100 `BLOCK`), decomposing Layer-1 General Risk (high-value burst, new device, unknown beneficiary) and Layer-2 Behavioral Deviations.
   - **NetworkX Multi-Hop Flow**: Inspects 4-tier pipeline: Victims &rarr; L1 Mule Hub &rarr; L2 Distribution &rarr; Terminal ATM/Runner Nodes.
   - **Convergent Complaints Table**: Lists correlated 1930 victim reports.

3. **ATM/CSP Cash-Out Predictor (`http://localhost:3000/cashout`)**:
   - Gradient-Boosted ML ranking of top candidate withdrawal points (e.g. *SBI 24x7 E-Corner Rohini* - 95.0% probability, *Airtel Payments Bank CSP Laxmi Nagar* - 77.5%).
   - Estimated withdrawal time window (e.g., *Next 30–90 mins*) and distance from last hop.
   - Spatial map centering on candidate pins with risk-level badges.

4. **Alerts & Multi-Agency Dispatch (`http://localhost:3000/alerts`)**:
   - Filter by stakeholder: **Police Cyber Cell (LEA)**, **Bank Fraud Nodal**, **I4C Central Registry**.
   - Review dispatched actionable intelligence cards with debit freeze codes and tactical notes.

---

## 🚀 4. Quickstart & Running Instructions

### Prerequisites
- **Python 3.9+** (Tested on Python 3.13)
- **Node.js 18+** / npm

### Step 1: Clone & Setup Environment
```bash
# In project root:
pip install -r requirements.txt
```

### Step 2: Run All Automated Tests (19/19 Passing)
```bash
# Executes UPIShield risk engine tests, FastAPI backend API tests, & E2E test suites:
python -m pytest
# or: python -m unittest discover -s tests -p "test_*.py" -v
```

### Step 3: Start FastAPI Backend
```bash
uvicorn backend.main:app --reload --port 8000
```
- API Docs (Swagger UI): `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/health`

### Step 4: Start Next.js Frontend
```bash
cd frontend
npm install
npm run dev
```
- Open your browser at: `http://localhost:3000`

*(Optional) The standalone Streamlit prototype remains runnable via `streamlit run app.py`.*

---

## 🧪 5. Synthetic Datasets & Reproducibility

- **Database**: SQLite file at `data/sih_cybercrime.db`.
- **Synthetic Transactions**: `data/synthetic_transactions.csv`.
- **ML Training Pipeline**: `python backend/ml/train_cashout_model.py` generates model weights trained on synthetic spatial-temporal withdrawal histories.
- **Seeding Script**: `python backend/synthetic_data.py` auto-populates reproducible test cases on startup.

---

## 📂 6. Repository Layout

```
UPIShield/
├── backend/                       # FastAPI Backend Service
│   ├── main.py                    # FastAPI entrypoint & CORS
│   ├── models.py                  # Pydantic data contracts
│   ├── database.py                # SQLite connection & schema initialization
│   ├── synthetic_data.py          # Synthetic NCRP complaints, cases, and mule data
│   ├── ml/
│   │   ├── cashout_predictor.py   # GradientBoosting cash-out predictor
│   │   └── train_cashout_model.py # Reproducible model trainer
│   ├── routers/                   # API routers (dashboard, cases, complaints, locations, alerts)
│   └── services/                  # Business logic (risk_service, graph_service, prediction_service, alert_service)
│
├── frontend/                      # Next.js 14 Web Application
│   ├── src/app/                   # App Router pages (Dashboard, Cases, Cashout, Alerts)
│   ├── src/components/            # UI components (Navbar, RiskScoreGauge, NetworkGraphVisualizer, LeafletMap, AlertModal)
│   ├── src/lib/                   # API client (api.ts) and TypeScript interfaces (types.ts)
│   └── package.json               # Frontend dependencies (Next.js, Leaflet, Tailwind, Lucide)
│
├── src/                           # UPIShield Core Python Risk Engine
│   ├── risk_engine.py             # Dual-layer risk scoring & explainability
│   ├── behavior.py                # Statistical user baseline profiling
│   ├── config.py                  # Dynamic weighting & rule parameters
│   └── data_generator.py          # Synthetic UPI transaction generator
│
├── tests/
│   ├── test_risk_engine.py        # Core risk engine unit tests
│   ├── test_backend_api.py        # FastAPI endpoints unit tests
│   └── test_live_e2e.py           # End-to-end operational pipeline test
│
├── app.py                         # Standalone Streamlit prototype
└── README.md                      # Documentation & review guide
```

