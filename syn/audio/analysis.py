"""Pure feature extraction from a mono audio window.

Everything here observes; nothing interprets. Interpretation into color
belongs to the LLM, governed by /prompts.
"""

from dataclasses import dataclass

import numpy as np

PITCH_CLASSES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Audible band considered for pitch analysis (A0 .. ~top of guitar harmonics)
FREQ_MIN = 27.5
FREQ_MAX = 5000.0

# Level thresholds (tuned against instrument line levels in Phase 5)
SILENCE_RMS = 0.005
SOFT_RMS = 0.02
LOUD_RMS = 0.2

# Onset-per-second thresholds
SPARSE_ONSET_RATE = 1.0
DENSE_ONSET_RATE = 4.0

# A pitch class must carry at least this share of the strongest one
PITCH_CLASS_RELATIVE_THRESHOLD = 0.35


@dataclass(frozen=True)
class AudioFeatures:
    pitch_classes: list[str]
    frequencies: list[float]
    dynamics: str
    density: str
    key_estimate: str | None


def rms(samples: np.ndarray) -> float:
    if len(samples) == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(samples, dtype=np.float64))))


def dynamics_from_rms(value: float) -> str:
    if value < SOFT_RMS:
        return "soft"
    if value < LOUD_RMS:
        return "medium"
    return "loud"


def _spectrum(samples: np.ndarray, sample_rate: int):
    """Band-limited magnitude spectrum: DC and out-of-band bins are
    dropped here so no downstream threshold can be skewed by them."""
    window = samples * np.hanning(len(samples))
    magnitudes = np.abs(np.fft.rfft(window))
    freqs = np.fft.rfftfreq(len(samples), 1.0 / sample_rate)
    band = (freqs >= FREQ_MIN) & (freqs <= FREQ_MAX)
    return magnitudes[band], freqs[band]


def _chroma_from_spectrum(magnitudes: np.ndarray, freqs: np.ndarray) -> np.ndarray:
    chroma = np.zeros(12)
    if len(freqs) == 0:
        return chroma

    midi = 69.0 + 12.0 * np.log2(freqs / 440.0)
    classes = np.mod(np.round(midi).astype(int), 12)
    np.add.at(chroma, classes, magnitudes)

    total = chroma.sum()
    if total <= 1e-9:
        return np.zeros(12)
    return chroma / total


def chroma_vector(samples: np.ndarray, sample_rate: int) -> np.ndarray:
    """12-dim energy distribution over pitch classes (octave-folded)."""
    return _chroma_from_spectrum(*_spectrum(samples, sample_rate))


def pitch_classes_from_chroma(chroma: np.ndarray, top_n: int = 4) -> list[str]:
    peak = chroma.max()
    if peak <= 1e-9:
        return []
    order = np.argsort(chroma)[::-1][:top_n]
    return [
        PITCH_CLASSES[i]
        for i in order
        if chroma[i] >= peak * PITCH_CLASS_RELATIVE_THRESHOLD
    ]


def _dominant_from_spectrum(
    magnitudes: np.ndarray, freqs: np.ndarray, top_n: int = 3
) -> list[float]:
    if len(magnitudes) == 0 or magnitudes.max() <= 1e-9:
        return []

    floor = 0.05 * magnitudes.max()  # relative to the in-band maximum
    picked: list[float] = []
    for i in np.argsort(magnitudes)[::-1]:
        if magnitudes[i] < floor:
            break
        freq = float(freqs[i])
        if all(abs(freq - p) / p > 0.03 for p in picked):
            picked.append(freq)
        if len(picked) == top_n:
            break
    return sorted(round(f, 1) for f in picked)


def dominant_frequencies(
    samples: np.ndarray, sample_rate: int, top_n: int = 3
) -> list[float]:
    """Strongest spectral peaks, at least a semitone apart, ascending."""
    return _dominant_from_spectrum(*_spectrum(samples, sample_rate), top_n=top_n)


def estimate_key(chroma: np.ndarray) -> str | None:
    """Tonic = strongest pitch class; quality from its third."""
    if chroma.max() <= 1e-9:
        return None
    tonic = int(np.argmax(chroma))
    major_third = chroma[(tonic + 4) % 12]
    minor_third = chroma[(tonic + 3) % 12]
    quality = "major" if major_third >= minor_third else "minor"
    return f"{PITCH_CLASSES[tonic]} {quality}"


def onset_rate(
    samples: np.ndarray, sample_rate: int, frame_seconds: float = 0.05
) -> float:
    """Attacks per second, detected as rising frame-energy edges."""
    frame = max(1, int(frame_seconds * sample_rate))
    count = len(samples) // frame
    if count < 2:
        return 0.0

    frames = samples[: count * frame].reshape(count, frame)
    energies = np.sqrt(np.mean(np.square(frames, dtype=np.float64), axis=1))

    onsets = 0
    for prev, cur in zip(energies, energies[1:]):
        if cur > SILENCE_RMS and cur > prev * 1.5:
            onsets += 1
    duration = count * frame / sample_rate
    return onsets / duration


def density_from_onset_rate(rate: float) -> str:
    if rate < SPARSE_ONSET_RATE:
        return "sparse"
    if rate < DENSE_ONSET_RATE:
        return "normal"
    return "dense"


def analyze(samples: np.ndarray, sample_rate: int) -> AudioFeatures:
    level = rms(samples)
    if level < SILENCE_RMS:
        return AudioFeatures(
            pitch_classes=[],
            frequencies=[],
            dynamics="soft",
            density="sparse",
            key_estimate=None,
        )

    magnitudes, freqs = _spectrum(samples, sample_rate)
    chroma = _chroma_from_spectrum(magnitudes, freqs)
    return AudioFeatures(
        pitch_classes=pitch_classes_from_chroma(chroma),
        frequencies=_dominant_from_spectrum(magnitudes, freqs),
        dynamics=dynamics_from_rms(level),
        density=density_from_onset_rate(onset_rate(samples, sample_rate)),
        key_estimate=estimate_key(chroma),
    )
