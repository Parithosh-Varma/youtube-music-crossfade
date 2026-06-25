from pathlib import Path

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError


def build_crossfade_mix(
    file_paths: list[Path],
    crossfade_ms: int = 5000,
    output_path: str = "crossfade_mix.mp3",
    bitrate: str = "320k",
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

        if combined is None:
            combined = seg
        else:
            combined = combined.append(seg, crossfade=crossfade_ms)

        loaded_count += 1
        if verbose:
            duration = len(seg) / 1000
            print(f"  [{i}/{len(file_paths)}] ✓ {fpath.name}  ({duration:.1f}s)")

    if combined is None:
        raise RuntimeError("No valid audio files could be loaded")

    total = len(combined) / 1000
    if verbose:
        print(f"\nExporting {loaded_count} tracks → {output_path}  ({total:.1f}s total)")

    combined.export(output_path, format="mp3", bitrate=bitrate)
    return Path(output_path)
