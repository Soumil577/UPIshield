"""
Alert Service for generating, storing, and retrieving LEA, Bank, and I4C Intelligence Alerts.
"""

import json
from datetime import datetime
from typing import List
import uuid

from backend.database import get_db_connection
from backend.models import AlertCreateRequest, AlertResponse


class AlertDispatchService:
    """
    Simulates real-time intelligence alerts across Law Enforcement, Banks/FIs, and I4C.
    """

    def create_alert(self, req: AlertCreateRequest) -> AlertResponse:
        conn = get_db_connection()
        case = conn.execute("SELECT * FROM cases WHERE id = ?", (req.case_id,)).fetchone()
        
        placeholders = ",".join(["?"] * len(req.location_ids)) if req.location_ids else "''"
        locations_rows = conn.execute(
            f"SELECT id, name, type, bank, address, latitude, longitude FROM locations WHERE id IN ({placeholders})",
            req.location_ids
        ).fetchall() if req.location_ids else []

        loc_details = [dict(r) for r in locations_rows]

        alert_id = f"ALT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        case_title = case["title"] if case else "Cybercrime Incident"
        dispatched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action_code = "ACT-DEBIT-FREEZE-PATROL-DEPLOY"
        status = "DISPATCHED_ACTIVE"

        loc_names = [l["name"] for l in loc_details]
        summary = (
            f"CRITICAL TACTICAL ALERT: Multi-agency interception alert dispatched to {', '.join(req.target_agencies)}. "
            f"Target hotspots: {', '.join(loc_names[:2])}. Immediate debit freeze and police patrol requested. "
            f"Notes: {req.custom_notes}"
        )

        conn.execute("""
        INSERT INTO alerts (id, case_id, case_title, priority, target_agencies, predicted_locations, dispatched_at, status, action_code, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert_id,
            req.case_id,
            case_title,
            req.priority,
            json.dumps(req.target_agencies),
            json.dumps(loc_details),
            dispatched_at,
            status,
            action_code,
            summary
        ))
        conn.commit()
        conn.close()

        return AlertResponse(
            id=alert_id,
            case_id=req.case_id,
            case_title=case_title,
            priority=req.priority,
            target_agencies=req.target_agencies,
            predicted_locations=loc_details,
            dispatched_at=dispatched_at,
            status=status,
            action_code=action_code,
            summary=summary
        )

    def get_all_alerts(self) -> List[AlertResponse]:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM alerts ORDER BY dispatched_at DESC").fetchall()
        conn.close()

        alerts = []
        for r in rows:
            alerts.append(AlertResponse(
                id=r["id"],
                case_id=r["case_id"],
                case_title=r["case_title"],
                priority=r["priority"],
                target_agencies=json.loads(r["target_agencies"]),
                predicted_locations=json.loads(r["predicted_locations"]),
                dispatched_at=r["dispatched_at"],
                status=r["status"],
                action_code=r["action_code"],
                summary=r["summary"]
            ))
        return alerts


alert_service = AlertDispatchService()

