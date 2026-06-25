import os
import subprocess
import shutil
from pathlib import Path


def check_deps() -> None:
    missing = []
    for cmd in ["yt-dlp", "ffmpeg"]:
        if not shutil.which(cmd):
            missing.append(cmd)
    if missing:
        msg = "Missing required dependencies: " + ", ".join(missing)
        raise RuntimeError(msg)


def download_playlist(
    url: str,
    out_dir: str = "downloaded_songs",
    audio_format: str = "mp3",
    quality: int = 0,
    verbose: bool = True,
) -> list[str]:
    check_deps()
    os.makedirs(out_dir, exist_ok=True)

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", audio_format,
        "--audio-quality", str(quality),
        "--embed-thumbnail",
        "--add-metadata",
        "--output", f"{out_dir}/%(title)s.%(ext)s",
        "--no-playlist-reverse",
        "--yes-playlist",
        url,
    ]

    if not verbose:
        cmd.extend(["--quiet", "--no-warnings"])

    result = subprocess.run(cmd, capture_output=not verbose, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed:\n{result.stderr}")

    pattern = f"{out_dir}/*.{audio_format}"
    return sorted(Path(out_dir).glob(f"*.{audio_format}"))
