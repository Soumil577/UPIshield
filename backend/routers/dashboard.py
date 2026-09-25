"""
Dashboard Statistics & Hotspot API Endpoint.
"""

from fastapi import APIRouter
from backend.database import get_db_connection
from backend.models import DashboardStats, Complaint, CashoutLocation
from backend.services.alert_service import alert_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard_summary():
    conn = get_db_connection()
    
    total_complaints = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    total_cases = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
    amount_at_risk = conn.execute("SELECT SUM(total_amount_lost) FROM cases").fetchone()[0] or 0.0
    high_risk_cases_count = conn.execute("SELECT COUNT(*) FROM cases WHERE status = 'IMMINENT_CASHOUT_FLAGGED'").fetchone()[0]

    c_rows = conn.execute("SELECT * FROM complaints ORDER BY reported_time DESC LIMIT 5").fetchall()
    recent_complaints = [Complaint(**dict(r)) for r in c_rows]

    loc_rows = conn.execute("SELECT * FROM locations ORDER BY historical_fraud_count DESC").fetchall()
    locations = [CashoutLocation(
        id=r["id"],
        name=r["name"],
        type=r["type"],
        bank=r["bank"],
        address=r["address"],
        city=r["city"],
        latitude=float(r["latitude"]),
        longitude=float(r["longitude"]),
        cctv_available=bool(r["cctv_available"]),
        historical_fraud_count=int(r["historical_fraud_count"])
    ) for r in loc_rows]

    conn.close()

    recent_alerts = alert_service.get_all_alerts()[:3]
    active_hotspots_count = len([l for l in locations if l.historical_fraud_count >= 10])

    return DashboardStats(
        total_complaints=total_complaints,
        total_cases=total_cases,
        amount_at_risk=amount_at_risk,
        high_risk_cases_count=high_risk_cases_count,
        active_hotspots_count=active_hotspots_count,
        recent_complaints=recent_complaints,
        recent_alerts=recent_alerts,
        hotspot_locations=locations
    )

