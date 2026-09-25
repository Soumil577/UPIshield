"""
Comprehensive Test Suite for UPIShield.
Validates:
1. Normal transaction produces low risk.
2. New device increases risk.
3. New beneficiary increases risk.
4. Large transaction increases risk.
5. New user can be evaluated without history.
6. Existing user's abnormal transaction receives behavioral risk.
7. Score is always between 0 and 100.
8. Decision is always ALLOW, VERIFY, or BLOCK.
9. All 3 demo scenarios produce their target decisions.
"""

import unittest
import pandas as pd

from src.config import DecisionThresholds
from src.behavior import build_user_profile, score_behavioral_anomaly
from src.risk_engine import RiskEngine, calculate_general_risk
from src.data_generator import generate_synthetic_transactions, get_user_history
from src.utils import DEMO_SCENARIOS
from src.ml_engine import MLAnomalyEngine


class TestUPIShieldRiskEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Generate a reproducible test dataset once for tests."""
        cls.df = generate_synthetic_transactions(seed=42)
        cls.engine = RiskEngine()
        cls.ml_engine = MLAnomalyEngine()
        cls.ml_engine.train_on_history(cls.df)

    def test_1_normal_transaction_produces_low_risk(self):
        """Test 1: Normal transaction for an existing user produces low risk and ALLOW decision."""
        user_history = get_user_history("user_std_01", self.df)
        normal_tx = {
            "transaction_id": "TXN_TEST_NORM",
            "user_id": "user_std_01",
            "amount": 750.0,
            "beneficiary_id": "BENEF_SUPERMART",
            "beneficiary_new": 0,
            "device_id": "DEV_AARAV_PHONE",
            "device_new": 0,
            "location": "Mumbai",
            "hour": 14,
            "timestamp": "2026-08-25 14:00:00",
            "transaction_frequency": 2.0
        }
        res = self.engine.evaluate_transaction(normal_tx, user_history_df=user_history)
        self.assertLessEqual(res.final_score, 39.0)
        self.assertEqual(res.decision, "ALLOW")

    def test_2_new_device_increases_risk(self):
        """Test 2: Transacting on a new device increases the risk score."""
        user_history = get_user_history("user_std_01", self.df)
        base_tx = {
            "transaction_id": "TXN_BASE",
            "user_id": "user_std_01",
            "amount": 800.0,
            "beneficiary_id": "BENEF_SUPERMART",
            "beneficiary_new": 0,
            "device_id": "DEV_AARAV_PHONE",
            "device_new": 0,
            "location": "Mumbai",
            "hour": 14,
            "transaction_frequency": 2.0
        }
        new_dev_tx = base_tx.copy()
        new_dev_tx["device_id"] = "DEV_BRAND_NEW_PHONE"
        new_dev_tx["device_new"] = 1

        res_base = self.engine.evaluate_transaction(base_tx, user_history_df=user_history)
        res_new_dev = self.engine.evaluate_transaction(new_dev_tx, user_history_df=user_history)

        self.assertGreater(res_new_dev.final_score, res_base.final_score)
        self.assertGreater(res_new_dev.general_score, res_base.general_score)
        self.assertGreater(res_new_dev.behavior_score, res_base.behavior_score)

    def test_3_new_beneficiary_increases_risk(self):
        """Test 3: Transacting to a new beneficiary increases the risk score."""
        user_history = get_user_history("user_std_01", self.df)
        base_tx = {
            "transaction_id": "TXN_BASE_BEN",
            "user_id": "user_std_01",
            "amount": 800.0,
            "beneficiary_id": "BENEF_SUPERMART",
            "beneficiary_new": 0,
            "device_id": "DEV_AARAV_PHONE",
            "device_new": 0,
            "location": "Mumbai",
            "hour": 14,
            "transaction_frequency": 2.0
        }
        new_ben_tx = base_tx.copy()
        new_ben_tx["beneficiary_id"] = "BENEF_UNKNOWN_TARGET"
        new_ben_tx["beneficiary_new"] = 1

        res_base = self.engine.evaluate_transaction(base_tx, user_history_df=user_history)
        res_new_ben = self.engine.evaluate_transaction(new_ben_tx, user_history_df=user_history)

        self.assertGreater(res_new_ben.final_score, res_base.final_score)
        self.assertGreater(res_new_ben.general_score, res_base.general_score)
        self.assertGreater(res_new_ben.behavior_score, res_base.behavior_score)

    def test_4_large_transaction_increases_risk(self):
        """Test 4: Unusually large transaction amount increases general risk."""
        small_tx = {"amount": 500.0, "device_new": 0, "beneficiary_new": 0, "hour": 14, "transaction_frequency": 1.0}
        large_tx = {"amount": 60000.0, "device_new": 0, "beneficiary_new": 0, "hour": 14, "transaction_frequency": 1.0}

        score_small, _ = calculate_general_risk(small_tx)
        score_large, reasons = calculate_general_risk(large_tx)

        self.assertGreater(score_large, score_small)
        self.assertTrue(any("₹50,000" in r or "high transaction value" in r.lower() for r in reasons))

    def test_5_new_user_can_be_evaluated_without_history(self):
        """Test 5: A user with zero history can be evaluated successfully via general rules."""
        empty_history = pd.DataFrame()
        new_user_tx = {
            "transaction_id": "TXN_NEW_USER",
            "user_id": "user_brand_new",
            "amount": 35000.0,
            "beneficiary_id": "BENEF_RANDOM",
            "beneficiary_new": 1,
            "device_id": "DEV_NEW_PHONE",
            "device_new": 1,
            "location": "Delhi",
            "hour": 2,
            "transaction_frequency": 1.0
        }
        res = self.engine.evaluate_transaction(new_user_tx, user_history_df=empty_history)
        self.assertEqual(res.history_status, "NO_HISTORY")
        self.assertEqual(res.weights_applied["general"], 1.0)
        self.assertEqual(res.weights_applied["behavior"], 0.0)
        self.assertEqual(res.final_score, res.general_score)
        self.assertGreaterEqual(res.final_score, 70.0)
        self.assertEqual(res.decision, "BLOCK")

    def test_6_existing_user_abnormal_transaction_receives_behavioral_risk(self):
        """Test 6: Existing user who deviates heavily receives a strong behavioral anomaly penalty."""
        user_history = get_user_history("user_std_01", self.df)
        abnormal_tx = {
            "transaction_id": "TXN_ABNORMAL",
            "user_id": "user_std_01",
            "amount": 30000.0,  # normally ~750
            "beneficiary_id": "BENEF_SHADY_MULE",
            "beneficiary_new": 1,
            "device_id": "DEV_EMULATOR_007",
            "device_new": 1,
            "location": "Kolkata",
            "hour": 3,
            "transaction_frequency": 6.0
        }
        res = self.engine.evaluate_transaction(abnormal_tx, user_history_df=user_history)
        self.assertEqual(res.history_status, "SUFFICIENT_HISTORY")
        self.assertGreaterEqual(res.behavior_score, 70.0)
        self.assertIn(res.decision, ["VERIFY", "BLOCK"])
        self.assertTrue(any("deviat" in r.lower() or "higher than" in r.lower() for r in res.behavior_reasons))

    def test_7_score_is_always_between_0_and_100(self):
        """Test 7: The risk score is strictly normalized between 0 and 100 across varied conditions."""
        extreme_tx_cases = [
            {"amount": 0.0, "device_new": 0, "beneficiary_new": 0, "hour": 12, "transaction_frequency": 0.5},
            {"amount": 500000.0, "device_new": 1, "beneficiary_new": 1, "hour": 3, "location": "unknown proxy", "transaction_frequency": 20.0},
            {"amount": -100.0, "device_new": 0, "beneficiary_new": 0, "hour": 15, "transaction_frequency": 1.0},
            {"amount": 1000000.0, "device_new": 1, "beneficiary_new": 1, "hour": 4, "location": "foreign vpn", "transaction_frequency": 50.0}
        ]

        for tx in extreme_tx_cases:
            res = self.engine.evaluate_transaction(tx, user_history_df=None)
            self.assertGreaterEqual(res.final_score, 0.0)
            self.assertLessEqual(res.final_score, 100.0)
            self.assertGreaterEqual(res.general_score, 0.0)
            self.assertLessEqual(res.general_score, 100.0)

    def test_8_decision_is_always_allow_verify_or_block(self):
        """Test 8: Output decision is always strictly one of ALLOW, VERIFY, or BLOCK."""
        scores_to_test = [0.0, 10.5, 38.9, 39.0, 39.1, 55.0, 68.9, 69.0, 69.1, 75.0, 100.0]
        thresh = DecisionThresholds(allow_max=39, verify_max=69)
        valid_decisions = {"ALLOW", "VERIFY", "BLOCK"}

        for s in scores_to_test:
            decision = thresh.classify(s)
            self.assertIn(decision, valid_decisions)

    def test_demo_scenarios(self):
        """Test the 3 demo scenarios to ensure expected outcomes for live review."""
        sc1 = DEMO_SCENARIOS["scenario_1"]
        res1 = self.engine.evaluate_transaction(sc1["payload"], user_history_df=get_user_history(sc1["payload"]["user_id"], self.df))
        self.assertEqual(res1.decision, sc1["expected_decision"])

        sc2 = DEMO_SCENARIOS["scenario_2"]
        res2 = self.engine.evaluate_transaction(sc2["payload"], user_history_df=get_user_history(sc2["payload"]["user_id"], self.df))
        self.assertIn(res2.decision, ["VERIFY", "BLOCK"])
        self.assertGreaterEqual(res2.behavior_score, 60.0)

        sc3 = DEMO_SCENARIOS["scenario_3"]
        res3 = self.engine.evaluate_transaction(sc3["payload"], user_history_df=get_user_history(sc3["payload"]["user_id"], self.df))
        self.assertEqual(res3.decision, sc3["expected_decision"])
        self.assertEqual(res3.history_status, "NO_HISTORY")


if __name__ == "__main__":
    unittest.main()

