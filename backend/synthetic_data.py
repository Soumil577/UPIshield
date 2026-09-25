"""
SIH26184 Synthetic Cybercrime Intelligence Data Generator.
Populates SQLite with realistic NCRP/1930 complaints, convergent mule syndicate cases,
multi-hop transaction trails, Delhi-NCR ATM/CSP locations, and historical cashouts.
"""

import random
import json
from datetime import datetime, timedelta
from backend.database import get_db_connection, init_database


def seed_cybercrime_data(seed: int = 42):
    """Populates the database with deterministic synthetic data."""
    random.seed(seed)
    init_database()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing tables
    cursor.execute("DELETE FROM alerts")
    cursor.execute("DELETE FROM historical_cashouts")
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM complaints")
    cursor.execute("DELETE FROM cases")
    cursor.execute("DELETE FROM locations")

    # 1. Locations
    locations = [
        {
            "id": "LOC-ATM-101",
            "name": "SBI 24x7 E-Corner ATM (Sector 7 Rohini)",
            "type": "ATM",
            "bank": "State Bank of India",
            "address": "Pocket C, Sector 7, Rohini, North West Delhi",
            "city": "Delhi",
            "latitude": 28.7126,
            "longitude": 77.1197,
            "cctv_available": 1,
            "historical_fraud_count": 14
        },
        {
            "id": "LOC-CSP-102",
            "name": "Airtel Payments Bank CSP & Money Transfer (Laxmi Nagar)",
            "type": "CSP",
            "bank": "Airtel Payments Bank",
            "address": "Vikas Marg, Near Metro Pillar 38, Laxmi Nagar",
            "city": "Delhi",
            "latitude": 28.6304,
            "longitude": 77.2773,
            "cctv_available": 0,
            "historical_fraud_count": 22
        },
        {
            "id": "LOC-ATM-103",
            "name": "PNB High-Volume ATM (Karol Bagh)",
            "type": "ATM",
            "bank": "Punjab National Bank",
            "address": "Arya Samaj Road, Karol Bagh Commercial Area",
            "city": "Delhi",
            "latitude": 28.6517,
            "longitude": 77.1906,
            "cctv_available": 1,
            "historical_fraud_count": 9
        },
        {
            "id": "LOC-CSP-104",
            "name": "Fino Payments Bank BC Agent (Chandni Chowk)",
            "type": "CSP",
            "bank": "Fino Payments Bank",
            "address": "Kucha Mahajani, Chandni Chowk",
            "city": "Delhi",
            "latitude": 28.6562,
            "longitude": 77.2310,
            "cctv_available": 0,
            "historical_fraud_count": 18
        },
        {
            "id": "LOC-ATM-105",
            "name": "HDFC Bank ATM (Janakpuri District Centre)",
            "type": "ATM",
            "bank": "HDFC Bank",
            "address": "Community Centre, Janakpuri",
            "city": "Delhi",
            "latitude": 28.6290,
            "longitude": 77.0818,
            "cctv_available": 1,
            "historical_fraud_count": 6
        },
        {
            "id": "LOC-ATM-106",
            "name": "Canara Bank ATM (Connaught Place)",
            "type": "ATM",
            "bank": "Canara Bank",
            "address": "Outer Circle, Block M, Connaught Place",
            "city": "Delhi",
            "latitude": 28.6328,
            "longitude": 77.2197,
            "cctv_available": 1,
            "historical_fraud_count": 5
        },
        {
            "id": "LOC-CSP-107",
            "name": "PayNearby Micro-ATM Kiosk (Dwarka Mor)",
            "type": "CSP",
            "bank": "PayNearby / Yes Bank BC",
            "address": "Near Pillar 782, Dwarka Mor Metro Station",
            "city": "Delhi",
            "latitude": 28.6190,
            "longitude": 77.0330,
            "cctv_available": 0,
            "historical_fraud_count": 12
        },
        {
            "id": "LOC-ATM-108",
            "name": "ICICI Bank ATM (Noida Sector 18)",
            "type": "ATM",
            "bank": "ICICI Bank",
            "address": "Atta Market, Sector 18",
            "city": "Noida",
            "latitude": 28.5708,
            "longitude": 77.3261,
            "cctv_available": 1,
            "historical_fraud_count": 8
        }
    ]

    for loc in locations:
        cursor.execute("""
        INSERT INTO locations (id, name, type, bank, address, city, latitude, longitude, cctv_available, historical_fraud_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (loc["id"], loc["name"], loc["type"], loc["bank"], loc["address"], loc["city"], loc["latitude"], loc["longitude"], loc["cctv_available"], loc["historical_fraud_count"]))

    # 2. Cases
    cases = [
        {
            "id": "CASE-2026-4401",
            "title": "Operation ShadowMule: Multi-State UPI Siphon to Delhi-NCR Cashout Ring",
            "description": "High-priority syndicate where multiple victim complaints across Mumbai, Bengaluru and Pune converge on a coordinated mule network with rapid multi-hop layer splitting and imminent cash withdrawal.",
            "category": "Syndicate / Multi-Hop Mule Ring",
            "total_amount_lost": 270000.0,
            "created_at": "2026-09-24 14:20:00",
            "status": "IMMINENT_CASHOUT_FLAGGED",
            "primary_mule_account": "ACC-SBIN-994812",
            "primary_mule_upi": "fastpay.sharma@okaxis"
        },
        {
            "id": "CASE-2026-4402",
            "title": "Electricity Bill Threat Phishing Ring",
            "description": "Victims threatened with immediate power disconnection coerced into installing remote control APK.",
            "category": "Remote Access / APK Fraud",
            "total_amount_lost": 82000.0,
            "created_at": "2026-09-24 11:15:00",
            "status": "UNDER_INVESTIGATION",
            "primary_mule_account": "ACC-HDFC-331201",
            "primary_mule_upi": "quickbill.support@ybl"
        },
        {
            "id": "CASE-2026-4403",
            "title": "Fake Investment Crypto Arbitrage Portal",
            "description": "Ponzi platform promising 25% daily ROI diverting investor deposits to mule UPI IDs.",
            "category": "Investment / Ponzi Fraud",
            "total_amount_lost": 195000.0,
            "created_at": "2026-09-23 18:40:00",
            "status": "UNDER_INVESTIGATION",
            "primary_mule_account": "ACC-ICIC-884120",
            "primary_mule_upi": "growcap.trading@icici"
        }
    ]

    for c in cases:
        cursor.execute("""
        INSERT INTO cases (id, title, description, category, total_amount_lost, created_at, status, primary_mule_account, primary_mule_upi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (c["id"], c["title"], c["description"], c["category"], c["total_amount_lost"], c["created_at"], c["status"], c["primary_mule_account"], c["primary_mule_upi"]))

    # 3. Complaints
    complaints = [
        {
            "id": "NCRP-2026-98124",
            "case_id": "CASE-2026-4401",
            "victim_name": "Priya Sharma",
            "victim_phone": "+91-9820144512",
            "victim_upi": "priyasharma@okaxis",
            "victim_account": "ACC-HDFC-910245",
            "victim_bank": "HDFC Bank",
            "fraud_category": "Part-time Telegram Task Scam",
            "reported_amount": 65000.0,
            "incident_time": "2026-09-24 11:30:00",
            "reported_time": "2026-09-24 12:15:00",
            "status": "ACTIONABLE",
            "city": "Mumbai"
        },
        {
            "id": "NCRP-2026-98150",
            "case_id": "CASE-2026-4401",
            "victim_name": "Rajesh Verma",
            "victim_phone": "+91-9448102319",
            "victim_upi": "rajesh.verma@sbi",
            "victim_account": "ACC-SBIN-772109",
            "victim_bank": "State Bank of India",
            "fraud_category": "Impersonation / Digital Arrest",
            "reported_amount": 120000.0,
            "incident_time": "2026-09-24 12:45:00",
            "reported_time": "2026-09-24 13:20:00",
            "status": "ACTIONABLE",
            "city": "Bengaluru"
        },
        {
            "id": "NCRP-2026-98188",
            "case_id": "CASE-2026-4401",
            "victim_name": "Ankit Mehta",
            "victim_phone": "+91-9764512093",
            "victim_upi": "ankitmehta@icici",
            "victim_account": "ACC-ICIC-449102",
            "victim_bank": "ICICI Bank",
            "fraud_category": "UPI Collect Request / Fake Refund",
            "reported_amount": 85000.0,
            "incident_time": "2026-09-24 13:10:00",
            "reported_time": "2026-09-24 13:55:00",
            "status": "ACTIONABLE",
            "city": "Pune"
        },
        {
            "id": "NCRP-2026-98205",
            "case_id": "CASE-2026-4402",
            "victim_name": "Sunita Kulkarni",
            "victim_phone": "+91-9123456789",
            "victim_upi": "sunita.k@kotak",
            "victim_account": "ACC-KKBK-554412",
            "victim_bank": "Kotak Mahindra Bank",
            "fraud_category": "Electricity Bill Threat Phishing",
            "reported_amount": 82000.0,
            "incident_time": "2026-09-24 10:20:00",
            "reported_time": "2026-09-24 11:10:00",
            "status": "PROCESSING",
            "city": "Nagpur"
        },
        {
            "id": "NCRP-2026-98221",
            "case_id": "CASE-2026-4403",
            "victim_name": "Deepak Choudhary",
            "victim_phone": "+91-9871109923",
            "victim_upi": "deepak.c@paytm",
            "victim_account": "ACC-PYTM-110022",
            "victim_bank": "Paytm Payments Bank",
            "fraud_category": "Crypto Arbitrage Scheme",
            "reported_amount": 195000.0,
            "incident_time": "2026-09-23 16:30:00",
            "reported_time": "2026-09-23 18:15:00",
            "status": "PROCESSING",
            "city": "Jaipur"
        }
    ]

    for comp in complaints:
        cursor.execute("""
        INSERT INTO complaints (id, case_id, victim_name, victim_phone, victim_upi, victim_account, victim_bank, fraud_category, reported_amount, incident_time, reported_time, status, city)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (comp["id"], comp["case_id"], comp["victim_name"], comp["victim_phone"], comp["victim_upi"], comp["victim_account"], comp["victim_bank"], comp["fraud_category"], comp["reported_amount"], comp["incident_time"], comp["reported_time"], comp["status"], comp["city"]))

    # 4. Transactions
    transactions = [
        {
            "id": "TXN-HOP1-001",
            "case_id": "CASE-2026-4401",
            "sender_id": "priyasharma@okaxis",
            "sender_type": "victim",
            "receiver_id": "fastpay.sharma@okaxis",
            "receiver_type": "mule_l1",
            "amount": 65000.0,
            "timestamp": "2026-09-24 11:32:15",
            "device_id": "DEV-VICTIM-MUMBAI",
            "ip_address": "49.36.120.4",
            "location": "Mumbai",
            "layer_index": 1
        },
        {
            "id": "TXN-HOP1-002",
            "case_id": "CASE-2026-4401",
            "sender_id": "rajesh.verma@sbi",
            "sender_type": "victim",
            "receiver_id": "fastpay.sharma@okaxis",
            "receiver_type": "mule_l1",
            "amount": 120000.0,
            "timestamp": "2026-09-24 12:47:30",
            "device_id": "DEV-VICTIM-BLR",
            "ip_address": "122.172.88.91",
            "location": "Bengaluru",
            "layer_index": 1
        },
        {
            "id": "TXN-HOP1-003",
            "case_id": "CASE-2026-4401",
            "sender_id": "ankitmehta@icici",
            "sender_type": "victim",
            "receiver_id": "fastpay.sharma@okaxis",
            "receiver_type": "mule_l1",
            "amount": 85000.0,
            "timestamp": "2026-09-24 13:12:05",
            "device_id": "DEV-VICTIM-PUNE",
            "ip_address": "103.51.24.11",
            "location": "Pune",
            "layer_index": 1
        },
        {
            "id": "TXN-HOP2-004",
            "case_id": "CASE-2026-4401",
            "sender_id": "fastpay.sharma@okaxis",
            "sender_type": "mule_l1",
            "receiver_id": "kumar.settle@paytm",
            "receiver_type": "mule_l2",
            "amount": 140000.0,
            "timestamp": "2026-09-24 13:25:00",
            "device_id": "DEV-MULE-OP1",
            "ip_address": "103.212.45.18",
            "location": "Delhi-Rohini",
            "layer_index": 2
        },
        {
            "id": "TXN-HOP2-005",
            "case_id": "CASE-2026-4401",
            "sender_id": "fastpay.sharma@okaxis",
            "sender_type": "mule_l1",
            "receiver_id": "vikas.traders@airtel",
            "receiver_type": "mule_l2",
            "amount": 130000.0,
            "timestamp": "2026-09-24 13:30:10",
            "device_id": "DEV-MULE-OP1",
            "ip_address": "103.212.45.18",
            "location": "Delhi-LaxmiNagar",
            "layer_index": 2
        },
        {
            "id": "TXN-HOP3-006",
            "case_id": "CASE-2026-4401",
            "sender_id": "kumar.settle@paytm",
            "sender_type": "mule_l2",
            "receiver_id": "RUNNER-CARD-DELHI-01",
            "receiver_type": "runner_token",
            "amount": 90000.0,
            "timestamp": "2026-09-24 14:05:00",
            "device_id": "DEV-RUNNER-991",
            "ip_address": "103.212.45.18",
            "location": "Sector 7 Rohini",
            "layer_index": 3
        },
        {
            "id": "TXN-HOP3-007",
            "case_id": "CASE-2026-4401",
            "sender_id": "vikas.traders@airtel",
            "sender_type": "mule_l2",
            "receiver_id": "RUNNER-CSP-TOKEN-02",
            "receiver_type": "runner_token",
            "amount": 80000.0,
            "timestamp": "2026-09-24 14:10:00",
            "device_id": "DEV-RUNNER-992",
            "ip_address": "103.212.45.22",
            "location": "Laxmi Nagar Vikas Marg",
            "layer_index": 3
        }
    ]

    for tx in transactions:
        cursor.execute("""
        INSERT INTO transactions (id, case_id, sender_id, sender_type, receiver_id, receiver_type, amount, timestamp, device_id, ip_address, location, layer_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tx["id"], tx["case_id"], tx["sender_id"], tx["sender_type"], tx["receiver_id"], tx["receiver_type"], tx["amount"], tx["timestamp"], tx["device_id"], tx["ip_address"], tx["location"], tx["layer_index"]))

    # 5. Historical Cashouts
    base_time = datetime(2026, 8, 1, 10, 0, 0)
    for i in range(250):
        loc = random.choices(
            locations,
            weights=[35, 30, 15, 8, 4, 3, 3, 2],
            k=1
        )[0]
        cash_amt = round(random.choice([10000, 20000, 40000, 50000, 80000, 100000]), 2)
        dist = round(max(0.2, random.normalvariate(2.8, 1.4)), 2)
        w_time = base_time + timedelta(days=random.randint(0, 50), hours=random.randint(11, 19), minutes=random.randint(0, 59))
        mule_acc = f"MULE-HIST-{random.randint(100, 999)}"

        cursor.execute("""
        INSERT INTO historical_cashouts (id, location_id, amount, withdrawal_time, distance_from_last_hop_km, mule_account_id, successful)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (f"CASH-{1000+i}", loc["id"], cash_amt, w_time.strftime("%Y-%m-%d %H:%M:%S"), dist, mule_acc, 1))

    # 6. Default Alerts
    alerts = [
        {
            "id": "ALT-2026-8801",
            "case_id": "CASE-2026-4401",
            "case_title": "Operation ShadowMule: Multi-State UPI Siphon",
            "priority": "CRITICAL",
            "target_agencies": json.dumps(["LEA_DELHI_POLICE_CYBERCELL", "BANK_SBI_FRAUD_NODAL", "I4C_REGISTRY"]),
            "predicted_locations": json.dumps([
                {"location_id": "LOC-ATM-101", "name": "SBI 24x7 E-Corner ATM (Sector 7 Rohini)", "confidence": "95.0%"},
                {"location_id": "LOC-CSP-102", "name": "Airtel Payments Bank CSP & Money Transfer (Laxmi Nagar)", "confidence": "73.2%"}
            ]),
            "dispatched_at": "2026-09-24 14:22:10",
            "status": "DISPATCHED_ACTIVE",
            "action_code": "ACT-DEBIT-FREEZE-PATROL-DEPLOY",
            "summary": "Tactical alert issued for immediate ATM hotspot patrol at Rohini Sector 7 and debit freeze on Layer 2 mule account kumar.settle@paytm."
        }
    ]

    for a in alerts:
        cursor.execute("""
        INSERT INTO alerts (id, case_id, case_title, priority, target_agencies, predicted_locations, dispatched_at, status, action_code, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (a["id"], a["case_id"], a["case_title"], a["priority"], a["target_agencies"], a["predicted_locations"], a["dispatched_at"], a["status"], a["action_code"], a["summary"]))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_cybercrime_data()
    print("[SUCCESS] Successfully seeded database.")

