# Set all required environment variables BEFORE any syn import.
# syn.config.Config evaluates them at import time, and load_dotenv()
# does not override variables that are already set, so tests stay
# deterministic regardless of the local .env contents.
import os

os.environ["PROMPT_RESEARCH"] = "prompts/research.md"
os.environ["PROMPT_LIVE"] = "prompts/live.md"
os.environ["SYN_LOG_DIR"] = "logs"
os.environ["SYN_LOG_RESEARCH_DIR"] = "logs/research"
os.environ["SYN_LOG_LIVE_DIR"] = "logs/live"
os.environ["SYN_LLM_PROVIDER"] = "lmstudio"
os.environ["SYN_LLM_MODEL"] = "env-model"
os.environ["SYN_LLM_BASE_URL"] = "http://127.0.0.1:9999"
os.environ["PROMPT_RESEARCH_TEMPERATURE"] = "0.0"
os.environ["PROMPT_LIVE_TEMPERATURE"] = "0.7"

import pytest

from syn.llm.schema import LLMOutput


@pytest.fixture
def valid_output() -> LLMOutput:
    return LLMOutput(base_hue=120.0, hue_offset=10.0, saturation=0.5, brightness=0.6)
