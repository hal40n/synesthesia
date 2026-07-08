from unittest.mock import patch

import pytest

from syn.cli import main


def test_start_research_creates_session():
    argv = ["syn", "start", "research", "--key", "C major", "--seed", "7"]
    with patch("sys.argv", argv), patch("syn.cli.Session") as MockSession:
        main()
    MockSession.assert_called_once_with(
        mode="research", key="C major", seed=7, session_name=None
    )
    MockSession.return_value.start.assert_called_once()


def test_invalid_mode_exits():
    argv = ["syn", "start", "hybrid"]
    with patch("sys.argv", argv), pytest.raises(SystemExit):
        main()


def test_missing_command_exits():
    argv = ["syn"]
    with patch("sys.argv", argv), pytest.raises(SystemExit):
        main()
