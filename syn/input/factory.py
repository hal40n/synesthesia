from syn.input.base import InputSource
from syn.input.static import StaticInputSource


def create_input_source(name: str, key: str | None = None) -> InputSource:
    if name == "static":
        return StaticInputSource(key=key)
    if name == "audio":
        # imported lazily so the static path never needs sounddevice
        from syn.input.audio import AudioInputSource

        return AudioInputSource(key=key)
    raise ValueError(f"Unknown input source: {name}")
