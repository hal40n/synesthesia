import numpy as np
import pytest

from syn.audio.analysis import (
    analyze,
    chroma_vector,
    density_from_onset_rate,
    dominant_frequencies,
    dynamics_from_rms,
    estimate_key,
    onset_rate,
    pitch_classes_from_chroma,
    rms,
)

SR = 44100


def sine(freq: float, duration: float = 2.0, amp: float = 0.2, sr: int = SR) -> np.ndarray:
    t = np.arange(int(sr * duration)) / sr
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def c_major_triad() -> np.ndarray:
    # root slightly emphasized so the tonic estimate is stable
    return sine(261.63, amp=0.3) + sine(329.63, amp=0.2) + sine(392.0, amp=0.2)


def a_minor_triad() -> np.ndarray:
    return sine(220.0, amp=0.3) + sine(261.63, amp=0.2) + sine(329.63, amp=0.2)


class TestRmsAndDynamics:
    def test_rms_of_sine(self):
        # RMS of a sine is amp / sqrt(2)
        assert rms(sine(440.0, amp=0.2)) == pytest.approx(0.2 / np.sqrt(2), rel=0.01)

    def test_rms_of_silence_is_zero(self):
        assert rms(np.zeros(SR, dtype=np.float32)) == 0.0

    @pytest.mark.parametrize(
        "amp,expected",
        [(0.01, "soft"), (0.15, "medium"), (0.6, "loud")],
    )
    def test_dynamics_thresholds(self, amp, expected):
        assert dynamics_from_rms(rms(sine(440.0, amp=amp))) == expected


class TestChromaAndPitch:
    def test_triad_pitch_classes(self):
        chroma = chroma_vector(c_major_triad(), SR)
        assert set(pitch_classes_from_chroma(chroma)) == {"C", "E", "G"}

    def test_octaves_fold_to_same_class(self):
        low = chroma_vector(sine(261.63), SR)
        high = chroma_vector(sine(523.25), SR)
        assert pitch_classes_from_chroma(low) == pitch_classes_from_chroma(high) == ["C"]

    def test_silence_has_no_pitch_classes(self):
        chroma = chroma_vector(np.zeros(SR, dtype=np.float32), SR)
        assert pitch_classes_from_chroma(chroma) == []


class TestDominantFrequencies:
    def test_finds_triad_partials(self):
        found = dominant_frequencies(c_major_triad(), SR, top_n=3)
        assert len(found) == 3
        for expected, actual in zip([261.63, 329.63, 392.0], found):
            assert actual == pytest.approx(expected, abs=2.0)

    def test_silence_has_no_frequencies(self):
        assert dominant_frequencies(np.zeros(SR, dtype=np.float32), SR) == []


class TestKeyEstimate:
    def test_major_triad(self):
        assert estimate_key(chroma_vector(c_major_triad(), SR)) == "C major"

    def test_minor_triad(self):
        assert estimate_key(chroma_vector(a_minor_triad(), SR)) == "A minor"

    def test_silence_has_no_key(self):
        assert estimate_key(chroma_vector(np.zeros(SR, dtype=np.float32), SR)) is None


class TestOnsetDensity:
    def _bursts(self, count: int, duration: float = 2.0) -> np.ndarray:
        """count short tone bursts evenly spread over duration seconds."""
        signal = np.zeros(int(SR * duration), dtype=np.float32)
        burst = sine(440.0, duration=0.08, amp=0.5)
        spacing = len(signal) // count
        for i in range(count):
            start = i * spacing
            signal[start : start + len(burst)] += burst
        return signal

    def test_sustained_tone_is_sparse(self):
        rate = onset_rate(sine(220.0, duration=2.0, amp=0.3), SR)
        assert density_from_onset_rate(rate) == "sparse"

    def test_moderate_bursts_are_normal(self):
        rate = onset_rate(self._bursts(4), SR)  # 2 onsets/sec
        assert density_from_onset_rate(rate) == "normal"

    def test_rapid_bursts_are_dense(self):
        rate = onset_rate(self._bursts(10), SR)  # 5 onsets/sec
        assert density_from_onset_rate(rate) == "dense"


class TestAnalyze:
    def test_triad_produces_full_features(self):
        features = analyze(c_major_triad(), SR)
        assert set(features.pitch_classes) == {"C", "E", "G"}
        assert features.key_estimate == "C major"
        assert features.dynamics in ("soft", "medium", "loud")
        assert features.density in ("sparse", "normal", "dense")
        assert len(features.frequencies) == 3

    def test_silence_produces_empty_observation(self):
        features = analyze(np.zeros(SR, dtype=np.float32), SR)
        assert features.pitch_classes == []
        assert features.frequencies == []
        assert features.dynamics == "soft"
        assert features.density == "sparse"
        assert features.key_estimate is None
