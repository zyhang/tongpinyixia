#!/usr/bin/env python3
"""Generate the restrained UI sounds used by 答案之外."""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 44_100
OUTPUT_DIR = Path(__file__).resolve().parent


def envelope(t: float, duration: float, attack: float, release: float) -> float:
    attack_gain = min(1.0, t / max(attack, 1e-6))
    release_gain = min(1.0, (duration - t) / max(release, 1e-6))
    return max(0.0, attack_gain * release_gain)


def low_pass(samples: list[float], cutoff_hz: float) -> list[float]:
    dt = 1.0 / SAMPLE_RATE
    rc = 1.0 / (2.0 * math.pi * cutoff_hz)
    alpha = dt / (rc + dt)
    filtered: list[float] = []
    value = 0.0
    for sample in samples:
        value += alpha * (sample - value)
        filtered.append(value)
    return filtered


def write_wav(filename: str, samples: list[float], peak_db: float) -> None:
    peak = max(abs(sample) for sample in samples) or 1.0
    target_peak = 10 ** (peak_db / 20.0)
    pcm = [max(-1.0, min(1.0, sample / peak * target_peak)) for sample in samples]
    with wave.open(str(OUTPUT_DIR / filename), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(b"".join(struct.pack("<h", round(sample * 32767)) for sample in pcm))


def choice_tap() -> list[float]:
    """A soft, neutral tap: short enough to feel tactile rather than audible."""
    duration = 0.105
    count = round(duration * SAMPLE_RATE)
    rng = random.Random(17)
    noise = low_pass([rng.uniform(-1.0, 1.0) for _ in range(count)], 1_900)
    samples: list[float] = []
    phase = 0.0
    for index in range(count):
        t = index / SAMPLE_RATE
        frequency = 410.0 * math.exp(-8.0 * t) + 135.0
        phase += 2.0 * math.pi * frequency / SAMPLE_RATE
        body = math.sin(phase) * math.exp(-32.0 * t)
        texture = noise[index] * math.exp(-48.0 * t)
        release = min(1.0, (duration - t) / 0.018)
        samples.append((0.86 * body + 0.14 * texture) * release)
    return samples


def resonance_glow() -> list[float]:
    """A tiny warm glow for acknowledging an anonymous reason."""
    duration = 0.30
    count = round(duration * SAMPLE_RATE)
    rng = random.Random(29)
    noise = low_pass([rng.uniform(-1.0, 1.0) for _ in range(count)], 3_200)
    samples: list[float] = []
    for index in range(count):
        t = index / SAMPLE_RATE
        env = envelope(t, duration, 0.018, 0.13) * math.exp(-2.6 * t)
        warm = math.sin(2.0 * math.pi * 466.16 * t + 0.15)
        glow = math.sin(2.0 * math.pi * 587.33 * t + 0.55)
        air = noise[index] * envelope(t, duration, 0.035, 0.18)
        samples.append(env * (0.58 * warm + 0.30 * glow) + 0.035 * air)
    return samples


def reason_float_away() -> list[float]:
    """An airy release for a reason being gently sent into 答案之外."""
    duration = 0.76
    count = round(duration * SAMPLE_RATE)
    rng = random.Random(43)
    raw_noise = [rng.uniform(-1.0, 1.0) for _ in range(count)]
    soft_noise = low_pass(raw_noise, 2_600)
    deep_noise = low_pass(raw_noise, 520)
    airy_noise = [soft - deep for soft, deep in zip(soft_noise, deep_noise)]
    samples: list[float] = []
    phase = 0.0
    for index in range(count):
        t = index / SAMPLE_RATE
        progress = t / duration
        frequency = 349.23 + 74.0 * (1.0 - math.exp(-3.5 * progress))
        phase += 2.0 * math.pi * frequency / SAMPLE_RATE
        tone_env = envelope(t, duration, 0.055, 0.31) * math.exp(-1.55 * t)
        tone = math.sin(phase) + 0.24 * math.sin(phase * 1.5 + 0.7)
        air_env = math.sin(math.pi * progress) ** 1.7
        second_note_t = t - 0.16
        second_note = 0.0
        if second_note_t >= 0:
            second_env = envelope(second_note_t, duration - 0.16, 0.045, 0.28)
            second_note = math.sin(2.0 * math.pi * 523.25 * second_note_t + 0.2) * second_env
        samples.append(0.52 * tone * tone_env + 0.22 * second_note + 0.12 * airy_noise[index] * air_env)
    return samples


def main() -> None:
    write_wav("choice-tap.wav", choice_tap(), peak_db=-20.0)
    write_wav("resonance-glow.wav", resonance_glow(), peak_db=-18.0)
    write_wav("reason-float-away.wav", reason_float_away(), peak_db=-16.0)


if __name__ == "__main__":
    main()
