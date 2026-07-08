from syn.input.base import InputSource
from syn.llm.schema import LLMInput


class StaticInputSource(InputSource):
    """
    Fixed C-major triad observation.

    Deterministic stand-in used when no audio capture is configured;
    also the reference input for reproducibility comparisons.
    """

    def __init__(self, key: str | None = None):
        self.key = key or "C major"

    def read(self) -> LLMInput:
        return LLMInput(
            key=self.key,
            pitch_classes=["C", "E", "G"],
            frequencies=[261.6, 329.6, 392.0],
            dynamics="medium",
            density="normal",
        )
