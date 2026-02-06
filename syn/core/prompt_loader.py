from pathlib import path

def load_prompt(path: str) -> str:
    prompt_path = Path(path)

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")

    return prompt_path.read_text(encoding="utf-8")