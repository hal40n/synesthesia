import json
from datetime import datetime, timezone

from syn.config import Config
from syn.log.base import BaseLogger
from syn.log.live import LiveLogger
from syn.log.research import ResearchLogger


class _TimestampOnlyLogger(BaseLogger):
    def write(self, data: dict):
        pass


def test_timestamp_is_utc_in_legacy_format():
    """Timestamps double as log filenames: keep the naive-UTC isoformat
    shape, and make sure the value really is UTC, not local time."""
    ts = _TimestampOnlyLogger().timestamp
    parsed = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    assert abs((now_utc - parsed).total_seconds()) < 5


def test_research_logger_writes_indented_json(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "SYN_LOG_RESEARCH_DIR", tmp_path / "research")
    logger = ResearchLogger()
    logger.write({"mode": "research", "seed": 1})

    files = list((tmp_path / "research").glob("*.json"))
    assert len(files) == 1
    raw = files[0].read_text(encoding="utf-8")
    assert json.loads(raw) == {"mode": "research", "seed": 1}
    assert "\n" in raw  # indented for human comparison


def test_live_logger_writes_compact_json(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "SYN_LOG_LIVE_DIR", tmp_path / "live")
    logger = LiveLogger()
    logger.write({"mode": "live"})

    files = list((tmp_path / "live").glob("*.json"))
    assert len(files) == 1
    assert json.loads(files[0].read_text(encoding="utf-8")) == {"mode": "live"}
