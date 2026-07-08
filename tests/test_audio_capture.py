import numpy as np
import pytest

import syn.audio.capture as capture_module
from syn.audio.capture import AudioCapture


class FakeStream:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def close(self):
        self.stopped = True


@pytest.fixture
def fake_sd(monkeypatch):
    created = []

    class FakeSounddevice:
        @staticmethod
        def InputStream(**kwargs):
            stream = FakeStream(**kwargs)
            created.append(stream)
            return stream

    monkeypatch.setattr(capture_module, "sd", FakeSounddevice)
    return created


def test_start_opens_mono_stream_on_device(fake_sd):
    capture = AudioCapture(device="BlackHole 2ch", sample_rate=48000, window_seconds=1.0)
    capture.start()

    assert len(fake_sd) == 1
    stream = fake_sd[0]
    assert stream.started
    assert stream.kwargs["device"] == "BlackHole 2ch"
    assert stream.kwargs["channels"] == 1
    assert stream.kwargs["samplerate"] == 48000


def test_numeric_device_string_resolves_to_index(fake_sd):
    capture = AudioCapture(device="3", sample_rate=44100, window_seconds=1.0)
    capture.start()
    assert fake_sd[0].kwargs["device"] == 3


def test_default_device_is_none(fake_sd):
    capture = AudioCapture(device=None, sample_rate=44100, window_seconds=1.0)
    capture.start()
    assert fake_sd[0].kwargs["device"] is None


def test_read_window_pads_with_leading_silence(fake_sd):
    capture = AudioCapture(device=None, sample_rate=100, window_seconds=1.0)
    capture.start()

    block = np.ones((30, 1), dtype=np.float32) * 0.5
    capture._on_audio(block, 30, None, None)

    window = capture.read_window()
    assert len(window) == 100
    assert np.all(window[:70] == 0.0)
    assert np.all(window[70:] == 0.5)


def test_read_window_keeps_only_latest_samples(fake_sd):
    capture = AudioCapture(device=None, sample_rate=100, window_seconds=1.0)
    capture.start()

    capture._on_audio(np.full((80, 1), 0.1, dtype=np.float32), 80, None, None)
    capture._on_audio(np.full((80, 1), 0.2, dtype=np.float32), 80, None, None)

    window = capture.read_window()
    assert len(window) == 100
    assert np.all(window[-80:] == np.float32(0.2))
    assert np.all(window[:20] == np.float32(0.1))


def test_rms_now_reflects_recent_level(fake_sd):
    capture = AudioCapture(device=None, sample_rate=1000, window_seconds=1.0)
    capture.start()

    capture._on_audio(np.zeros((500, 1), dtype=np.float32), 500, None, None)
    capture._on_audio(np.full((500, 1), 0.4, dtype=np.float32), 500, None, None)

    assert capture.rms_now(seconds=0.1) == pytest.approx(0.4, rel=0.01)


def test_stop_closes_stream(fake_sd):
    capture = AudioCapture(device=None, sample_rate=100, window_seconds=1.0)
    capture.start()
    capture.stop()
    assert fake_sd[0].stopped
