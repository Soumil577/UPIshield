"""
Configuration and Thresholds for UPIShield.
Provides central settings for decision rules, risk point allocations,
and dynamic weighting policies.
"""

from dataclasses import dataclass
from typing import Dict, Any


# ==========================================
# DECISION THRESHOLDS (Configurable in 1 place)
# ==========================================
# 0 - 39  -> ALLOW
# 40 - 69 -> VERIFY
# 70 - 100 -> BLOCK
DEFAULT_THRESHOLD_ALLOW: int = 39
DEFAULT_THRESHOLD_VERIFY: int = 69


@dataclass
class DecisionThresholds:
    allow_max: int = DEFAULT_THRESHOLD_ALLOW
    verify_max: int = DEFAULT_THRESHOLD_VERIFY

    def classify(self, score: float) -> str:
        """Classifies a 0-100 risk score into ALLOW, VERIFY, or BLOCK."""
        clamped_score = max(0.0, min(100.0, float(score)))
        if clamped_score <= self.allow_max:
            return "ALLOW"
        elif clamped_score <= self.verify_max:
            return "VERIFY"
        else:
            return "BLOCK"


# ==========================================
# DYNAMIC WEIGHTING POLICY
# ==========================================
# Controls how much weight General Risk vs Behavioral Risk receives
# based on transaction count in user history.
HISTORY_SUFFICIENT_MIN_TX: int = 5  # >= 5 tx qualifies as SUFFICIENT_HISTORY

WEIGHTS_BY_HISTORY = {
    "NO_HISTORY": {
        "general": 1.0,
        "behavior": 0.0,
        "label": "No History (100% General Risk)"
    },
    "LIMITED_HISTORY": {
        "general": 0.70,
        "behavior": 0.30,
        "label": "Limited History (70% General / 30% Behavioral)"
    },
    "SUFFICIENT_HISTORY": {
        "general": 0.40,
        "behavior": 0.60,
        "label": "Sufficient History (40% General / 60% Behavioral)"
    }
}


# ==========================================
# GENERAL RISK ENGINE WEIGHTS & RULES
# ==========================================
GENERAL_RISK_RULES = {
    # Absolute transaction amount risk
    "amount_very_high": {"threshold": 50000, "points": 35, "reason": "Extremely high transaction amount (>= ₹50,000)"},
    "amount_high": {"threshold": 25000, "points": 25, "reason": "High transaction amount (>= ₹25,000)"},
    "amount_moderate": {"threshold": 10000, "points": 12, "reason": "Elevated transaction amount (>= ₹10,000)"},
    
    # Device and beneficiary risks
    "new_device": {"points": 25, "reason": "Transaction initiated from an unregistered/new device"},
    "new_beneficiary": {"points": 20, "reason": "Payment to a newly encountered beneficiary"},
    
    # Temporal risk (e.g. 01:00 AM - 05:00 AM)
    "unusual_hour": {"start_hour": 1, "end_hour": 5, "points": 15, "reason": "Transaction at high-risk odd hours (01:00 AM - 05:00 AM)"},
    
    # Frequency / Velocity risk
    "high_frequency": {"threshold": 5, "points": 15, "reason": "Rapid succession of transactions (High frequency >= 5 tx/hr)"},
    
    # High-risk location
    "unusual_location": {"points": 15, "reason": "Transaction from an unusual or unverified location"}
}


# ==========================================
# PERSONALIZED BEHAVIORAL PROFILE RULES
# ==========================================
BEHAVIOR_RISK_RULES = {
    # Amount anomaly relative to personal historical average / median
    "amount_massive_spike": {"multiplier": 6.0, "points": 45, "reason": "Amount is >6x higher than personal average"},
    "amount_large_spike": {"multiplier": 3.5, "points": 30, "reason": "Amount is >3.5x higher than personal average"},
    "amount_moderate_spike": {"multiplier": 2.0, "points": 15, "reason": "Amount is >2x higher than personal average"},
    "amount_exceeds_max": {"points": 15, "reason": "Amount exceeds historical personal maximum"},
    
    # Unfamiliar attributes for established user
    "unseen_device": {"points": 25, "reason": "Device was never previously used by this user"},
    "unseen_beneficiary": {"points": 20, "reason": "Beneficiary is not in user's established beneficiary circle"},
    "unusual_user_hour": {"points": 15, "reason": "Transaction time deviates from user's active historical hours"},
    "unseen_location": {"points": 15, "reason": "Transaction originates from a location never visited in user history"},
    "frequency_surge": {"multiplier": 2.5, "points": 15, "reason": "Transaction frequency is >2.5x higher than user's normal pace"}
}

