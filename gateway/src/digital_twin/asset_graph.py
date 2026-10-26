"""
Digital Twin Asset Dependency Graph Engine using NetworkX.

Models infrastructure components, directed dependencies, and topological risk propagation paths.
"""

import logging
from typing import Dict, Any, List, Optional
import networkx as nx

logger = logging.getLogger("DigitalTwinGraph")


class DigitalTwinGraph:
    """
    NetworkX Directed Graph representing Digital Twin infrastructure topology.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.build_default_topology()

    def build_default_topology(self):
        """Construct baseline smart campus infrastructure dependency graph."""
        # 1. Add Infrastructure Nodes
        assets = [
            {"id": "main_power", "name": "Main Electrical Grid", "type": "POWER_SOURCE", "criticality": 1.0, "node_id": None},
            {"id": "ups_backup", "name": "UPS Battery Backup", "type": "POWER_BACKUP", "criticality": 0.9, "node_id": None},
            {"id": "cooling_pump_01", "name": "Chilled Water Pump", "type": "COOLING_SYSTEM", "criticality": 0.85, "node_id": "node_esp32_02"},
            {"id": "cooling_fan_01", "name": "Server Rack Intake Fan", "type": "COOLING_SYSTEM", "criticality": 0.8, "node_id": "node_esp32_01"},
            {"id": "server_rack_01", "name": "Primary Server Rack 01", "type": "COMPUTE_LOAD", "criticality": 1.0, "node_id": "node_esp32_01"},
            {"id": "server_rack_02", "name": "Secondary Storage Rack", "type": "COMPUTE_LOAD", "criticality": 0.7, "node_id": "node_esp32_01"},
            {"id": "water_supply_line", "name": "Utility Water Supply Line", "type": "WATER_SYSTEM", "criticality": 0.6, "node_id": "node_esp32_02"},
            {"id": "air_exhaust", "name": "HVAC Air Exhaust Vent", "type": "VENTILATION", "criticality": 0.5, "node_id": "node_esp32_01"}
        ]

        for asset in assets:
            self.graph.add_node(
                asset["id"],
                name=asset["name"],
                type=asset["type"],
                criticality=asset["criticality"],
                node_id=asset["node_id"],
                status="NORMAL",  # NORMAL, ADVISORY, HIGH_RISK, EMERGENCY_STOP
                risk_score=0.0
            )

        # 2. Add Directed Dependency Edges (Parent -> Child: Child depends on Parent)
        dependencies = [
            ("main_power", "ups_backup", "POWER_SUPPLY", 1.0),
            ("ups_backup", "server_rack_01", "POWER_SUPPLY", 1.0),
            ("ups_backup", "server_rack_02", "POWER_SUPPLY", 0.8),
            ("ups_backup", "cooling_pump_01", "POWER_SUPPLY", 0.9),
            ("cooling_pump_01", "cooling_fan_01", "COOLING_LINE", 0.85),
            ("cooling_fan_01", "server_rack_01", "THERMAL_DISSIPATION", 0.9),
            ("water_supply_line", "cooling_pump_01", "WATER_FEED", 0.75),
            ("air_exhaust", "server_rack_01", "VENTILATION", 0.5)
        ]

        for parent, child, dep_type, weight in dependencies:
            self.graph.add_edge(parent, child, dependency_type=dep_type, weight=weight)

        logger.info(f"Digital Twin Graph constructed with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")

    def update_asset_status(self, asset_id: str, status: str, risk_score: float = 0.0) -> bool:
        """Update node status and risk score in graph."""
        if asset_id in self.graph:
            self.graph.nodes[asset_id]["status"] = status
            self.graph.nodes[asset_id]["risk_score"] = round(risk_score, 3)
            logger.info(f"Asset '{asset_id}' status updated to {status} (risk={risk_score})")
            return True
        return False

    def get_downstream_impact_path(self, failed_asset_id: str) -> List[str]:
        """
        Find all downstream assets affected if `failed_asset_id` fails using BFS traversal.
        """
        if failed_asset_id not in self.graph:
            return []
        # Breadth-first search traversal of descendants
        affected = list(nx.descendants(self.graph, failed_asset_id))
        return affected

    def export_topology_dict(self) -> Dict[str, Any]:
        """
        Export graph in JSON-serializable format for Cytoscape / Vis.js frontend visualizers.
        """
        nodes_list = []
        for n, data in self.graph.nodes(data=True):
            nodes_list.append({
                "id": n,
                "label": data.get("name", n),
                "type": data.get("type"),
                "status": data.get("status", "NORMAL"),
                "risk_score": data.get("risk_score", 0.0),
                "criticality": data.get("criticality", 1.0),
                "node_id": data.get("node_id")
            })

        edges_list = []
        for u, v, data in self.graph.edges(data=True):
            edges_list.append({
                "source": u,
                "target": v,
                "dependency_type": data.get("dependency_type"),
                "weight": data.get("weight", 1.0)
            })

        return {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "nodes": nodes_list,
            "edges": edges_list
        }


# Global Digital Twin Instance
digital_twin_engine = DigitalTwinGraph()
