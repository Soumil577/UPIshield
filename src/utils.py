"""
Utility functions and preset demo scenarios for UPIShield.
"""

from typing import Dict, Any, List


DEMO_SCENARIOS = {
    "scenario_1": {
        "title": "Scenario 1: Normal Transaction (Existing User)",
        "subtitle": "Aarav Sharma pays ₹800 to regular grocery merchant during daytime on known phone.",
        "expected_decision": "ALLOW",
        "description": "Standard routine transaction with low risk score across all parameters.",
        "payload": {
            "transaction_id": "TXN_DEMO_001",
            "user_id": "user_std_01",
            "amount": 800.0,
            "beneficiary_id": "BENEF_SUPERMART",
            "beneficiary_new": 0,
            "device_id": "DEV_AARAV_PHONE",
            "device_new": 0,
            "location": "Mumbai",
            "hour": 14,
            "timestamp": "2026-08-25 14:15:00",
            "transaction_frequency": 2.0
        }
    },
    "scenario_2": {
        "title": "Scenario 2: Behavioral Anomaly (Existing User)",
        "subtitle": "Aarav Sharma (normal spending ₹200-₹1,800) suddenly pays ₹25,000 at 3:30 AM on new device.",
        "expected_decision": "BLOCK",
        "description": "Deviates heavily from established user baseline (amount spike, new device, odd midnight hour).",
        "payload": {
            "transaction_id": "TXN_DEMO_002",
            "user_id": "user_std_01",
            "amount": 25000.0,
            "beneficiary_id": "BENEF_UNKNOWN_CRYPTO",
            "beneficiary_new": 1,
            "device_id": "DEV_UNKNOWN_DEVICE_99",
            "device_new": 1,
            "location": "Kolkata",
            "hour": 3,
            "timestamp": "2026-08-25 03:30:00",
            "transaction_frequency": 5.5
        }
    },
    "scenario_3": {
        "title": "Scenario 3: High-Risk Transaction (Brand New User)",
        "subtitle": "Sneha Gupta (0 prior history) makes first-ever payment of ₹35,000 at 2:45 AM to new recipient.",
        "expected_decision": "BLOCK",
        "description": "Evaluated purely by General Risk rules with 100% weight, demonstrating robust zero-history protection.",
        "payload": {
            "transaction_id": "TXN_DEMO_003",
            "user_id": "user_new_01",
            "amount": 35000.0,
            "beneficiary_id": "BENEF_UNKNOWN_MERCHANT",
            "beneficiary_new": 1,
            "device_id": "DEV_SNEHA_NEW_DEVICE",
            "device_new": 1,
            "location": "Delhi",
            "hour": 2,
            "timestamp": "2026-08-25 02:45:00",
            "transaction_frequency": 1.0
        }
    }
}


def format_inr(amount: float) -> str:
    """Formats a float as Indian Rupee string."""
    try:
        return f"₹{amount:,.2f}"
    except Exception:
        return f"₹{amount}"


def get_decision_badge_html(decision: str) -> str:
    """Returns styled HTML badge for ALLOW, VERIFY, or BLOCK."""
    color_map = {
        "ALLOW": {"bg": "#E6F4EA", "text": "#137333", "border": "#34A853", "icon": "✓"},
        "VERIFY": {"bg": "#FEF7E0", "text": "#B06000", "border": "#FBBC04", "icon": "⚠️"},
        "BLOCK": {"bg": "#FCE8E6", "text": "#C5221F", "border": "#EA4335", "icon": "⛔"}
    }
    style = color_map.get(decision, {"bg": "#F1F3F4", "text": "#3C4043", "border": "#9AA0A6", "icon": "ℹ"})
    
    return f"""
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: {style['bg']};
        color: {style['text']};
        border: 2px solid {style['border']};
        padding: 6px 18px;
        border-radius: 24px;
        font-weight: 700;
        font-size: 1.25rem;
        letter-spacing: 0.5px;
    ">
        <span>{style['icon']}</span>
        <span>{decision}</span>
    </div>
    """

