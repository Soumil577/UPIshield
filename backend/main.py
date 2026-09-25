"""
FastAPI Backend Entrypoint for SIH26184 UPIShield Cybercrime Intelligence System.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_database
from backend.synthetic_data import seed_cybercrime_data
from backend.routers import dashboard, cases, complaints, locations, alerts

app = FastAPI(
    title="UPIShield — SIH26184 Cybercrime Intelligence API",
    description="Proactive Cybercrime Intelligence & ATM/CSP Cash-Out Prediction Prototype",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(dashboard.router)
app.include_router(cases.router)
app.include_router(complaints.router)
app.include_router(locations.router)
app.include_router(alerts.router)


@app.on_event("startup")
def startup_event():
    """Initializes database schema and populates synthetic data if not already seeded."""
    init_database()
    # Check if database has cases; if empty, seed synthetic dataset automatically
    from backend.database import get_db_connection
    conn = get_db_connection()
    case_count = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
    conn.close()

    if case_count == 0:
        seed_cybercrime_data()


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "ONLINE",
        "system": "UPIShield SIH26184 Intelligence Framework",
        "database": "SQLite (Synthetic Data)",
        "version": "1.0.0"
    }
