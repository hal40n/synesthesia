from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

def load_prompt(filepath: str) -> str:
    # Remove leading slash if present and resolve relative to project root
    relative_path = filepath.lstrip("/")
    prompt_path = PROJECT_ROOT / relative_path

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")