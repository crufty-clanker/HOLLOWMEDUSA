"""CodeHarness — generates + lints source code (Code Generation)."""

import ast
import re
from typing import Any

from ..harness import Harness, HarnessResult


class CodeHarness(Harness):
    """Generate and validate source code for pipeline nodes."""

    name = "code"

    def run(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        code = input_data.get("code", "") or input_data.get("llm_output", "")

        # Extract code blocks if wrapped in markdown
        if "```" in code:
            code = re.search(r"```(?:python)?\n(.*?)```", code, re.DOTALL)
            code = code.group(1) if code else code

        return HarnessResult(success=True, output=code.strip())

    def validate(self, output: Any) -> list[str]:
        errors = []
        if not isinstance(output, str):
            errors.append("Output must be a string")
            return errors

        if not output.strip():
            errors.append("Code is empty")
            return errors

        # Try to parse as Python AST
        try:
            ast.parse(output)
        except SyntaxError as e:
            errors.append(f"Python syntax error: {e}")

        return errors
