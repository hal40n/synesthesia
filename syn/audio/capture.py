import collections
import threading

import numpy as np
import sounddevice as sd


class AudioCapture:
    """
    Continuously captures mono audio from one device into a ring buffer.

    The device is either an audio-interface input (instruments) or a
    loopback device such as BlackHole (sound playing on the Mac).

    The buffer stores the callback's blocks as-is; the lock is only
    ever held for deque bookkeeping, never for large copies, so the
    real-time audio callback is never blocked by readers.
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
        self._blocks: collections.deque[np.ndarray] = collections.deque()
        self._total_samples = 0
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
        resolved = self._resolve_device()
        print(
            f"[audio] device={'system default' if resolved is None else resolved}, "
            f"sample_rate={self.sample_rate}"
        )
        self._stream = sd.InputStream(
            device=resolved,
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
        if status:
            print(f"[audio] stream status: {status}")
        mono = indata[:, 0] if indata.ndim > 1 else indata
        block = mono.astype(np.float32, copy=True)
        with self._lock:
            self._blocks.append(block)
            self._total_samples += len(block)
            # drop whole old blocks while a full window still remains
            while (
                self._blocks
                and self._total_samples - len(self._blocks[0]) >= self._window_samples
            ):
                self._total_samples -= len(self._blocks.popleft())

    def _blocks_snapshot(self) -> list[np.ndarray]:
        # blocks are append-only arrays, so sharing references is safe
        with self._lock:
            return list(self._blocks)

    def read_window(self) -> np.ndarray:
        """Latest window, left-padded with silence while filling up."""
        blocks = self._blocks_snapshot()
        if not blocks:
            return np.zeros(self._window_samples, dtype=np.float32)

        data = np.concatenate(blocks)[-self._window_samples :]
        missing = self._window_samples - len(data)
        if missing > 0:
            data = np.concatenate([np.zeros(missing, dtype=np.float32), data])
        return data

    def rms_now(self, seconds: float = 0.05) -> float:
        """Instantaneous level of the most recent audio (fast layer)."""
        needed = max(1, int(self.sample_rate * seconds))
        recent: list[np.ndarray] = []
        collected = 0
        for block in reversed(self._blocks_snapshot()):
            recent.append(block)
            collected += len(block)
            if collected >= needed:
                break
        if collected == 0:
            return 0.0

        data = np.concatenate(recent[::-1])[-needed:]
        return float(np.sqrt(np.mean(np.square(data, dtype=np.float64))))
