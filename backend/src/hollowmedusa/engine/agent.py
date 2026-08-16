"""Agent — ties a harness + model + system prompt together."""

from ..config.agent_config import AgentConfig
from ..engine.harness import Harness, HarnessResult
from ..engine.model_client import ModelClient


class Agent:
    """Execute a pipeline step: inject prompt → call LLM → run harness → validate.

    An Agent is the unit of execution in the pipeline. It combines:
    - An AgentConfig (id, step, harness, system_prompt, model)
    - A Harness (validation + retry logic)
    - A ModelClient (LLM provider)
    """

    def __init__(self, config: AgentConfig, harness: Harness, model_client: ModelClient):
        self.config = config
        self.harness = harness
        self.model_client = model_client

    async def execute(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        """Run the full agent pipeline.

        1. Build prompt from system prompt + input data
        2. Call LLM with the compiled prompt
        3. Run harness on LLM output
        4. Validate harness output
        5. Return result
        """
        # 1. Build the prompt
        prompt = self._build_prompt(input_data, context)

        # 2. Call LLM
        llm_response = await self.model_client.generate(
            prompt=prompt,
            system_prompt=self.config.system_prompt,
            model=self.config.primary_model,
        )

        # 3. Run harness
        harness_result = self.harness.run(
            input_data={"llm_output": llm_response.content, **input_data},
            context=context,
        )

        # 4. Validate
        validation_errors = self.harness.validate(harness_result.output)
        if validation_errors:
            harness_result.validation_errors = validation_errors
            harness_result.success = False

        return harness_result

    def _build_prompt(self, input_data: dict, context: dict | None) -> str:
        """Inject context variables into the prompt."""
        prompt_parts = [self.config.system_prompt, "\n\nInput:\n"]

        for key, value in input_data.items():
            if key != "llm_output":
                prompt_parts.append(f"{key}: {value}\n")

        if context:
            prompt_parts.append(f"\nContext:\n{context}")

        return "\n".join(prompt_parts)
