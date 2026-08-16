from hollowmedusa.engine.prompt_linter import PromptLinter


def test_prompt_linter_empty():
    linter = PromptLinter()
    errors = linter.lint("")
    assert len(errors) == 1
    assert "empty" in errors[0].lower()


def test_prompt_linter_undefined_var():
    linter = PromptLinter()
    errors = linter.lint("Use {{undefined_var}}", ["defined_var"])
    assert len(errors) == 1
    assert "undefined" in errors[0].lower()


def test_prompt_linter_contradiction():
    linter = PromptLinter()
    errors = linter.lint("Always do X. Never do X.")
    assert len(errors) == 1
    assert "contradictory" in errors[0].lower()


def test_prompt_linter_long():
    linter = PromptLinter()
    errors = linter.lint("x" * 10001)
    assert len(errors) == 1
    assert "10,000" in errors[0]
