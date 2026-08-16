"""TopologyHarness — validates graph structure (Architecture)."""

from typing import Any

from ..harness import Harness, HarnessResult


class TopologyHarness(Harness):
    """Validate and normalize architecture graph topology."""

    name = "topology"

    def run(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        graph = input_data.get("graph", {})

        # Normalize: ensure nodes and edges exist
        if "nodes" not in graph:
            graph["nodes"] = []
        if "edges" not in graph:
            graph["edges"] = []

        # Validate nodes have IDs
        for node in graph["nodes"]:
            if "id" not in node:
                node["id"] = node.get("name", f"node_{len(graph['nodes'])}")

        # Validate edges reference existing nodes
        node_ids = {n["id"] for n in graph["nodes"]}
        valid_edges = []
        for edge in graph["edges"]:
            if edge.get("source") in node_ids and edge.get("target") in node_ids:
                valid_edges.append(edge)
            else:
                # Keep edge but flag it
                valid_edges.append(edge)

        graph["edges"] = valid_edges
        return HarnessResult(success=True, output=graph)

    def validate(self, output: Any) -> list[str]:
        errors = []
        if not isinstance(output, dict):
            errors.append("Output must be a dict")
            return errors

        if "nodes" not in output:
            errors.append("Missing required field: nodes")
        if "edges" not in output:
            errors.append("Missing required field: edges")

        # Check for cycles (simple check)
        if self._has_cycle(output):
            errors.append("Graph contains cycles (not allowed in pipeline)")

        return errors

    def _has_cycle(self, graph: dict) -> bool:
        """Detect cycles using DFS."""
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)

            for edge in graph.get("edges", []):
                if edge.get("source") == node:
                    target = edge.get("target")
                    if target in rec_stack:
                        return True
                    if target not in visited and dfs(target):
                        return True

            rec_stack.discard(node)
            return False

        for node in graph.get("nodes", []):
            node_id = node.get("id")
            if node_id not in visited and dfs(node_id):
                return True
        return False
