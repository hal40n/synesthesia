"""Color state shared between the interpretation thread and the renderer.

Two layers with different tempos meet here:
- slow layer: the LLM decides hue/saturation/brightness every window
- fast layer: the instantaneous audio level modulates brightness per frame
"""

import colorsys
import threading
from dataclasses import dataclass, replace

from syn.llm.schema import LLMOutput

# How strongly the instantaneous level drives brightness. An RMS at or
# above 1/FAST_GAIN restores the LLM's full brightness.
FAST_GAIN = 8.0
# Brightness floor so the color never disappears between notes.
SILENT_FLOOR = 0.35


@dataclass(frozen=True)
class ColorState:
    hue: float  # 0..360
    saturation: float  # 0..1
    brightness: float  # 0..1


def color_from_output(output: LLMOutput) -> ColorState:
    return ColorState(
        hue=(output.base_hue + output.hue_offset) % 360.0,
        saturation=output.saturation,
        brightness=output.brightness,
    )


def mix_brightness(llm_brightness: float, rms_now: float) -> float:
    """Fast layer: scale the LLM's brightness by the current level."""
    level = min(1.0, max(0.0, rms_now) * FAST_GAIN)
    mixed = llm_brightness * (SILENT_FLOOR + (1.0 - SILENT_FLOOR) * level)
    return min(1.0, max(0.0, mixed))


def frame_state(base: ColorState, rms_now: float | None) -> ColorState:
    if rms_now is None:
        return base
    return replace(base, brightness=mix_brightness(base.brightness, rms_now))


def hsv_to_rgb255(hue: float, saturation: float, value: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb((hue % 360.0) / 360.0, saturation, value)
    return (round(r * 255), round(g * 255), round(b * 255))


class ColorStateHolder:
    """Thread-safe holder; states are immutable and swapped atomically."""

    def __init__(self, initial: ColorState):
        self._state = initial
        self._lock = threading.Lock()

    def set(self, state: ColorState):
        with self._lock:
            self._state = state

    def get(self) -> ColorState:
        with self._lock:
            return self._state
