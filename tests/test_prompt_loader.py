import pytest

from syn.core.prompt_loader import load_prompt


def test_loads_existing_prompt():
    # Prompt wording is authoritative and freely editable (/prompts):
    # assert only that content is loaded, never pin its text.
    text = load_prompt("prompts/research.md")
    assert text.strip()


def test_leading_slash_is_stripped():
    assert load_prompt("/prompts/research.md") == load_prompt("prompts/research.md")


def test_missing_prompt_raises():
    with pytest.raises(FileNotFoundError):
        load_prompt("prompts/does-not-exist.md")
