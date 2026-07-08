import numpy as np
import pytest

from syn.input.audio import AudioInputSource
from syn.input.base import InputSource
from syn.llm.schema import LLMInput

SR = 44100


class FakeCapture:
    def __init__(self, samples: np.ndarray, sample_rate: int = SR):
        self.samples = samples
        self.sample_rate = sample_rate
        self.started = False

    def start(self):
        self.started = True

    def read_window(self) -> np.ndarray:
        return self.samples


def triad() -> np.ndarray:
    t = np.arange(SR * 2) / SR
    signal = (
        0.3 * np.sin(2 * np.pi * 261.63 * t)
        + 0.2 * np.sin(2 * np.pi * 329.63 * t)
        + 0.2 * np.sin(2 * np.pi * 392.0 * t)
    )
    return signal.astype(np.float32)


def test_read_analyzes_capture_window():
    source = AudioInputSource(capture=FakeCapture(triad()))
    llm_input = source.read()

    assert isinstance(llm_input, LLMInput)
    assert set(llm_input.pitch_classes) == {"C", "E", "G"}
    assert llm_input.key == "C major"
    assert llm_input.dynamics in ("soft", "medium", "loud")


def test_capture_is_started():
    capture = FakeCapture(triad())
    AudioInputSource(capture=capture)
    assert capture.started


def test_session_key_overrides_estimate():
    source = AudioInputSource(key="F# minor", capture=FakeCapture(triad()))
    assert source.read().key == "F# minor"


def test_silence_falls_back_to_unknown_key():
    silence = np.zeros(SR, dtype=np.float32)
    source = AudioInputSource(capture=FakeCapture(silence))
    llm_input = source.read()
    assert llm_input.key == "unknown"
    assert llm_input.pitch_classes == []


def test_is_an_input_source():
    assert isinstance(AudioInputSource(capture=FakeCapture(triad())), InputSource)


def test_factory_creates_audio_source(monkeypatch):
    import syn.input.audio as audio_module
    from syn.input.factory import create_input_source

    monkeypatch.setattr(
        audio_module, "AudioCapture", lambda **kwargs: FakeCapture(triad())
    )
    source = create_input_source("audio", key="D major")
    assert isinstance(source, AudioInputSource)
    assert source.read().key == "D major"
