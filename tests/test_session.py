import pytest

from syn.modes.live import LiveMode
from syn.modes.research import ResearchMode
from syn.session import Session


def test_research_mode_is_created():
    session = Session(mode="research")
    assert isinstance(session.mode, ResearchMode)


def test_live_mode_is_created():
    session = Session(mode="live")
    assert isinstance(session.mode, LiveMode)


def test_invalid_mode_raises():
    with pytest.raises(ValueError, match="Invalid session mode"):
        Session(mode="hybrid")


def test_session_holds_context():
    session = Session(mode="live", key="E minor", session_name="night-01")
    assert session.key == "E minor"
    assert session.session_name == "night-01"
    assert session.seed is None
