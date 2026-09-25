"""
Personalized Behavioral Profiler for UPIShield.
Extracts user-specific behavioral baselines from transaction history and detects anomalies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Set, Any, Optional, Tuple
import numpy as np
import pandas as pd

from src.config import BEHAVIOR_RISK_RULES, HISTORY_SUFFICIENT_MIN_TX


@dataclass
class UserBehaviorProfile:
    user_id: str
    tx_count: int
    cohort: str  # NO_HISTORY, LIMITED_HISTORY, SUFFICIENT_HISTORY
    avg_amount: float = 0.0
    median_amount: float = 0.0
    std_amount: float = 0.0
    min_amount: float = 0.0
    max_amount: float = 0.0
    p90_amount: float = 0.0
    known_devices: Set[str] = field(default_factory=set)
    known_beneficiaries: Set[str] = field(default_factory=set)
    known_locations: Set[str] = field(default_factory=set)
    active_hours: Set[int] = field(default_factory=set)
    min_active_hour: int = 0
    max_active_hour: int = 23
    avg_frequency: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Returns a serializable dictionary representation of the profile."""
        return {
            "user_id": self.user_id,
            "tx_count": self.tx_count,
            "cohort": self.cohort,
            "avg_amount": round(self.avg_amount, 2),
            "median_amount": round(self.median_amount, 2),
            "std_amount": round(self.std_amount, 2),
            "amount_range": f"₹{self.min_amount:,.2f} - ₹{self.max_amount:,.2f}",
            "p90_amount": round(self.p90_amount, 2),
            "known_devices": sorted(list(self.known_devices)),
            "known_beneficiaries": sorted(list(self.known_beneficiaries)),
            "known_locations": sorted(list(self.known_locations)),
            "active_hours_range": f"{self.min_active_hour:02d}:00 - {self.max_active_hour:02d}:00" if self.active_hours else "N/A",
            "avg_frequency": round(self.avg_frequency, 2)
        }


def build_user_profile(user_id: str, history_df: Optional[pd.DataFrame] = None) -> UserBehaviorProfile:
    """
    Computes statistical behavioral baselines for a specific user from historical records.
    """
    if history_df is None or history_df.empty or len(history_df) == 0:
        return UserBehaviorProfile(
            user_id=user_id,
            tx_count=0,
            cohort="NO_HISTORY"
        )
    
    # Filter normal (non-fraud) transactions for baseline learning if available
    baseline_df = history_df[history_df["fraud_label"] == 0] if "fraud_label" in history_df.columns else history_df
    if baseline_df.empty:
        baseline_df = history_df
        
    tx_count = len(baseline_df)
    
    if tx_count == 0:
        cohort = "NO_HISTORY"
    elif tx_count < HISTORY_SUFFICIENT_MIN_TX:
        cohort = "LIMITED_HISTORY"
    else:
        cohort = "SUFFICIENT_HISTORY"

    amounts = baseline_df["amount"].astype(float).values
    avg_amt = float(np.mean(amounts)) if tx_count > 0 else 0.0
    med_amt = float(np.median(amounts)) if tx_count > 0 else 0.0
    std_amt = float(np.std(amounts)) if tx_count > 1 else 0.0
    min_amt = float(np.min(amounts)) if tx_count > 0 else 0.0
    max_amt = float(np.max(amounts)) if tx_count > 0 else 0.0
    p90_amt = float(np.percentile(amounts, 90)) if tx_count > 0 else 0.0

    devices = set(baseline_df["device_id"].dropna().unique())
    beneficiaries = set(baseline_df["beneficiary_id"].dropna().unique())
    locations = set(baseline_df["location"].dropna().unique())
    
    # Extract hours from timestamps
    active_hours = set()
    if "timestamp" in baseline_df.columns:
        for ts in baseline_df["timestamp"]:
            try:
                dt = pd.to_datetime(ts)
                active_hours.add(dt.hour)
            except Exception:
                pass

    min_hour = min(active_hours) if active_hours else 0
    max_hour = max(active_hours) if active_hours else 23
    
    avg_freq = float(baseline_df["transaction_frequency"].mean()) if "transaction_frequency" in baseline_df.columns else 1.0

    return UserBehaviorProfile(
        user_id=user_id,
        tx_count=tx_count,
        cohort=cohort,
        avg_amount=avg_amt,
        median_amount=med_amt,
        std_amount=std_amt,
        min_amount=min_amt,
        max_amount=max_amt,
        p90_amount=p90_amt,
        known_devices=devices,
        known_beneficiaries=beneficiaries,
        known_locations=locations,
        active_hours=active_hours,
        min_active_hour=min_hour,
        max_active_hour=max_hour,
        avg_frequency=avg_freq
    )


def extract_hour_from_time_or_ts(tx: Dict[str, Any]) -> int:
    """Extracts integer hour (0-23) from timestamp string, time object, or explicit hour."""
    if "hour" in tx and tx["hour"] is not None:
        return int(tx["hour"])
    if "timestamp" in tx and tx["timestamp"]:
        try:
            dt = pd.to_datetime(tx["timestamp"])
            return dt.hour
        except Exception:
            pass
    return 12  # default midday fallback


