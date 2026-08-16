"""TestHarness — runs tests and aggregates results (Testing)."""

import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..harness import Harness, HarnessResult


class TestHarness(Harness):
    """Execute tests and collect results."""

    name = "test"

    def run(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        test_files = input_data.get("test_files", {})

        # Write test files to temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            for file_path, code in test_files.items():
                full_path = tmp_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(code)

            # Run pytest
            try:
                result = subprocess.run(
                    ["python", "-m", "pytest", str(tmp_path), "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                test_results = {
                    "passed": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }

                return HarnessResult(success=result.returncode == 0, output=test_results)

            except subprocess.TimeoutExpired:
                return HarnessResult(
                    success=False,
                    error="Test execution timed out",
                )
            except Exception as e:
                return HarnessResult(
                    success=False,
                    error=f"Test execution failed: {str(e)}",
                )

    def validate(self, output: Any) -> list[str]:
        errors = []
        if not isinstance(output, dict):
            errors.append("Output must be a dict with test results")
            return errors

        if "passed" not in output:
            errors.append("Missing required field: passed")

        return errors
