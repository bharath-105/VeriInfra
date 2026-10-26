"""
Root-Cause Ranking Engine using NetworkX Graph Traversal.

Identifies originating root causes across infrastructure asset dependency topologies.
"""

import logging
from typing import Dict, Any, List, Tuple
import networkx as nx

from gateway.src.digital_twin.asset_graph import DigitalTwinGraph

logger = logging.getLogger("RootCauseRanker")


class RootCauseRanker:
    """
    Ranks candidate root-cause assets across dependency graphs during multi-sensor anomalies.
    """

    def __init__(self, digital_twin: DigitalTwinGraph):
        self.dt = digital_twin

    def rank_root_causes(self, trigger_asset_id: str, anomaly_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Perform reverse topological traversal from trigger_asset_id to find upstream root cause origin.
        
        Returns:
            List of ranked root causes: [{"asset_id": str, "probability": float, "reason": str}]
        """
        graph = self.dt.graph
        if trigger_asset_id not in graph:
            return [{"asset_id": trigger_asset_id, "probability": 1.0, "reason": "Isolated Asset Node"}]

        # Find all upstream ancestors (assets that trigger_asset_id depends on)
        ancestors = list(nx.ancestors(graph, trigger_asset_id))
        candidates = ancestors + [trigger_asset_id]

        ranked_results = []
        total_score = 0.0

        for candidate_id in candidates:
            node_data = graph.nodes[candidate_id]
            crit = node_data.get("criticality", 1.0)
            node_anomaly = anomaly_scores.get(candidate_id, 0.5)

            # Compute path impact weight along shortest path to trigger
            path_weight = 1.0
            if candidate_id != trigger_asset_id:
                try:
                    path = nx.shortest_path(graph, candidate_id, trigger_asset_id)
                    for i in range(len(path) - 1):
                        edge_data = graph.get_edge_data(path[i], path[i+1])
                        path_weight *= edge_data.get("weight", 1.0)
                except nx.NetworkXNoPath:
                    path_weight = 0.5

            raw_rank_score = crit * node_anomaly * path_weight
            total_score += raw_rank_score
            ranked_results.append({
                "asset_id": candidate_id,
                "name": node_data.get("name", candidate_id),
                "type": node_data.get("type"),
                "raw_score": raw_rank_score,
                "path_impact_weight": round(path_weight, 3)
            })

        # Normalize probability scores
        for item in ranked_results:
            prob = (item["raw_score"] / total_score) if total_score > 0 else 0.5
            item["probability"] = round(prob, 3)
            item["reason"] = f"Upstream dependency path weight = {item['path_impact_weight']}"

        # Sort descending by probability
        ranked_results.sort(key=lambda x: x["probability"], reverse=True)
        return ranked_results
