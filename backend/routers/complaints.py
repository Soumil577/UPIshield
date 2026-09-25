"""
NCRP & 1930 Cybercrime Complaints API Router.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from backend.database import get_db_connection
from backend.models import Complaint

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])


@router.get("", response_model=List[Complaint])
def list_complaints(case_id: Optional[str] = None):
    conn = get_db_connection()
    if case_id:
        rows = conn.execute("SELECT * FROM complaints WHERE case_id = ? ORDER BY reported_time DESC", (case_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM complaints ORDER BY reported_time DESC").fetchall()
    conn.close()

    return [Complaint(**dict(r)) for r in rows]


@router.get("/{complaint_id}", response_model=Complaint)
def get_complaint_by_id(complaint_id: str):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")

    return Complaint(**dict(row))
