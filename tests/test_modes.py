import json
import time
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

        # the mode must wire Config settings into the client explicitly
        client_kwargs = MockClient.call_args.kwargs
        assert client_kwargs["temperature"] == Config.LLM_TEMPERATURE_RESEARCH
        assert client_kwargs["provider"] == Config.SYN_LLM_PROVIDER
        assert client_kwargs["base_url"] == Config.SYN_LLM_BASE_URL
        assert client_kwargs["model"] == Config.SYN_LLM_MODEL

        files = list(research_log_dir.glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text(encoding="utf-8"))
        assert data["mode"] == "research"
        assert data["seed"] == 42
        assert data["llm_input"]["key"] == "C major"
        assert data["llm_output"]["base_hue"] == 120.0
        assert data["temperature"] == Config.LLM_TEMPERATURE_RESEARCH

    def test_input_source_env_cannot_break_reproducibility(
        self, research_log_dir, valid_output, monkeypatch
    ):
        """Research always observes the fixed input, even if the
        environment selects audio for live sessions."""
        monkeypatch.setattr(Config, "SYN_INPUT_SOURCE", "audio")
        session = Session(mode="research", key="C major", seed=7)
        with patch("syn.modes.research.LLMClient") as MockClient:
            MockClient.return_value.interpret.return_value = valid_output
            session.start()

        data = json.loads(
            next(iter(research_log_dir.glob("*.json"))).read_text(encoding="utf-8")
        )
        assert data["llm_input"]["pitch_classes"] == ["C", "E", "G"]


class WaitForLogRenderer:
    """Stands in for the pygame window: pulls frames until the
    interpretation thread has written a trace (or 3s pass)."""

    poll_dir = None

    def __init__(self, **kwargs):
        pass

    def run(self, next_state, max_frames=None):
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            next_state()
            if self.poll_dir is not None and list(self.poll_dir.glob("*.json")):
                time.sleep(0.05)  # let the thread finish its cycle
                return
            time.sleep(0.01)


class BriefRenderer:
    """Pulls frames for a moment, then quits."""

    def __init__(self, **kwargs):
        pass

    def run(self, next_state, max_frames=None):
        deadline = time.monotonic() + 0.2
        while time.monotonic() < deadline:
            next_state()
            time.sleep(0.01)


class TestLiveMode:
    def test_seed_option_is_rejected(self):
        session = Session(mode="live", seed=1)
        with pytest.raises(ValueError, match="--seed is not allowed"):
            session.start()

    def test_start_renders_and_writes_trace_log(self, live_log_dir, valid_output):
        session = Session(mode="live", key="E minor", session_name="night-01")
        WaitForLogRenderer.poll_dir = live_log_dir
        with (
            patch("syn.modes.live.LLMClient") as MockClient,
            patch("syn.modes.live.Renderer", WaitForLogRenderer),
        ):
            MockClient.return_value.interpret.return_value = valid_output
            session.start()

        # a static observation cannot change, so the session interprets
        # it exactly once
        files = list(live_log_dir.glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text(encoding="utf-8"))
        assert data["mode"] == "live"
        assert data["session"] == "night-01"
        # live logs are traces: they intentionally omit the full input
        assert "llm_input" not in data
        assert "seed" not in data

    def test_interpretation_failure_keeps_session_alive(self, live_log_dir):
        session = Session(mode="live", key="E minor")
        with (
            patch("syn.modes.live.LLMClient") as MockClient,
            patch("syn.modes.live.Renderer", BriefRenderer),
        ):
            MockClient.return_value.interpret.side_effect = RuntimeError("LLM down")
            session.start()  # must not raise: presence over crash

        assert list(live_log_dir.glob("*.json")) == []

    def test_logging_failure_does_not_kill_interpretation(self, valid_output, monkeypatch, tmp_path):
        # point the live log dir at a file so LiveLogger.write fails
        blocker = tmp_path / "not-a-dir"
        blocker.write_text("x")
        monkeypatch.setattr(Config, "SYN_LOG_LIVE_DIR", blocker)

        session = Session(mode="live", key="E minor")
        with (
            patch("syn.modes.live.LLMClient") as MockClient,
            patch("syn.modes.live.Renderer", BriefRenderer),
        ):
            MockClient.return_value.interpret.return_value = valid_output
            session.start()  # must not raise even though tracing is broken
