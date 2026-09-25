"""
Risk Engine for UPIShield.
Combines General Transaction Risk Scoring with Personalized Behavioral Anomaly Detection
to compute an interpretable combined risk score (0-100) and actionable decision (ALLOW/VERIFY/BLOCK).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

from src.config import (
    DecisionThresholds,
    DEFAULT_THRESHOLD_ALLOW,
    DEFAULT_THRESHOLD_VERIFY,
    GENERAL_RISK_RULES,
    WEIGHTS_BY_HISTORY
)
from src.behavior import (
    UserBehaviorProfile,
    build_user_profile,
    score_behavioral_anomaly,
    extract_hour_from_time_or_ts
)


@dataclass
class RiskEvaluationResult:
    transaction_id: str
    user_id: str
    amount: float
    final_score: float
    decision: str  # ALLOW, VERIFY, BLOCK
    history_status: str  # NO_HISTORY, LIMITED_HISTORY, SUFFICIENT_HISTORY
    weights_applied: Dict[str, float]
    general_score: float
    general_reasons: List[str]
    behavior_score: float
    behavior_reasons: List[str]
    human_readable_summary: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    ml_anomaly_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "final_score": round(self.final_score, 1),
            "decision": self.decision,
            "history_status": self.history_status,
            "weights_applied": self.weights_applied,
            "general_score": round(self.general_score, 1),
            "general_reasons": self.general_reasons,
            "behavior_score": round(self.behavior_score, 1),
            "behavior_reasons": self.behavior_reasons,
            "human_readable_summary": self.human_readable_summary,
            "ml_anomaly_score": self.ml_anomaly_score
        }


def calculate_general_risk(tx: Dict[str, Any]) -> Tuple[float, List[str]]:
    """
    Computes a transparent, weighted general risk score (0-100) based purely on
    transaction attributes, without requiring prior user history.
    """
    raw_score = 0.0
    reasons: List[str] = []

    amount = float(tx.get("amount", 0.0))
    device_new = bool(tx.get("device_new", False) or tx.get("device_new") == 1)
    beneficiary_new = bool(tx.get("beneficiary_new", False) or tx.get("beneficiary_new") == 1)
    hour = extract_hour_from_time_or_ts(tx)
    freq = float(tx.get("transaction_frequency", 1.0))
    location = str(tx.get("location", "")).lower()

    # 1. Absolute Amount Thresholds
    if amount >= GENERAL_RISK_RULES["amount_very_high"]["threshold"]:
        raw_score += GENERAL_RISK_RULES["amount_very_high"]["points"]
        reasons.append(f"General Risk: Very high transaction value (₹{amount:,.2f} >= ₹50,000)")
    elif amount >= GENERAL_RISK_RULES["amount_high"]["threshold"]:
        raw_score += GENERAL_RISK_RULES["amount_high"]["points"]
        reasons.append(f"General Risk: High transaction value (₹{amount:,.2f} >= ₹25,000)")
    elif amount >= GENERAL_RISK_RULES["amount_moderate"]["threshold"]:
        raw_score += GENERAL_RISK_RULES["amount_moderate"]["points"]
        reasons.append(f"General Risk: Elevated transaction value (₹{amount:,.2f} >= ₹10,000)")

    # 2. Device & Beneficiary Flags
    if device_new:
        raw_score += GENERAL_RISK_RULES["new_device"]["points"]
        reasons.append("General Risk: New / unregistered device detected for this transaction")

    if beneficiary_new:
        raw_score += GENERAL_RISK_RULES["new_beneficiary"]["points"]
        reasons.append("General Risk: Payment to a first-time beneficiary")

    # 3. High-Risk Time (Midnight / Early Morning 01:00 AM - 05:00 AM)
    odd_start = GENERAL_RISK_RULES["unusual_hour"]["start_hour"]
    odd_end = GENERAL_RISK_RULES["unusual_hour"]["end_hour"]
    if odd_start <= hour <= odd_end:
        raw_score += GENERAL_RISK_RULES["unusual_hour"]["points"]
        reasons.append(f"General Risk: High-risk time window ({hour:02d}:00 is between {odd_start:02d}:00 and {odd_end:02d}:00 AM)")

    # 4. Rapid Frequency / Velocity
    if freq >= GENERAL_RISK_RULES["high_frequency"]["threshold"]:
        raw_score += GENERAL_RISK_RULES["high_frequency"]["points"]
        reasons.append(f"General Risk: High transaction velocity ({freq:.1f} tx/hr)")

    # 5. Suspicious / Non-standard Location
    high_risk_loc_keywords = ["unknown", "foreign", "unverified", "vpn", "proxy"]
    if any(k in location for k in high_risk_loc_keywords):
        raw_score += GENERAL_RISK_RULES["unusual_location"]["points"]
        reasons.append(f"General Risk: High-risk or flagged location context ({tx.get('location')})")

    # If no risk factors triggered
    if not reasons:
        reasons.append("General Risk: Transaction characteristics conform to safe baselines")

    general_score = min(100.0, max(0.0, round(raw_score, 1)))
    return general_score, reasons


def generate_human_readable_explanation(
    decision: str,
    final_score: float,
    cohort: str,
    general_reasons: List[str],
    behavior_reasons: List[str]
) -> str:
    """
    Generates a concise, executive summary explaining the rationale behind the decision.
    """
    score_str = f"{final_score:.0f}/100"
    
    if decision == "ALLOW":
        if cohort == "NO_HISTORY":
            return (
                f"Transaction approved with Low Risk ({score_str}). "
                f"Although this user has no transaction history, the transaction amount and operational parameters "
                f"fall within standard, low-risk limits."
            )
        else:
            return (
                f"Transaction approved with Low Risk ({score_str}). "
                f"Transaction aligns with user's verified historical baseline (familiar device, recipient, and amounts)."
            )

    elif decision == "VERIFY":
        active_concerns = [r.replace("Personalized Anomaly: ", "").replace("General Risk: ", "") 
                           for r in (general_reasons + behavior_reasons) 
                           if "conform to safe" not in r and "relying on General" not in r]
        concerns_text = "; ".join(active_concerns[:2]) if active_concerns else "Moderate risk detected"
        return (
            f"Step-Up Verification required (Risk Score {score_str}). "
            f"Key triggers: {concerns_text}. Recommended action: Prompt for biometric confirmation or SMS OTP."
        )

    else:  # BLOCK
        active_concerns = [r.replace("Personalized Anomaly: ", "").replace("General Risk: ", "") 
                           for r in (general_reasons + behavior_reasons) 
                           if "conform to safe" not in r and "relying on General" not in r]
        concerns_text = "; ".join(active_concerns[:3]) if active_concerns else "Critical risk threshold breached"
        if cohort == "NO_HISTORY":
            return (
                f"Transaction BLOCKED due to Severe General Risk ({score_str}). "
                f"Even with zero user history, multi-factor risk rules triggered: {concerns_text}. "
                f"Protected against high-value first-touch fraud."
            )
        else:
            return (
                f"Transaction BLOCKED due to Severe Behavioral Deviation & Threat Signals ({score_str}). "
                f"Significant departure from historical user norms: {concerns_text}."
            )


class RiskEngine:
    """
    Unified UPIShield Risk Engine combining general and behavioral layers.
    """

    def __init__(self, thresholds: Optional[DecisionThresholds] = None):
        self.thresholds = thresholds or DecisionThresholds(
            allow_max=DEFAULT_THRESHOLD_ALLOW,
            verify_max=DEFAULT_THRESHOLD_VERIFY
        )

    def evaluate_transaction(
        self,
        tx: Dict[str, Any],
        user_history_df: Optional[pd.DataFrame] = None,
        custom_weights: Optional[Dict[str, float]] = None,
        ml_model: Optional[Any] = None
    ) -> RiskEvaluationResult:
        """
        Main entry point: Evaluates an incoming transaction against general rules
        and personalized behavior.
        """
        user_id = str(tx.get("user_id", "anonymous_user"))
        amount = float(tx.get("amount", 0.0))
        tx_id = str(tx.get("transaction_id", "TXN_SIM"))

        # 1. Build or retrieve user profile
        profile = build_user_profile(user_id=user_id, history_df=user_history_df)

        # 2. General Risk Layer (History-independent)
        general_score, general_reasons = calculate_general_risk(tx)

        # 3. Behavioral Anomaly Layer (History-dependent)
        behavior_score, behavior_reasons, metrics = score_behavioral_anomaly(tx, profile)

        # 4. Determine Dynamic Weighting
        if custom_weights:
            w_gen = custom_weights.get("general", 0.5)
            w_beh = custom_weights.get("behavior", 0.5)
        else:
            weight_cfg = WEIGHTS_BY_HISTORY.get(profile.cohort, WEIGHTS_BY_HISTORY["NO_HISTORY"])
            w_gen = weight_cfg["general"]
            w_beh = weight_cfg["behavior"]

        # 5. Combined Score Calculation (Clamped 0 - 100)
        raw_final = (general_score * w_gen) + (behavior_score * w_beh)
        final_score = min(100.0, max(0.0, round(raw_final, 1)))

        # 6. Classify Decision
        decision = self.thresholds.classify(final_score)

        # 7. Optional ML Anomaly Evaluation
        ml_anomaly_score = None
        if ml_model is not None:
            try:
                ml_anomaly_score = ml_model.predict_anomaly_score(tx)
            except Exception:
                pass

        # 8. Human-Readable Explanation
        explanation = generate_human_readable_explanation(
            decision=decision,
            final_score=final_score,
            cohort=profile.cohort,
            general_reasons=general_reasons,
            behavior_reasons=behavior_reasons
        )

        return RiskEvaluationResult(
            transaction_id=tx_id,
            user_id=user_id,
            amount=amount,
            final_score=final_score,
            decision=decision,
            history_status=profile.cohort,
            weights_applied={"general": round(w_gen, 2), "behavior": round(w_beh, 2)},
            general_score=general_score,
            general_reasons=general_reasons,
            behavior_score=behavior_score,
            behavior_reasons=behavior_reasons,
            human_readable_summary=explanation,
            metrics=metrics,
            ml_anomaly_score=ml_anomaly_score
        )

