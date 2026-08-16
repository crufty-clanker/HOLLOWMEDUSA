"""DocHarness — template-based documentation generation (Documentation)."""

from typing import Any

from ..harness import Harness, HarnessResult


class DocHarness(Harness):
    """Generate documentation from pipeline state and code."""

    name = "doc"

    def run(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        doc_text = input_data.get("documentation", "") or input_data.get("llm_output", "")

        # Basic markdown validation
        if not doc_text.strip():
            return HarnessResult(success=False, error="Documentation is empty")

        return HarnessResult(success=True, output=doc_text.strip())

    def validate(self, output: Any) -> list[str]:
        errors = []
        if not isinstance(output, str):
            errors.append("Output must be a string")
            return errors

        if not output.strip():
            errors.append("Documentation is empty")

        # Check for basic markdown structure
        if not any(output.startswith(marker) for marker in ['#', '##', '-']):
            errors.append("Documentation should start with a heading or list")

        return errors
