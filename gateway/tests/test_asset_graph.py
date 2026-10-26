"""
Unit & Integration Tests for NetworkX Digital Twin Asset Graph (Phase 4 Verification).

Run with:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s gateway/tests -p "test_*.py"
"""

import os
import sys
import unittest

# Set TESTING env var before importing app
os.environ["TESTING"] = "true"

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from gateway.src.digital_twin.asset_graph import DigitalTwinGraph, digital_twin_engine
from backend.app.main import app


class TestDigitalTwinAssetGraph(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dt = DigitalTwinGraph()
        cls.client = TestClient(app)

    def test_default_topology_structure(self):
        """Verify baseline graph contains 8 nodes and directed dependency edges."""
        self.assertEqual(self.dt.graph.number_of_nodes(), 8)
        self.assertGreaterEqual(self.dt.graph.number_of_edges(), 7)

        # Check key infrastructure assets exist
        self.assertIn("main_power", self.dt.graph)
        self.assertIn("ups_backup", self.dt.graph)
        self.assertIn("server_rack_01", self.dt.graph)
        self.assertIn("cooling_pump_01", self.dt.graph)

    def test_asset_status_update(self):
        """Verify asset status and risk score updates."""
        success = self.dt.update_asset_status("server_rack_01", "HIGH_RISK", 0.85)
        self.assertTrue(success)
        self.assertEqual(self.dt.graph.nodes["server_rack_01"]["status"], "HIGH_RISK")
        self.assertEqual(self.dt.graph.nodes["server_rack_01"]["risk_score"], 0.85)

    def test_downstream_impact_path(self):
        """Verify BFS traversal of affected downstream assets when power fails."""
        # If ups_backup fails, server_rack_01 and cooling_pump_01 must be impacted!
        impacted = self.dt.get_downstream_impact_path("ups_backup")
        
        self.assertIn("server_rack_01", impacted)
        self.assertIn("cooling_pump_01", impacted)
        self.assertIn("cooling_fan_01", impacted)

    def test_export_topology_dict(self):
        """Verify JSON export format for Cytoscape / Vis.js visualization."""
        topo = self.dt.export_topology_dict()
        
        self.assertEqual(topo["num_nodes"], 8)
        self.assertIn("nodes", topo)
        self.assertIn("edges", topo)
        
        # Check node payload fields
        first_node = topo["nodes"][0]
        self.assertIn("id", first_node)
        self.assertIn("label", first_node)
        self.assertIn("status", first_node)

    def test_fastapi_digital_twin_api(self):
        """Verify GET /api/v1/digital-twin/topology endpoint returns valid payload."""
        response = self.client.get("/api/v1/digital-twin/topology")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["num_nodes"], 8)

        # Test impact analysis API
        response_impact = self.client.get("/api/v1/digital-twin/impact/main_power")
        self.assertEqual(response_impact.status_code, 200)
        impact_data = response_impact.json()
        self.assertGreater(impact_data["affected_downstream_count"], 0)


if __name__ == "__main__":
    unittest.main()
