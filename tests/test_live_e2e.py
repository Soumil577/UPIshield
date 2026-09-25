"""
End-to-End Vertical Slice Integration Test for SIH26184 Prototype.
Verifies the complete flow:
Complaint -> Risk Analysis -> Entity Network -> Cash-Out Prediction -> Alert Generation
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app
from backend.synthetic_data import seed_cybercrime_data


class TestE2EVerticalSliceFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed_cybercrime_data(seed=42)
        cls.client = TestClient(app)

    def test_full_vertical_slice_workflow(self):
        """
        Executes step-by-step verification of the end-to-end target prototype flow.
        """
        # Step 1: Complaint retrieval
        comp_res = self.client.get("/api/complaints?case_id=CASE-2026-4401")
        self.assertEqual(comp_res.status_code, 200)
        complaints = comp_res.json()
        self.assertGreater(len(complaints), 0)
        victim_upi = complaints[0]["victim_upi"]
        self.assertIsNotNone(victim_upi)

        # Step 2: Risk analysis via Case detail
        case_res = self.client.get("/api/cases/CASE-2026-4401")
        self.assertEqual(case_res.status_code, 200)
        case_data = case_res.json()
        risk_eval = case_data["risk_evaluation"]
        self.assertIsNotNone(risk_eval)
        self.assertIn("final_score", risk_eval)
        self.assertIn("decision", risk_eval)

        # Step 3: Entity Network Graph resolution
        net_res = self.client.get("/api/cases/CASE-2026-4401/network")
        self.assertEqual(net_res.status_code, 200)
        graph = net_res.json()
        self.assertGreater(len(graph["nodes"]), 0)
        self.assertGreater(len(graph["edges"]), 0)

        # Step 4: Predict Cash-Out Locations
        pred_res = self.client.post("/api/cases/CASE-2026-4401/predict-cashout")
        self.assertEqual(pred_res.status_code, 200)
        predictions = pred_res.json()["predicted_locations"]
        self.assertGreater(len(predictions), 0)
        top_loc_id = predictions[0]["location_id"]

        # Step 5: Dispatch Actionable Intelligence Alert
        alert_payload = {
            "case_id": "CASE-2026-4401",
            "location_ids": [top_loc_id],
            "target_agencies": ["LEA_POLICE_CYBERCELL", "BANK_FRAUD_NODAL", "I4C_REGISTRY"],
            "priority": "CRITICAL",
            "custom_notes": "E2E Integration Verification: Immediate patrol dispatch."
        }
        alert_res = self.client.post("/api/alerts", json=alert_payload)
        self.assertEqual(alert_res.status_code, 200)
        alert_data = alert_res.json()
        self.assertEqual(alert_data["case_id"], "CASE-2026-4401")
        self.assertEqual(alert_data["status"], "DISPATCHED_ACTIVE")


if __name__ == "__main__":
    unittest.main()
