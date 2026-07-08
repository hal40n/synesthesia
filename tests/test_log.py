import json
from datetime import datetime

from syn.config import Config
from syn.log.live import LiveLogger
from syn.log.research import ResearchLogger


def test_timestamp_keeps_legacy_utc_format():
    """Timestamps are used as filenames: keep the naive-UTC isoformat shape."""
    logger_ts = ResearchLogger.__new__(ResearchLogger)
    super(ResearchLogger, logger_ts).__init__()
    datetime.strptime(logger_ts.timestamp, "%Y-%m-%dT%H:%M:%S.%f")


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
