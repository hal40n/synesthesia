import collections
import threading

import numpy as np
import sounddevice as sd


class AudioCapture:
    """
    Continuously captures mono audio from one device into a ring buffer.

    The device is either an audio-interface input (instruments) or a
    loopback device such as BlackHole (sound playing on the Mac).
    """

    def __init__(
        self,
        device: str | None = None,
        sample_rate: int = 44100,
        window_seconds: float = 2.0,
    ):
        self.device = device
        self.sample_rate = sample_rate
        self.window_seconds = window_seconds
        self._window_samples = int(sample_rate * window_seconds)
        self._buffer = collections.deque(maxlen=self._window_samples)
        self._lock = threading.Lock()
        self._stream = None

    def _resolve_device(self) -> int | str | None:
        if self.device is None:
            return None  # system default input
        if self.device.isdigit():
            return int(self.device)
        return self.device

    def start(self):
        if self._stream is not None:
            return
        self._stream = sd.InputStream(
            device=self._resolve_device(),
            channels=1,
            samplerate=self.sample_rate,
            callback=self._on_audio,
        )
        self._stream.start()

    def stop(self):
        if self._stream is None:
            return
        self._stream.stop()
        self._stream.close()
        self._stream = None

    def _on_audio(self, indata, frames, time_info, status):
        mono = indata[:, 0] if indata.ndim > 1 else indata
        with self._lock:
            self._buffer.extend(mono.copy())

    def _snapshot(self) -> np.ndarray:
        with self._lock:
            return np.array(self._buffer, dtype=np.float32)

    def read_window(self) -> np.ndarray:
        """Latest window, left-padded with silence while filling up."""
        data = self._snapshot()
        missing = self._window_samples - len(data)
        if missing > 0:
            data = np.concatenate([np.zeros(missing, dtype=np.float32), data])
        return data

    def rms_now(self, seconds: float = 0.05) -> float:
        """Instantaneous level of the most recent audio (fast layer)."""
        data = self._snapshot()
        recent = data[-max(1, int(self.sample_rate * seconds)) :]
        if len(recent) == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(recent, dtype=np.float64))))
