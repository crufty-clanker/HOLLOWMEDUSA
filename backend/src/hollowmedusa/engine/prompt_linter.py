"""PromptLinter — validates prompts for common issues."""

import re


class PromptLinter:
    """Validate prompts for contradictions, undefined variables, and format issues."""

    def __init__(self):
        self.errors: list[str] = []

    def lint(self, prompt: str, variables: list[str] | None = None) -> list[str]:
        """Lint a prompt and return a list of error strings.

        Args:
            prompt: The prompt text to validate.
            variables: List of defined variable names (for undefined var check).

        Returns:
            List of error strings (empty = valid).
        """
        self.errors = []

        # Check for empty prompt
        if not prompt.strip():
            self.errors.append("Prompt is empty")

        # Check for undefined variables
        if variables:
            defined_vars = set(variables)
            found_vars = re.findall(r"\{\{(\w+)\}\}", prompt)
            for var in found_vars:
                if var not in defined_vars:
                    self.errors.append(f"Undefined variable: {{{{ {var} }}}}")

        # Check for contradictory instructions
        if "always" in prompt.lower() and "never" in prompt.lower():
            self.errors.append("Prompt contains contradictory 'always' and 'never' instructions")

        # Check for excessive length (>10k chars)
        if len(prompt) > 10000:
            self.errors.append("Prompt exceeds 10,000 characters")

        return self.errors
