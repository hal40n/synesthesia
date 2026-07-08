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
    SYN_LLM_BASE_URL = os.getenv("SYN_LLM_BASE_URL", "http://127.0.0.1:1234")
    LLM_TEMPERATURE_RESEARCH = _get_env_float("PROMPT_RESEARCH_TEMPERATURE")
    LLM_TEMPERATURE_LIVE = _get_env_float("PROMPT_LIVE_TEMPERATURE")        