"""
Intelligence Alerts Router for SIH26184.
Provides GET and POST endpoints for multi-agency rapid dispatch alerts.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from backend.models import AlertCreateRequest, AlertResponse
from backend.services.alert_service import alert_service

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse])
def list_alerts():
    return alert_service.get_all_alerts()


@router.post("", response_model=AlertResponse)
def dispatch_alert(req: AlertCreateRequest):
    try:
        return alert_service.create_alert(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to dispatch alert: {str(e)}")
