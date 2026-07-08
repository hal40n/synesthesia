import json
from unittest.mock import patch

import pytest

from syn.config import Config
from syn.session import Session


@pytest.fixture
def research_log_dir(tmp_path, monkeypatch):
    log_dir = tmp_path / "research"
    monkeypatch.setattr(Config, "SYN_LOG_RESEARCH_DIR", log_dir)
    return log_dir


@pytest.fixture
def live_log_dir(tmp_path, monkeypatch):
    log_dir = tmp_path / "live"
    monkeypatch.setattr(Config, "SYN_LOG_LIVE_DIR", log_dir)
    return log_dir


class TestResearchMode:
    def test_session_option_is_rejected(self):
        session = Session(mode="research", session_name="not-allowed")
        with pytest.raises(ValueError, match="--session is not allowed"):
            session.start()

    def test_start_writes_reproducible_log(self, research_log_dir, valid_output):
        session = Session(mode="research", key="C major", seed=42)
        with patch("syn.modes.research.LLMClient") as MockClient:
            MockClient.return_value.interpret.return_value = valid_output
            session.start()

        files = list(research_log_dir.glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text(encoding="utf-8"))
        assert data["mode"] == "research"
        assert data["seed"] == 42
        assert data["llm_input"]["key"] == "C major"
        assert data["llm_output"]["base_hue"] == 120.0
        assert data["temperature"] == Config.LLM_TEMPERATURE_RESEARCH


class TestLiveMode:
    def test_seed_option_is_rejected(self):
        session = Session(mode="live", seed=1)
        with pytest.raises(ValueError, match="--seed is not allowed"):
            session.start()

    def test_start_writes_trace_log_without_input(self, live_log_dir, valid_output):
        session = Session(mode="live", key="E minor", session_name="night-01")
        with patch("syn.modes.live.LLMClient") as MockClient:
            MockClient.return_value.interpret.return_value = valid_output
            session.start()

        files = list(live_log_dir.glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text(encoding="utf-8"))
        assert data["mode"] == "live"
        assert data["session"] == "night-01"
        # live logs are traces: they intentionally omit the full input
        assert "llm_input" not in data
        assert "seed" not in data
