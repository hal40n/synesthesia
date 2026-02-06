import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

def _required_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set")
    return value

class Config:
    PROMPT_RESEARCH = _required_env("PROMPT_RESEARCH")
    PROMPT_LIVE = _required_env("PROMPT_LIVE")
    SYN_LOG_DIR = _required_env("SYN_LOG_DIR")
    SYN_LOG_RESEARCH_DIR = _required_env("SYN_LOG_RESEARCH_DIR")
    SYN_LOG_LIVE_DIR = _required_env("SYN_LOG_LIVE_DIR")
    SYN_LLM_PROVIDER = _required_env("SYN_LLM_PROVIDER")
    SYN_LLM_MODEL = _required_env("SYN_LLM_MODEL")