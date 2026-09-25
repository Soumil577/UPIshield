"""
UPIShield — Interactive Streamlit Dashboard & Prototype Simulator
Demonstrating Dual-Layer Risk Scoring: General Risk + Personalized Behavioral Anomaly Detection.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from src.config import (
    DecisionThresholds,
    DEFAULT_THRESHOLD_ALLOW,
    DEFAULT_THRESHOLD_VERIFY,
    WEIGHTS_BY_HISTORY
)
from src.data_generator import (
    load_dataset,
    generate_synthetic_transactions,
    get_user_history,
    USER_ARCHETYPES,
    CSV_PATH
)
from src.behavior import build_user_profile, UserBehaviorProfile
from src.risk_engine import RiskEngine
from src.ml_engine import MLAnomalyEngine
from src.utils import DEMO_SCENARIOS, format_inr, get_decision_badge_html


# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="UPIShield — Dual-Layer Fraud Detection Prototype",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished, professional appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1A73E8;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #5F6368;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F8F9FA;
        border: 1px solid #DADCE0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .score-badge {
        font-size: 2.2rem;
        font-weight: 800;
    }
    .score-allow { color: #137333; }
    .score-verify { color: #B06000; }
    .score-block { color: #C5221F; }
    .explanation-box {
        background-color: #EEF4FD;
        border-left: 5px solid #1A73E8;
        padding: 14px 18px;
        border-radius: 6px;
        font-size: 1.02rem;
        margin: 15px 0;
        color: #202124
    }
    .explanation-box b{
        color: #1A73E8
    }
    .factor-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 14px;
        height: 100%;
    }
    .scenario-btn {
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "dataset" not in st.session_state:
    st.session_state.dataset = load_dataset()

if "ml_engine" not in st.session_state:
    ml = MLAnomalyEngine()
    ml.train_on_history(st.session_state.dataset)
    st.session_state.ml_engine = ml

# Default input state (can be overwritten by demo presets)
if "current_inputs" not in st.session_state:
    st.session_state.current_inputs = {
        "user_id": "user_std_01",
        "amount": 800.0,
        "beneficiary_id": "BENEF_SUPERMART",
        "beneficiary_new": False,
        "device_id": "DEV_AARAV_PHONE",
        "device_new": False,
        "location": "Mumbai",
        "hour": 14,
        "transaction_frequency": 2.0,
        "transaction_id": "TXN_SIM_101"
    }


# Helper callback to load demo scenarios into session state
def load_scenario(scenario_key: str):
    sc = DEMO_SCENARIOS[scenario_key]["payload"]
    st.session_state.current_inputs = {
        "user_id": sc["user_id"],
        "amount": float(sc["amount"]),
        "beneficiary_id": sc["beneficiary_id"],
        "beneficiary_new": bool(sc["beneficiary_new"]),
        "device_id": sc["device_id"],
        "device_new": bool(sc["device_new"]),
        "location": sc["location"],
        "hour": int(sc["hour"]),
        "transaction_frequency": float(sc["transaction_frequency"]),
        "transaction_id": sc["transaction_id"]
    }
    st.session_state.selected_scenario_info = DEMO_SCENARIOS[scenario_key]


# ==========================================
# SIDEBAR: SETTINGS & THRESHOLDS
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-shield-green.png", width=64)
    st.title("UPIShield Config")
    st.caption("College / Hackathon Prototype v0.1")
    
    st.divider()
    st.subheader("⚙️ Decision Thresholds")
    allow_thresh = st.slider("ALLOW Upper Cutoff (0 to X)", min_value=10, max_value=50, value=DEFAULT_THRESHOLD_ALLOW, step=1)
    verify_thresh = st.slider("VERIFY Upper Cutoff (X to Y)", min_value=allow_thresh + 5, max_value=85, value=DEFAULT_THRESHOLD_VERIFY, step=1)
    
    st.caption(f"🟢 **ALLOW**: 0 – {allow_thresh}")
    st.caption(f"🟡 **VERIFY**: {allow_thresh + 1} – {verify_thresh}")
    st.caption(f"🔴 **BLOCK**: {verify_thresh + 1} – 100")
    
    thresholds = DecisionThresholds(allow_max=allow_thresh, verify_max=verify_thresh)
    risk_engine = RiskEngine(thresholds=thresholds)

    st.divider()
    st.subheader("🤖 Auxiliary ML Layer")
    enable_ml = st.checkbox("Enable Isolation Forest baseline", value=True)

    st.divider()
    st.subheader("🔄 Data Management")
    if st.button("Regenerate Synthetic Dataset", use_container_width=True):
        new_df = generate_synthetic_transactions(seed=np.random.randint(1, 1000))
        new_df.to_csv(CSV_PATH, index=False)
        st.session_state.dataset = new_df
        st.session_state.ml_engine.train_on_history(new_df)
        st.success(f"Generated {len(new_df)} transactions!")
        st.rerun()

    st.info("ℹ️ **Simulated Proof-of-Concept**\nOperates strictly on synthetic data without connecting to real banking/NPCI networks.")


# ==========================================
# MAIN HEADER & RESEARCH IDEA BANNER
# ==========================================
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown('<p class="main-header">🛡️ UPIShield: Adaptive Fraud Prevention</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header"><b>Dual-Layer Architecture:</b> Generalized Rule Risk for new users + Personalized Behavioral Anomaly Detection for established users.</p>',
        unsafe_allow_html=True
    )
with col_h2:
    st.metric(label="Simulated Transactions", value=f"{len(st.session_state.dataset)}")

st.divider()

# ==========================================
# 1-CLICK DEMO SCENARIOS SECTION
# ==========================================
st.subheader("🎯 Preset Demo Scenarios (Live Presentation)")
st.caption("Click any preset below to populate the simulator with targeted evaluation flows:")

col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    if st.button("🟢 Scenario 1: Normal Routine", use_container_width=True):
        load_scenario("scenario_1")
        st.rerun()
    st.caption("**User:** Aarav (Regular) | **₹800** | Known Device | 14:00 → **ALLOW**")

with col_s2:
    if st.button("🟡 Scenario 2: Existing User Anomaly", use_container_width=True):
        load_scenario("scenario_2")
        st.rerun()
    st.caption("**User:** Aarav | **₹25,000** (Spike) | New Device | 03:30 AM → **BLOCK/VERIFY**")

with col_s3:
    if st.button("🔴 Scenario 3: Brand New User Risk", use_container_width=True):
        load_scenario("scenario_3")
        st.rerun()
    st.caption("**User:** Sneha (0 History) | **₹35,000** | New Device | 02:45 AM → **BLOCK**")


# Show active banner if a demo preset is loaded
if "selected_scenario_info" in st.session_state:
    info = st.session_state.selected_scenario_info
    st.success(f"**Loaded Preset:** {info['title']} — *{info['subtitle']}* (Expected: `{info['expected_decision']}`)")

st.divider()


# ==========================================
# TRANSACTION SIMULATOR & ANALYSIS TABS
# ==========================================
tab_sim, tab_profile, tab_dataset, tab_arch = st.tabs([
    "💳 Transaction Simulator", 
    "👤 User Behavioral Profiles", 
    "📊 Synthetic Dataset Explorer",
    "📐 Architecture & Research Concept"
])

with tab_sim:
    inputs = st.session_state.current_inputs

    # Available user list
    user_options = list(USER_ARCHETYPES.keys())
    user_labels = {uid: f"{uid} — {USER_ARCHETYPES[uid]['name']}" for uid in user_options}

    with st.form("simulator_form"):
        st.markdown("#### 📝 Transaction Parameters")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            selected_user = st.selectbox(
                "User Account",
                options=user_options,
                index=user_options.index(inputs["user_id"]) if inputs["user_id"] in user_options else 0,
                format_func=lambda u: user_labels.get(u, u),
                help="Select an existing user profile or a brand new user with 0 history"
            )
            tx_amount = st.number_input(
                "Transaction Amount (₹)",
                min_value=1.0,
                max_value=200000.0,
                value=float(inputs["amount"]),
                step=100.0,
                help="Enter payment amount in INR"
            )
            tx_hour = st.slider(
                "Time of Transaction (Hour 0-23)",
                min_value=0,
                max_value=23,
                value=int(inputs["hour"]),
                help="0 = Midnight, 12 = Noon, 23 = 11 PM"
            )

        with c2:
            beneficiary = st.text_input(
                "Beneficiary ID / UPI ID",
                value=inputs["beneficiary_id"],
                help="Identifier of the payment recipient"
            )
            beneficiary_new = st.checkbox(
                "Is Beneficiary New to User?",
                value=bool(inputs["beneficiary_new"]),
                help="Check if this is the first payment to this recipient"
            )
            location = st.text_input(
                "Location / City",
                value=inputs["location"],
                help="City or geo-location of the transaction"
            )

        with c3:
            device = st.text_input(
                "Device Identifier",
                value=inputs["device_id"],
                help="Device fingerprint / ID"
            )
            device_new = st.checkbox(
                "Is Device New / Unregistered?",
                value=bool(inputs["device_new"]),
                help="Check if this device has not been used previously by this user"
            )
            frequency = st.number_input(
                "Recent Frequency (tx/hr)",
                min_value=0.5,
                max_value=20.0,
                value=float(inputs["transaction_frequency"]),
                step=0.5,
                help="Transaction velocity in transactions per hour"
            )

        col_btn1, col_btn2 = st.columns([2, 5])
        with col_btn1:
            submitted = st.form_submit_button("⚡ Analyze Transaction", use_container_width=True, type="primary")

    # Update state if submitted
    if submitted:
        st.session_state.current_inputs = {
            "user_id": selected_user,
            "amount": float(tx_amount),
            "beneficiary_id": beneficiary,
            "beneficiary_new": bool(beneficiary_new),
            "device_id": device,
            "device_new": bool(device_new),
            "location": location,
            "hour": int(tx_hour),
            "transaction_frequency": float(frequency),
            "transaction_id": "TXN_SIM_" + datetime.now().strftime("%H%M%S")
        }

    # Execute Evaluation
    active_tx = st.session_state.current_inputs
    user_history_df = get_user_history(active_tx["user_id"], st.session_state.dataset)
    
    # Run Risk Engine
    eval_result = risk_engine.evaluate_transaction(
        tx=active_tx,
        user_history_df=user_history_df,
        ml_model=st.session_state.ml_engine if enable_ml else None
    )

    st.markdown("### 📊 Evaluation Results")

    # Metrics Summary Row
    res_col1, res_col2, res_col3, res_col4 = st.columns([2, 2, 2, 2])

    with res_col1:
        score_val = eval_result.final_score
        score_class = "score-allow" if score_val <= allow_thresh else ("score-verify" if score_val <= verify_thresh else "score-block")
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:0.85rem; color:#5F6368; font-weight:600;">FINAL RISK SCORE</span>
            <div class="score-badge {score_class}">{score_val:.0f} <span style="font-size:1.1rem; color:#5F6368;">/ 100</span></div>
        </div>
        """, unsafe_allow_html=True)

    with res_col2:
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:0.85rem; color:#5F6368; font-weight:600;">SYSTEM DECISION</span>
            <div style="margin-top: 6px;">{get_decision_badge_html(eval_result.decision)}</div>
        </div>
        """, unsafe_allow_html=True)

    with res_col3:
        w_gen = eval_result.weights_applied["general"] * 100
        w_beh = eval_result.weights_applied["behavior"] * 100
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:0.85rem; color:#5F6368; font-weight:600;">HISTORY COHORT</span>
            <div style="font-size:1.15rem; font-weight:700; color:#202124; margin-top:4px;">{eval_result.history_status}</div>
            <span style="font-size:0.8rem; color:#5F6368;">Weights: {w_gen:.0f}% Gen / {w_beh:.0f}% Beh</span>
        </div>
        """, unsafe_allow_html=True)

    with res_col4:
        ml_display = f"{eval_result.ml_anomaly_score:.1f} / 100" if eval_result.ml_anomaly_score is not None else "Disabled"
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:0.85rem; color:#5F6368; font-weight:600;">ML ANOMALY SCORE</span>
            <div style="font-size:1.3rem; font-weight:700; color:#4285F4; margin-top:2px;">{ml_display}</div>
            <span style="font-size:0.8rem; color:#5F6368;">Isolation Forest (Auxiliary)</span>
        </div>
        """, unsafe_allow_html=True)

    # Plain-English Executive Summary
    st.markdown(f"""
    <div class="explanation-box">
        <b>💡 Human-Readable Panel Verdict:</b><br/>
        {eval_result.human_readable_summary}
    </div>
    """, unsafe_allow_html=True)

    # Detailed Dual-Layer Explanations
    col_layer1, col_layer2 = st.columns(2)

    with col_layer1:
        st.markdown("#### 🌐 Layer 1: General Risk Factors")
        st.caption(f"Score: **{eval_result.general_score:.1f}/100** (Weight applied: **{eval_result.weights_applied['general']*100:.0f}%**)")
        st.markdown("""
        *Evaluates absolute transaction features without needing past user profile history.*
        """)
        for reason in eval_result.general_reasons:
            if "safe baselines" in reason.lower():
                st.success(f"✔️ {reason}")
            else:
                st.warning(f"⚠️ {reason}")

    with col_layer2:
        st.markdown("#### 👤 Layer 2: Personalized Behavioral Factors")
        st.caption(f"Score: **{eval_result.behavior_score:.1f}/100** (Weight applied: **{eval_result.weights_applied['behavior']*100:.0f}%**)")
        st.markdown("""
        *Measures deviations against user's historical amount, timing, devices, and recipients.*
        """)
        for reason in eval_result.behavior_reasons:
            if "no prior user" in reason.lower():
                st.info(f"ℹ️ {reason}")
            elif "aligns" in reason.lower() or "safe" in reason.lower():
                st.success(f"✔️ {reason}")
            else:
                st.error(f"🚨 {reason}")


# ==========================================
# USER PROFILE INSPECTOR TAB
# ==========================================
with tab_profile:
    st.subheader("👤 User Behavioral Profiler")
    st.caption("Inspect how UPIShield establishes behavioral baselines from historical synthetic transactions.")

    selected_prof_user = st.selectbox(
        "Select User Profile to Inspect",
        options=list(USER_ARCHETYPES.keys()),
        format_func=lambda u: f"{u} — {USER_ARCHETYPES[u]['name']}",
        key="prof_user_select"
    )

    prof_history = get_user_history(selected_prof_user, st.session_state.dataset)
    profile = build_user_profile(selected_prof_user, prof_history)
    prof_dict = profile.to_dict()

    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    p_col1.metric("Historical Transactions", f"{profile.tx_count} tx")
    p_col2.metric("Average Amount", f"₹{profile.avg_amount:,.2f}")
    p_col3.metric("Median Amount", f"₹{profile.median_amount:,.2f}")
    p_col4.metric("History Cohort", profile.cohort)

    st.markdown("#### 🔍 Established Baselines")
    p_d1, p_d2 = st.columns(2)
    
    with p_d1:
        st.markdown(f"**Amount Range:** `{prof_dict['amount_range']}`")
        st.markdown(f"**Amount Std Deviation:** `₹{profile.std_amount:,.2f}`")
        st.markdown(f"**90th Percentile:** `₹{profile.p90_amount:,.2f}`")
        st.markdown(f"**Typical Active Hours:** `{prof_dict['active_hours_range']}`")
        st.markdown(f"**Average Frequency:** `{prof_dict['avg_frequency']} tx/hr`")

    with p_d2:
        st.markdown(f"**Known Devices ({len(profile.known_devices)}):**")
        if profile.known_devices:
            st.write(list(profile.known_devices))
        else:
            st.write("*None (New User)*")

        st.markdown(f"**Known Beneficiaries ({len(profile.known_beneficiaries)}):**")
        if profile.known_beneficiaries:
            st.write(list(profile.known_beneficiaries))
        else:
            st.write("*None (New User)*")

        st.markdown(f"**Known Locations ({len(profile.known_locations)}):**")
        if profile.known_locations:
            st.write(list(profile.known_locations))
        else:
            st.write("*None (New User)*")

    if not prof_history.empty:
        st.markdown("#### 📜 User's Historical Transactions")
        st.dataframe(prof_history[["transaction_id", "amount", "timestamp", "beneficiary_id", "device_id", "location", "fraud_label"]], use_container_width=True)


# ==========================================
# SYNTHETIC DATA EXPLORER TAB
# ==========================================
with tab_dataset:
    st.subheader("📊 Synthetic Transaction Dataset")
    st.caption("Browse and filter the pre-generated simulated transactions.")
    
    df_display = st.session_state.dataset.copy()
    
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        filter_user = st.multiselect("Filter by User ID", options=df_display["user_id"].unique(), default=[])
    with c_f2:
        filter_fraud = st.selectbox("Filter by Label", options=["All", "Normal Transactions Only (0)", "Injected Anomalies (1)"])

    if filter_user:
        df_display = df_display[df_display["user_id"].isin(filter_user)]
    if filter_fraud == "Normal Transactions Only (0)":
        df_display = df_display[df_display["fraud_label"] == 0]
    elif filter_fraud == "Injected Anomalies (1)":
        df_display = df_display[df_display["fraud_label"] == 1]

    st.dataframe(df_display, use_container_width=True, height=400)
    st.caption(f"Showing {len(df_display)} records out of {len(st.session_state.dataset)} total.")


# ==========================================
# ARCHITECTURE & EXPLANATION TAB
# ==========================================
with tab_arch:
    st.subheader("📐 UPIShield Research Architecture")
    st.markdown("""
    ### Core Problem Solved
    Traditional fraud detection systems either rely purely on static rule sets (which fail to catch nuanced account takeovers) or heavily on machine learning behavioral profiles (which fail when a new user has zero transaction history).

    ### UPIShield Dual-Engine Solution
    UPIShield solves this by combining two complementary engines with a dynamic weighting layer:

    ```
                      ┌─────────────────────────────────────────┐
                      │      Incoming UPI Transaction Request    │
                      └────────────────────┬────────────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
       ┌─────────────────────────┐                   ┌─────────────────────────┐
       │   General Risk Engine   │                   │   Behavioral Profiler   │
       │ (History-Independent)   │                   │  (History-Dependent)    │
       │ - High Absolute Amounts │                   │ - Deviation from Median │
       │ - New Device / Recipient│                   │ - Unseen Device/Recipient│
       │ - Midnight Hours Window │                   │ - Out-of-profile Hours  │
       │ - High Velocity Burst   │                   │ - Location Jump         │
       └────────────┬────────────┘                   └────────────┬────────────┘
                    │ (General Score: 0-100)                      │ (Behavior Score: 0-100)
                    └──────────────────────┬──────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │       Dynamic Weighting Combiner        │
                      │  - NO_HISTORY: 100% Gen + 0% Beh        │
                      │  - LIMITED_HIST: 70% Gen + 30% Beh      │
                      │  - SUFFICIENT: 40% Gen + 60% Beh        │
                      └────────────────────┬────────────────────┘
                                           │ (Final Score: 0-100)
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    Decision & Explainability Layer      │
                      │  - 0..39: ALLOW                         │
                      │  - 40..69: VERIFY (Step-up 2FA/OTP)     │
                      │  - 70..100: BLOCK                       │
                      └─────────────────────────────────────────┘
    ```
    """)

