import argparse
import shutil
from pathlib import Path

from .downloader import download_playlist
from .mixer import build_crossfade_mix


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a YouTube Music playlist and merge tracks with crossfade.",
    )
    parser.add_argument("url", help="YouTube Music playlist URL")
    parser.add_argument(
        "-o", "--output",
        default="crossfade_mix.mp3",
        help="Output file path (default: crossfade_mix.mp3)",
    )
    parser.add_argument(
        "-d", "--download-dir",
        default="downloaded_songs",
        help="Directory to store downloaded songs (default: downloaded_songs)",
    )
    parser.add_argument(
        "-c", "--crossfade",
        type=int,
        default=5000,
        help="Crossfade duration in milliseconds (default: 5000)",
    )
    parser.add_argument(
        "-f", "--audio-format",
        default="mp3",
        choices=["mp3", "m4a", "opus", "wav", "flac"],
        help="Output audio format (default: mp3)",
    )
    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=0,
        help="Audio quality 0=best to 9=worst (default: 0)",
    )
    parser.add_argument(
        "--bitrate",
        default="320k",
        help="Output MP3 bitrate (default: 320k)",
    )
    parser.add_argument(
        "--keep-downloads",
        action="store_true",
        help="Keep individual downloaded files after mixing",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output",
    )

    args = parser.parse_args()

    verbose = not args.quiet

    if verbose:
        print("Downloading playlist...")
    files = download_playlist(
        url=args.url,
        out_dir=args.download_dir,
        audio_format=args.audio_format,
        quality=args.quality,
        verbose=verbose,
    )
    files = [Path(f) for f in files]

    if not files:
        print("No files were downloaded. Check the URL and try again.")
        return

    if verbose:
        print(f"\nDownloaded {len(files)} files. Building crossfade mix...")

    build_crossfade_mix(
        file_paths=files,
        crossfade_ms=args.crossfade,
        output_path=args.output,
        bitrate=args.bitrate,
        verbose=verbose,
    )

    if not args.keep_downloads:
        shutil.rmtree(args.download_dir, ignore_errors=True)
        if verbose:
            print(f"Cleaned up '{args.download_dir}/'")


if __name__ == "__main__":
    main()
