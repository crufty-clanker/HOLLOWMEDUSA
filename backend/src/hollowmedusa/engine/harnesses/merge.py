"""MergeHarness — integrates code into project tree (Integration)."""

from typing import Any

from ..harness import Harness, HarnessResult


class MergeHarness(Harness):
    """Validate and merge generated code into the project structure."""

    name = "merge"

    def run(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        code_dict = input_data.get("code", {})
        merged = {}

        for file_path, code in code_dict.items():
            # Sanitize file path (prevent path traversal)
            safe_path = file_path.replace("..", "").lstrip("/")
            merged[safe_path] = code

        return HarnessResult(success=True, output=merged)

    def validate(self, output: Any) -> list[str]:
        errors = []
        if not isinstance(output, dict):
            errors.append("Output must be a dict of file_path -> code")
            return errors

        for file_path, code in output.items():
            if ".." in file_path:
                errors.append(f"Path traversal detected: {file_path}")
            if not code.strip():
                errors.append(f"Empty code for file: {file_path}")

        return errors
