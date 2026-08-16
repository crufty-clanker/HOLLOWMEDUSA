"""ReviewHarness — cross-cutting analysis with structured output (Review)."""

from typing import Any

from ..harness import Harness, HarnessResult


class ReviewHarness(Harness):
    """Perform code + prompt review and generate structured report."""

    name = "review"

    def run(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        review_text = input_data.get("review", "") or input_data.get("llm_output", "")

        review: dict[str, Any] = {
            "summary": "",
            "issues": [],
            "recommendations": [],
        }

        lines = review_text.split("\n")
        current_section: str | None = None
        current_content: list[str] = []

        def _clean_lines(items: list[str]) -> list[str]:
            return [
                item.strip().lstrip("- ").strip()
                for item in items
                if item.strip()
            ]

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("Summary:") or stripped.startswith("## Summary"):
                if current_section == "issues":
                    review["issues"] = _clean_lines(current_content)
                elif current_section == "recommendations":
                    review["recommendations"] = _clean_lines(current_content)
                current_section = "summary"
                current_content = [stripped.split(":", 1)[-1].strip()]
            elif stripped.startswith("Issues:") or stripped.startswith("## Issues"):
                if current_section == "summary":
                    review["summary"] = "\n".join(current_content).strip()
                current_section = "issues"
                current_content = []
            elif stripped.startswith("Recommendations:") or stripped.startswith(
                "## Recommendations"
            ):
                if current_section == "issues":
                    review["issues"] = _clean_lines(current_content)
                current_section = "recommendations"
                current_content = []
            else:
                current_content.append(line)

        if current_section == "summary":
            review["summary"] = "\n".join(current_content).strip()
        elif current_section == "issues":
            review["issues"] = _clean_lines(current_content)
        elif current_section == "recommendations":
            review["recommendations"] = _clean_lines(current_content)

        return HarnessResult(success=True, output=review)

    def validate(self, output: Any) -> list[str]:
        errors = []
        if not isinstance(output, dict):
            errors.append("Output must be a dict")
            return errors

        for field in ("summary", "issues", "recommendations"):
            if field not in output:
                errors.append(f"Missing required field: {field}")

        return errors
