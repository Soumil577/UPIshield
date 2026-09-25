"""
Synthetic Data Generator for UPIShield.
Generates realistic UPI transactions across three user cohorts:
- Users with No History (0 tx)
- Users with Limited History (1-4 tx)
- Users with Sufficient History (15+ tx)
"""

import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np


# Data storage path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CSV_PATH = os.path.join(DATA_DIR, "synthetic_transactions.csv")


USER_ARCHETYPES = {
    "user_std_01": {
        "name": "Aarav Sharma (Standard Regular User)",
        "cohort": "SUFFICIENT_HISTORY",
        "tx_count": 35,
        "amount_range": (200.0, 1800.0),
        "amount_mean": 750.0,
        "amount_std": 280.0,
        "active_hours": (8, 22),
        "devices": ["DEV_AARAV_PHONE"],
        "beneficiaries": ["BENEF_SUPERMART", "BENEF_LANDLORD", "BENEF_CHAI_CORNER", "BENEF_COLLEAGUE_RAVI"],
        "locations": ["Mumbai", "Mumbai Suburban"],
        "avg_frequency": 2.1
    },
    "user_std_02": {
        "name": "Pooja Patel (College Student)",
        "cohort": "SUFFICIENT_HISTORY",
        "tx_count": 28,
        "amount_range": (30.0, 650.0),
        "amount_mean": 240.0,
        "amount_std": 110.0,
        "active_hours": (10, 23),
        "devices": ["DEV_POOJA_MOBILE"],
        "beneficiaries": ["BENEF_CANTEEN", "BENEF_XEROX", "BENEF_HOSTEL_MESS", "BENEF_METRO_CARD"],
        "locations": ["Bengaluru"],
        "avg_frequency": 3.4
    },
    "user_hni_01": {
        "name": "Vikram Malhotra (Business Owner / HNI)",
        "cohort": "SUFFICIENT_HISTORY",
        "tx_count": 40,
        "amount_range": (3000.0, 45000.0),
        "amount_mean": 16500.0,
        "amount_std": 7200.0,
        "active_hours": (9, 20),
        "devices": ["DEV_VIKRAM_IPHONE", "DEV_VIKRAM_MAC"],
        "beneficiaries": ["BENEF_VENDOR_STEEL", "BENEF_DISTRIBUTOR_A", "BENEF_LOGISTICS_EXP", "BENEF_HOTEL_LUXE"],
        "locations": ["Delhi", "Gurugram"],
        "avg_frequency": 4.0
    },
    "user_lim_01": {
        "name": "Rohan Verma (New Account - 2 tx)",
        "cohort": "LIMITED_HISTORY",
        "tx_count": 2,
        "amount_range": (300.0, 1200.0),
        "amount_mean": 750.0,
        "amount_std": 200.0,
        "active_hours": (11, 18),
        "devices": ["DEV_ROHAN_ANDROID"],
        "beneficiaries": ["BENEF_KIRANA_STORE", "BENEF_ELECTRICITY_BOARD"],
        "locations": ["Hyderabad"],
        "avg_frequency": 1.0
    },
    "user_new_01": {
        "name": "Sneha Gupta (Brand New User - 0 tx)",
        "cohort": "NO_HISTORY",
        "tx_count": 0,
        "amount_range": (0.0, 0.0),
        "amount_mean": 0.0,
        "amount_std": 0.0,
        "active_hours": (0, 24),
        "devices": [],
        "beneficiaries": [],
        "locations": [],
        "avg_frequency": 0.0
    }
}


