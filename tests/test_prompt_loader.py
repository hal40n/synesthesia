import pytest

from syn.core.prompt_loader import load_prompt


def test_loads_existing_prompt():
    text = load_prompt("prompts/research.md")
    assert "Research Mode" in text


def test_leading_slash_is_stripped():
    assert load_prompt("/prompts/research.md") == load_prompt("prompts/research.md")


def test_missing_prompt_raises():
    with pytest.raises(FileNotFoundError):
        load_prompt("prompts/does-not-exist.md")
