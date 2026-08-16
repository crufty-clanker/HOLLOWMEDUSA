"""PipelineRunner — executes the langgraph pipeline."""

from datetime import datetime

from ..config.agent_registry import AgentRegistry
from ..config.context_manager import ContextManager
from ..config.model_registry import ModelRegistry
from ..models.state import PipelineState, StepResult
from .agent import Agent


class PipelineRunner:
    """Execute a pipeline according to a graph topology.

    The runner:
    1. Builds agents from the registry
    2. Topologically sorts the graph
    3. Executes each node in order
    4. Captures results and errors
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        model_registry: ModelRegistry,
        context_manager: ContextManager,
    ):
        self.agent_registry = agent_registry
        self.model_registry = model_registry
        self.context_manager = context_manager
        self.agents: dict[str, Agent] = {}

    def build_agents(self):
        """Instantiate all agents from the registry."""
        for agent_config in self.agent_registry.list_agents():
            # Find matching harness
            from . import harnesses
            harness_cls = getattr(harnesses, f"{agent_config.harness.capitalize()}Harness", None)
            if not harness_cls:
                raise ValueError(f"Unknown harness: {agent_config.harness}")

            # Get model client
            model_client = self.model_registry.get_client(agent_config.primary_model)

            # Create agent
            agent = Agent(agent_config, harness_cls(), model_client)
            self.agents[agent_config.id] = agent

    async def run(self, state: PipelineState, graph: dict) -> PipelineState:
        """Execute the pipeline according to the graph topology.

        Args:
            state: Initial pipeline state.
            graph: Dict mapping node_id -> {"depends_on": [...]}

        Returns:
            Updated state with step results and errors.
        """
        state.started_at = datetime.now()

        # Topological sort of graph
        nodes = self._topological_sort(graph)

        for node_id in nodes:
            state.current_step = node_id
            agent = self.agents.get(node_id)
            if not agent:
                state.add_error(f"Agent not found: {node_id}")
                continue

            try:
                # Get context for this step
                context = self.context_manager.get_context_for_step(node_id)

                # Execute agent
                result = await agent.execute(state.to_dict(), context)

                # Record step result
                step_result = StepResult(
                    step=node_id,
                    status="succeeded" if result.success else "failed",
                    output=result.output,
                    error=result.error,
                )
                state.step_results.append(step_result)

                if not result.success:
                    state.add_error(f"Step {node_id} failed: {result.validation_errors}")

            except Exception as e:
                state.add_error(f"Step {node_id} error: {str(e)}")

        state.completed_at = datetime.now()
        state.current_step = None
        return state

    def _topological_sort(self, graph: dict) -> list[str]:
        """Topological sort of graph nodes using DFS.

        Args:
            graph: Dict mapping node_id -> {"depends_on": [...]}

        Returns:
            List of node IDs in execution order.
        """
        visited = set()
        order = []

        def visit(node):
            if node in visited:
                return
            visited.add(node)
            for neighbor in graph.get(node, {}).get("depends_on", []):
                visit(neighbor)
            order.append(node)

        for node in graph:
            visit(node)

        return order
