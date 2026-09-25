"""
Case Investigation & Predictive Intelligence Endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from backend.database import get_db_connection
from backend.models import CaseDetail, Complaint, EntityNetworkGraph, CashoutPredictionResponse
from backend.services.risk_service import risk_service
from backend.services.graph_service import graph_service
from backend.services.prediction_service import prediction_service

router = APIRouter(prefix="/api/cases", tags=["Cases"])


@router.get("", response_model=List[CaseDetail])
def list_cases():
    conn = get_db_connection()
    case_rows = conn.execute("SELECT * FROM cases ORDER BY created_at DESC").fetchall()
    
    results = []
    for c in case_rows:
        complaint_rows = conn.execute("SELECT * FROM complaints WHERE case_id = ?", (c["id"],)).fetchall()
        complaints = [Complaint(**dict(r)) for r in complaint_rows]
        results.append(CaseDetail(
            id=c["id"],
            title=c["title"],
            description=c["description"],
            category=c["category"],
            total_amount_lost=float(c["total_amount_lost"]),
            created_at=c["created_at"],
            status=c["status"],
            complaints=complaints,
            primary_mule_account=c["primary_mule_account"],
            primary_mule_upi=c["primary_mule_upi"]
        ))
    conn.close()
    return results


@router.get("/{case_id}", response_model=CaseDetail)
def get_case_detail(case_id: str):
    conn = get_db_connection()
    c = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    if not c:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    complaint_rows = conn.execute("SELECT * FROM complaints WHERE case_id = ?", (case_id,)).fetchall()
    complaints = [Complaint(**dict(r)) for r in complaint_rows]
    conn.close()

    risk_eval = risk_service.evaluate_case_financial_risk(case_id)

    return CaseDetail(
        id=c["id"],
        title=c["title"],
        description=c["description"],
        category=c["category"],
        total_amount_lost=float(c["total_amount_lost"]),
        created_at=c["created_at"],
        status=c["status"],
        complaints=complaints,
        primary_mule_account=c["primary_mule_account"],
        primary_mule_upi=c["primary_mule_upi"],
        risk_evaluation=risk_eval
    )


@router.get("/{case_id}/network", response_model=EntityNetworkGraph)
def get_case_network_graph(case_id: str):
    return graph_service.build_case_network(case_id)


@router.post("/{case_id}/predict-cashout", response_model=CashoutPredictionResponse)
def predict_case_cashout_locations(case_id: str):
    return prediction_service.predict_case_cashout(case_id)