def generate_synthetic_transactions(seed: int = 42, num_extra_normal: int = 40, num_extra_fraud: int = 15) -> pd.DataFrame:
    """
    Generates a synthetic DataFrame of transactions.
    Ensures clear separation of normal vs anomalous transactions with realistic UPI attributes.
    """
    random.seed(seed)
    np.random.seed(seed)
    
    records: List[Dict[str, Any]] = []
    base_time = datetime(2026, 8, 1, 9, 0, 0)
    tx_counter = 1000

    # 1. Generate Historical Transactions for Archetype Users
    for user_id, profile in USER_ARCHETYPES.items():
        count = profile["tx_count"]
        if count == 0:
            continue
            
        for i in range(count):
            tx_counter += 1
            # Progressive timestamps over 3 weeks
            tx_time = base_time + timedelta(
                days=random.randint(0, 20),
                hours=random.randint(profile["active_hours"][0], profile["active_hours"][1] - 1),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            # Amount sampled normally around user profile
            raw_amt = float(np.random.normal(profile["amount_mean"], profile["amount_std"]))
            min_a, max_a = profile["amount_range"]
            amount = round(max(min_a, min(raw_amt, max_a * 1.25)), 2)
            
            device = random.choice(profile["devices"])
            beneficiary = random.choice(profile["beneficiaries"])
            loc = random.choice(profile["locations"])
            freq = round(max(1.0, np.random.normal(profile["avg_frequency"], 0.6)), 1)
            
            records.append({
                "transaction_id": f"TXN{tx_counter}",
                "user_id": user_id,
                "amount": amount,
                "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                "beneficiary_id": beneficiary,
                "beneficiary_new": 0,
                "device_id": device,
                "device_new": 0,
                "location": loc,
                "transaction_frequency": freq,
                "fraud_label": 0
            })

    # 2. Add realistic fraud/anomalous samples in history for evaluation
    anomalous_scenarios = [
        # Massive amount deviation on standard user
        {
            "user_id": "user_std_01",
            "amount": 28000.0,
            "hour": 3,
            "device_id": "DEV_UNKNOWN_99",
            "beneficiary_id": "BENEF_UNKNOWN_MULE",
            "location": "Kolkata",
            "fraud_label": 1
        },
        # Sudden velocity surge & new device
        {
            "user_id": "user_std_02",
            "amount": 14000.0,
            "hour": 2,
            "device_id": "DEV_NEW_EMULATOR",
            "beneficiary_id": "BENEF_GAMING_PORTAL",
            "location": "Noida",
            "fraud_label": 1
        },
        # High value on new limited user
        {
            "user_id": "user_lim_01",
            "amount": 42000.0,
            "hour": 4,
            "device_id": "DEV_NEW_ROOTED_PHONE",
            "beneficiary_id": "BENEF_CRYPTO_SWAP",
            "location": "Surat",
            "fraud_label": 1
        }
    ]

    for sc in anomalous_scenarios:
        tx_counter += 1
        tx_time = base_time + timedelta(days=22, hours=sc["hour"], minutes=random.randint(5, 55))
        records.append({
            "transaction_id": f"TXN{tx_counter}",
            "user_id": sc["user_id"],
            "amount": sc["amount"],
            "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
            "beneficiary_id": sc["beneficiary_id"],
            "beneficiary_new": 1,
            "device_id": sc["device_id"],
            "device_new": 1,
            "location": sc["location"],
            "transaction_frequency": 6.5,
            "fraud_label": sc["fraud_label"]
        })

    df = pd.DataFrame(records)
    # Sort chronologically
    df["timestamp_dt"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp_dt").reset_index(drop=True)
    df = df.drop(columns=["timestamp_dt"])
    
    return df


def ensure_data_file_exists() -> str:
    """Ensures that the CSV data directory and file exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        df = generate_synthetic_transactions()
        df.to_csv(CSV_PATH, index=False)
    return CSV_PATH


def load_dataset() -> pd.DataFrame:
    """Loads the synthetic transaction dataset from CSV."""
    csv_file = ensure_data_file_exists()
    return pd.read_csv(csv_file)


def get_user_history(user_id: str, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Returns historical transactions for a given user (excluding injected labels)."""
    if df is None:
        df = load_dataset()
    user_tx = df[df["user_id"] == user_id].copy()
    return user_tx


if __name__ == "__main__":
    ensure_data_file_exists()
    df_loaded = load_dataset()
    print(f"[SUCCESS] Generated {len(df_loaded)} synthetic transactions across {df_loaded['user_id'].nunique()} users.")
    print(f"Saved to: {CSV_PATH}")
