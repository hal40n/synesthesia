import pytest

from syn.llm.schema import LLMOutput
from syn.render.state import (
    ColorState,
    ColorStateHolder,
    color_from_output,
    frame_state,
    hsv_to_rgb255,
    mix_brightness,
)


class TestColorFromOutput:
    def test_hue_is_base_plus_offset(self):
        output = LLMOutput(base_hue=100.0, hue_offset=20.0, saturation=0.5, brightness=0.6)
        state = color_from_output(output)
        assert state == ColorState(hue=120.0, saturation=0.5, brightness=0.6)

    def test_hue_wraps_around_the_circle(self):
        output = LLMOutput(base_hue=350.0, hue_offset=20.0, saturation=0.5, brightness=0.6)
        assert color_from_output(output).hue == pytest.approx(10.0)

    def test_negative_offset_wraps(self):
        output = LLMOutput(base_hue=5.0, hue_offset=-20.0, saturation=0.5, brightness=0.6)
        assert color_from_output(output).hue == pytest.approx(345.0)


class TestMixBrightness:
    def test_silence_dims_but_keeps_color_visible(self):
        assert 0 < mix_brightness(0.8, 0.0) < 0.8

    def test_loud_signal_restores_llm_brightness(self):
        assert mix_brightness(0.8, 0.5) == pytest.approx(0.8, abs=0.01)

    def test_monotonic_in_level(self):
        levels = [0.0, 0.02, 0.05, 0.1, 0.3]
        values = [mix_brightness(0.8, lv) for lv in levels]
        assert values == sorted(values)

    def test_stays_within_bounds(self):
        for llm_b in (0.0, 0.5, 1.0):
            for level in (0.0, 0.1, 5.0):
                assert 0.0 <= mix_brightness(llm_b, level) <= 1.0


class TestFrameState:
    def test_without_audio_returns_base_unchanged(self):
        base = ColorState(hue=120.0, saturation=0.5, brightness=0.6)
        assert frame_state(base, rms_now=None) is base

    def test_with_audio_modulates_brightness_only(self):
        base = ColorState(hue=120.0, saturation=0.5, brightness=0.6)
        modulated = frame_state(base, rms_now=0.0)
        assert modulated.hue == base.hue
        assert modulated.saturation == base.saturation
        assert modulated.brightness < base.brightness


class TestColorStateHolder:
    def test_get_returns_last_set(self):
        holder = ColorStateHolder(ColorState(0.0, 0.0, 0.0))
        state = ColorState(hue=42.0, saturation=0.4, brightness=0.7)
        holder.set(state)
        assert holder.get() is state


class TestHsvToRgb:
    def test_pure_red(self):
        assert hsv_to_rgb255(0.0, 1.0, 1.0) == (255, 0, 0)

    def test_black(self):
        assert hsv_to_rgb255(180.0, 1.0, 0.0) == (0, 0, 0)

    def test_green_hue(self):
        r, g, b = hsv_to_rgb255(120.0, 1.0, 1.0)
        assert (r, g, b) == (0, 255, 0)