def score_behavioral_anomaly(tx: Dict[str, Any], profile: UserBehaviorProfile) -> Tuple[float, List[str], Dict[str, Any]]:
    """
    Evaluates how much an incoming transaction deviates from the user's personal profile.
    Returns:
      - behavioral_risk_score (0 - 100)
      - reason_codes (List of human-readable explanations)
      - breakdown_metrics (Dict with calculated deviations)
    """
    reasons: List[str] = []
    metrics: Dict[str, Any] = {
        "cohort": profile.cohort,
        "tx_count": profile.tx_count,
        "amount_multiplier": 1.0,
        "device_known": True,
        "beneficiary_known": True,
        "hour_within_profile": True,
        "location_known": True
    }

    # If the user has NO HISTORY, behavioral scoring cannot establish baseline deviations
    if profile.cohort == "NO_HISTORY" or profile.tx_count == 0:
        return 0.0, ["No prior user transaction history available; relying on General Risk Engine."], metrics

    raw_score = 0.0
    amount = float(tx.get("amount", 0.0))
    device_id = str(tx.get("device_id", ""))
    beneficiary_id = str(tx.get("beneficiary_id", ""))
    location = str(tx.get("location", ""))
    hour = extract_hour_from_time_or_ts(tx)
    freq = float(tx.get("transaction_frequency", 1.0))

    # Baseline comparison value: use median or mean
    baseline_amt = profile.median_amount if profile.median_amount > 0 else (profile.avg_amount if profile.avg_amount > 0 else 1.0)
    amt_mult = amount / baseline_amt if baseline_amt > 0 else 1.0
    metrics["amount_multiplier"] = round(amt_mult, 2)

    # 1. Amount deviation checks
    if amt_mult >= BEHAVIOR_RISK_RULES["amount_massive_spike"]["multiplier"]:
        raw_score += BEHAVIOR_RISK_RULES["amount_massive_spike"]["points"]
        reasons.append(
            f"Personalized Anomaly: Transaction amount (₹{amount:,.2f}) is {amt_mult:.1f}x higher than typical baseline (₹{baseline_amt:,.2f})"
        )
    elif amt_mult >= BEHAVIOR_RISK_RULES["amount_large_spike"]["multiplier"]:
        raw_score += BEHAVIOR_RISK_RULES["amount_large_spike"]["points"]
        reasons.append(
            f"Personalized Anomaly: Transaction amount (₹{amount:,.2f}) is {amt_mult:.1f}x higher than typical baseline (₹{baseline_amt:,.2f})"
        )
    elif amt_mult >= BEHAVIOR_RISK_RULES["amount_moderate_spike"]["multiplier"]:
        raw_score += BEHAVIOR_RISK_RULES["amount_moderate_spike"]["points"]
        reasons.append(
            f"Personalized Anomaly: Transaction amount (₹{amount:,.2f}) is {amt_mult:.1f}x higher than personal median (₹{baseline_amt:,.2f})"
        )

    if profile.max_amount > 0 and amount > profile.max_amount * 1.5:
        raw_score += BEHAVIOR_RISK_RULES["amount_exceeds_max"]["points"]
        reasons.append(
            f"Personalized Anomaly: Amount exceeds previous highest recorded transaction (₹{profile.max_amount:,.2f}) by >50%"
        )

    # 2. Device familiarity check
    if profile.known_devices and device_id not in profile.known_devices:
        metrics["device_known"] = False
        raw_score += BEHAVIOR_RISK_RULES["unseen_device"]["points"]
        reasons.append(
            f"Personalized Anomaly: Unrecognized device ({device_id}). User normally transacts with: {', '.join(profile.known_devices)}"
        )

    # 3. Beneficiary familiarity check
    if profile.known_beneficiaries and beneficiary_id not in profile.known_beneficiaries:
        metrics["beneficiary_known"] = False
        raw_score += BEHAVIOR_RISK_RULES["unseen_beneficiary"]["points"]
        reasons.append(
            f"Personalized Anomaly: First-time transfer to beneficiary ({beneficiary_id}). Not in user's regular recipient circle."
        )

    # 4. Temporal deviation check
    if profile.active_hours:
        # Check if hour is completely outside user's active hours
        if hour not in profile.active_hours:
            metrics["hour_within_profile"] = False
            raw_score += BEHAVIOR_RISK_RULES["unusual_user_hour"]["points"]
            reasons.append(
                f"Personalized Anomaly: Transaction at {hour:02d}:00 is outside user's active window ({profile.min_active_hour:02d}:00 - {profile.max_active_hour:02d}:00)"
            )

    # 5. Location familiarity check
    if profile.known_locations and location and location not in profile.known_locations:
        metrics["location_known"] = False
        raw_score += BEHAVIOR_RISK_RULES["unseen_location"]["points"]
        reasons.append(
            f"Personalized Anomaly: Unfamiliar location ({location}). User usually operates from: {', '.join(profile.known_locations)}"
        )

    # 6. Frequency anomaly check
    if profile.avg_frequency > 0 and freq >= profile.avg_frequency * BEHAVIOR_RISK_RULES["frequency_surge"]["multiplier"]:
        raw_score += BEHAVIOR_RISK_RULES["frequency_surge"]["points"]
        reasons.append(
            f"Personalized Anomaly: Sudden velocity surge ({freq:.1f} tx/hr vs personal average of {profile.avg_frequency:.1f} tx/hr)"
        )

    # Clamp behavioral score between 0 and 100
    behavioral_score = min(100.0, max(0.0, round(raw_score, 1)))
    return behavioral_score, reasons, metrics

