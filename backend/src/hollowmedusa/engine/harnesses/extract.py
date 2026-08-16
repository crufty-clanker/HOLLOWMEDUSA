"""ExtractHarness — parses freeform text into structured data (Requirements)."""

import json
from typing import Any

from ..harness import Harness, HarnessResult


class ExtractHarness(Harness):
    """Extract structured requirements from freeform text."""

    name = "extract"

    def run(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        text = input_data.get("text", "") or input_data.get("llm_output", "")

        # Try to parse as JSON first
        try:
            parsed = json.loads(text)
            return HarnessResult(success=True, output=parsed)
        except json.JSONDecodeError:
            pass

        # Fallback: extract key-value pairs from text
        parsed = {}
        for line in text.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, _, value = line.partition(':')
                key = key.strip()
                value = value.strip()
                if key and value:
                    parsed[key] = value

        return HarnessResult(success=True, output=parsed)

    def validate(self, output: Any) -> list[str]:
        errors = []
        if not isinstance(output, dict):
            errors.append("Output must be a dict")
        if "goal" not in output:
            errors.append("Missing required field: goal")
        return errors
