"""CompileHarness — assembles prompts from templates + variables (Prompt Engineering)."""

import re
from typing import Any

from ..harness import Harness, HarnessResult


class CompileHarness(Harness):
    """Compile system prompts from templates with variable substitution."""

    name = "compile"

    def run(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        prompts = input_data.get("prompts", {})
        compiled = {}

        for node_id, prompt_template in prompts.items():
            # Substitute variables: {{variable_name}}
            compiled_prompt = self._substitute_variables(prompt_template, input_data)
            compiled[node_id] = compiled_prompt

        return HarnessResult(success=True, output=compiled)

    def _substitute_variables(self, template: str, data: dict) -> str:
        """Replace {{variable}} placeholders with values from data."""

        def replace_match(match):
            var_name = match.group(1)
            # Check nested data
            if var_name in data:
                return str(data[var_name])
            # Check nested dict access: {{architecture.goal}}
            parts = var_name.split(".")
            current = data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return match.group(0)  # Leave unchanged
            return str(current)

        return re.sub(r"\{\{(\w+(?:\.\w+)*)\}\}", replace_match, template)

    def validate(self, output: Any) -> list[str]:
        errors = []
        if not isinstance(output, dict):
            errors.append("Output must be a dict")
            return errors

        # Check for unresolved variables
        for node_id, prompt in output.items():
            unresolved = re.findall(r"\{\{(\w+)\}\}", prompt)
            if unresolved:
                errors.append(f"Node {node_id}: unresolved variables {unresolved}")

        return errors
