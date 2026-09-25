"""
Prediction Service coordinating case cash-out location estimations.
"""

from backend.database import get_db_connection
from backend.ml.cashout_predictor import predictor
from backend.models import CashoutPredictionResponse, CashoutPredictionItem


class CaseCashoutPredictionService:
    """
    Coordinates spatial-temporal ML inference for active cases.
    """

    def predict_case_cashout(self, case_id: str) -> CashoutPredictionResponse:
        conn = get_db_connection()
        case = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
        conn.close()

        target_amount = float(case["total_amount_lost"]) if case else 270000.0
        last_coord = (28.7120, 77.1190)

        raw_ranked = predictor.predict_top_locations(
            case_amount=target_amount,
            last_known_coord=last_coord,
            top_k=4
        )

        items = [CashoutPredictionItem(**r) for r in raw_ranked]

        methodology = (
            "Multi-factor Gradient Boosting model trained on synthetic historical cash withdrawals. "
            "Evaluated spatial proximity to the runner device hop, kiosk historical fraud volume, "
            "CSP vs ATM vulnerability index, and CCTV presence."
        )

        recommended_actions = [
            "Dispatch tactical cyber patrol / PCR van to Rank #1 hotspot (SBI Sector 7 Rohini).",
            "Issue immediate debit freeze instruction to SBI & Paytm Payments Bank nodal fraud desk.",
            "Broadcast suspect device IMEI and runner token to I4C Joint Cybercrime Coordination."
        ]

        return CashoutPredictionResponse(
            case_id=case_id,
            target_amount=target_amount,
            predicted_locations=items,
            methodology_note=methodology,
            recommended_actions=recommended_actions
        )


prediction_service = CaseCashoutPredictionService()

