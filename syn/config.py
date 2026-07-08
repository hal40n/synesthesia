import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent

load_dotenv(PROJECT_ROOT / ".env")

def _required_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set")
    return value

def _get_env_float(key: str) -> float:
    value = _required_env(key)
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Environment variable {key} must be a number")

def _resolve_path(key: str) -> Path:
    """Resolve a path relative to project root."""
    value = _required_env(key)
    return PROJECT_ROOT / value.lstrip("/")

class Config:
    PROMPT_RESEARCH = _required_env("PROMPT_RESEARCH")
    PROMPT_LIVE = _required_env("PROMPT_LIVE")
    SYN_LOG_DIR = _resolve_path("SYN_LOG_DIR")
    SYN_LOG_RESEARCH_DIR = _resolve_path("SYN_LOG_RESEARCH_DIR")
    SYN_LOG_LIVE_DIR = _resolve_path("SYN_LOG_LIVE_DIR")
    SYN_LLM_PROVIDER = _required_env("SYN_LLM_PROVIDER")
    SYN_LLM_MODEL = _required_env("SYN_LLM_MODEL")
    SYN_LLM_BASE_URL = _required_env("SYN_LLM_BASE_URL")
    # Live-mode observation source. "static" is the fixed triad; set
    # SYN_INPUT_SOURCE=audio to observe a capture device. Research
    # mode always observes the static input (reproducibility).
    SYN_INPUT_SOURCE = os.getenv("SYN_INPUT_SOURCE", "static")
    # Capture device: name, index, or unset for the system default
    # input (audio interface for instruments, BlackHole for on-Mac
    # sources). Printed when the capture stream starts.
    SYN_AUDIO_DEVICE = os.getenv("SYN_AUDIO_DEVICE") or None
    SYN_AUDIO_SAMPLE_RATE = int(os.getenv("SYN_AUDIO_SAMPLE_RATE", "44100"))
    SYN_AUDIO_WINDOW_SECONDS = float(os.getenv("SYN_AUDIO_WINDOW_SECONDS", "2.0"))
    LLM_TEMPERATURE_RESEARCH = _get_env_float("PROMPT_RESEARCH_TEMPERATURE")
    LLM_TEMPERATURE_LIVE = _get_env_float("PROMPT_LIVE_TEMPERATURE")        