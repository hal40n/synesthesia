from syn.audio.analysis import analyze
from syn.audio.capture import AudioCapture
from syn.config import Config
from syn.input.base import InputSource
from syn.llm.schema import LLMInput


class AudioInputSource(InputSource):
    """
    Observes a capture device and turns each window into an LLMInput.

    The session key, when given, overrides the estimated key: the
    performer knows the tonality better than an FFT does.
    """

    def __init__(self, key: str | None = None, capture=None):
        self.key = key
        self.capture = capture or AudioCapture(
            device=Config.SYN_AUDIO_DEVICE,
            sample_rate=Config.SYN_AUDIO_SAMPLE_RATE,
            window_seconds=Config.SYN_AUDIO_WINDOW_SECONDS,
        )
        self.capture.start()

    def read(self) -> LLMInput:
        samples = self.capture.read_window()
        features = analyze(samples, self.capture.sample_rate)
        return LLMInput(
            key=self.key or features.key_estimate or "unknown",
            pitch_classes=list(features.pitch_classes),
            frequencies=list(features.frequencies),
            dynamics=features.dynamics,
            density=features.density,
        )
