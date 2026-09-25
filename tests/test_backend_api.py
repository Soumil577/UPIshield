"""
FastAPI REST Endpoints Test Suite for SIH26184 Backend.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app
from backend.synthetic_data import seed_cybercrime_data


class TestBackendAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed_cybercrime_data(seed=42)
        cls.client = TestClient(app)

    def test_01_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ONLINE")

    def test_02_dashboard_stats(self):
        res = self.client.get("/api/dashboard")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_complaints"], 0)
        self.assertGreater(data["total_cases"], 0)
        self.assertGreater(data["amount_at_risk"], 0.0)
        self.assertTrue(isinstance(data["recent_complaints"], list))
        self.assertTrue(isinstance(data["hotspot_locations"], list))

    def test_03_list_cases(self):
        res = self.client.get("/api/cases")
        self.assertEqual(res.status_code, 200)
        cases = res.json()
        self.assertGreaterEqual(len(cases), 1)
        self.assertEqual(cases[0]["id"], "CASE-2026-4401")

    def test_04_get_case_detail(self):
        res = self.client.get("/api/cases/CASE-2026-4401")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["id"], "CASE-2026-4401")
        self.assertIsNotNone(data["risk_evaluation"])
        self.assertIn(data["risk_evaluation"]["decision"], ["ALLOW", "VERIFY", "BLOCK"])

    def test_05_get_case_network_graph(self):
        res = self.client.get("/api/cases/CASE-2026-4401/network")
        self.assertEqual(res.status_code, 200)
        graph = res.json()
        self.assertGreater(len(graph["nodes"]), 0)
        self.assertGreater(len(graph["edges"]), 0)

    def test_06_predict_cashout_locations(self):
        res = self.client.post("/api/cases/CASE-2026-4401/predict-cashout")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["case_id"], "CASE-2026-4401")
        self.assertGreater(len(data["predicted_locations"]), 0)
        top_rank = data["predicted_locations"][0]
        self.assertEqual(top_rank["rank"], 1)
        self.assertIn(top_rank["risk_level"], ["CRITICAL", "HIGH", "MODERATE"])

    def test_07_list_complaints(self):
        res = self.client.get("/api/complaints")
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.json()), 0)

    def test_08_list_locations(self):
        res = self.client.get("/api/locations")
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.json()), 0)

    def test_09_create_and_get_alert(self):
        payload = {
            "case_id": "CASE-2026-4401",
            "location_ids": ["LOC-ATM-101", "LOC-CSP-102"],
            "target_agencies": ["LEA_TEST", "BANK_TEST"],
            "priority": "CRITICAL",
            "custom_notes": "Automated unit test alert dispatch."
        }
        res_post = self.client.post("/api/alerts", json=payload)
        self.assertEqual(res_post.status_code, 200)
        alert_data = res_post.json()
        self.assertEqual(alert_data["case_id"], "CASE-2026-4401")

        res_get = self.client.get("/api/alerts")
        self.assertEqual(res_get.status_code, 200)
        alerts_list = res_get.json()
        self.assertTrue(any(a["id"] == alert_data["id"] for a in alerts_list))


if __name__ == "__main__":
    unittest.main()
