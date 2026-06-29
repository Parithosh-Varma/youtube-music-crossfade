import json
import math
from pathlib import Path

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

TARGET_RMS = -16.0

def _rms(target: float) -> float:
    return 10 ** (target / 20.0)

def normalize_loudness(seg: AudioSegment, target_rms: float = TARGET_RMS) -> AudioSegment:
    if seg.rms <= 0:
        return seg
    gain = target_rms - seg.dBFS
    return seg.apply_gain(gain)

def _equal_power_crossfade(a: AudioSegment, b: AudioSegment, duration_ms: int) -> AudioSegment:
    fade_out = a[-duration_ms:].fade_out(duration_ms)
    fade_in = b[:duration_ms].fade_in(duration_ms)
    crossfaded = fade_out.overlay(fade_in)
    return a[:-duration_ms] + crossfaded + b[duration_ms:]

def build_crossfade_mix(
    file_paths: list[Path],
    crossfade_ms: int = 5000,
    output_path: str = "crossfade_mix.mp3",
    bitrate: str = "320k",
    normalize: bool = True,
    target_loudness: float = TARGET_RMS,
    equal_power: bool = True,
    fade_in_ms: int = 0,
    fade_out_ms: int = 0,
    verbose: bool = True,
) -> Path:
    if not file_paths:
        raise ValueError("No audio files provided")

    combined: AudioSegment | None = None
    loaded_count = 0

    for i, fpath in enumerate(file_paths, 1):
        try:
            seg = AudioSegment.from_file(str(fpath))
        except (CouldntDecodeError, Exception) as e:
            if verbose:
                print(f"  [{i}/{len(file_paths)}] SKIP: {fpath.name} — {e}")
            continue

        if normalize:
            seg = normalize_loudness(seg, target_loudness)

        if combined is None:
            combined = seg
        else:
            if equal_power:
                combined = _equal_power_crossfade(combined, seg, crossfade_ms)
            else:
                combined = combined.append(seg, crossfade=crossfade_ms)

        loaded_count += 1
        if verbose:
            dur = len(seg) / 1000
            level = f"{seg.dBFS:.1f} dBFS" if normalize and seg.rms > 0 else ""
            print(f"  [{i}/{len(file_paths)}] ✓ {fpath.name}  ({dur:.1f}s) {level}")

    if combined is None:
        raise RuntimeError("No valid audio files could be loaded")

    if fade_in_ms:
        combined = combined.fade_in(fade_in_ms)
    if fade_out_ms:
        combined = combined.fade_out(fade_out_ms)

    total = len(combined) / 1000
    if verbose:
        print(f"\nExporting {loaded_count} tracks → {output_path}  ({total:.1f}s total)")
        print(f"Settings: normalize={normalize}, crossfade={crossfade_ms}ms, "
              f"equal_power={equal_power}, fade_in={fade_in_ms}ms, fade_out={fade_out_ms}ms")

    combined.export(output_path, format="mp3", bitrate=bitrate)
    return Path(output_path)


def load_config(config_path: str = "ytcrossfade.json") -> dict:
    path = Path(config_path)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_config(config: dict, config_path: str = "ytcrossfade.json") -> None:
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
