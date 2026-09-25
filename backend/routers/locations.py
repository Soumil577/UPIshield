"""
Physical Cash-Out Locations & ATM/CSP Hotspots API Router.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from backend.database import get_db_connection
from backend.models import CashoutLocation

router = APIRouter(prefix="/api/locations", tags=["Locations"])


@router.get("", response_model=List[CashoutLocation])
def list_locations(city: Optional[str] = None):
    conn = get_db_connection()
    if city:
        rows = conn.execute("SELECT * FROM locations WHERE city LIKE ? ORDER BY historical_fraud_count DESC", (f"%{city}%",)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM locations ORDER BY historical_fraud_count DESC").fetchall()
    conn.close()

    return [
        CashoutLocation(
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
        )
        for r in rows
    ]


@router.get("/{location_id}", response_model=CashoutLocation)
def get_location_by_id(location_id: str):
    conn = get_db_connection()
    r = conn.execute("SELECT * FROM locations WHERE id = ?", (location_id,)).fetchone()
    conn.close()

    if not r:
        raise HTTPException(status_code=404, detail=f"Location {location_id} not found")

    return CashoutLocation(
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
    )
