import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from .downloader import download_playlist
from .mixer import build_crossfade_mix, load_config, save_config

CONFIG_FILE = "ytcrossfade.json"


def main() -> None:
    config = load_config(CONFIG_FILE)

    parser = argparse.ArgumentParser(
        description="Download a YouTube Music playlist and merge tracks with crossfade.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("url", nargs="?", help="YouTube Music playlist URL")

    out = parser.add_argument_group("output")
    out.add_argument("-o", "--output", default=config.get("output", "crossfade_mix.mp3"),
                     help="Output file path")
    out.add_argument("--bitrate", default=config.get("bitrate", "320k"),
                     choices=["128k", "192k", "256k", "320k"],
                     help="Output MP3 bitrate")
    out.add_argument("--keep-downloads", action="store_true",
                     default=config.get("keep_downloads", False),
                     help="Keep individual downloaded files after mixing")

    audio = parser.add_argument_group("audio processing")
    audio.add_argument("-c", "--crossfade", type=int,
                       default=config.get("crossfade_ms", 5000),
                       help="Crossfade duration in milliseconds")
    audio.add_argument("--no-normalize", action="store_true",
                       help="Disable loudness normalization")
    audio.add_argument("--target-loudness", type=float,
                       default=config.get("target_loudness", -16.0),
                       help="Target loudness in dBFS for normalization")
    audio.add_argument("--linear-crossfade", action="store_true",
                       help="Use linear crossfade instead of equal-power")
    audio.add_argument("--fade-in", type=int,
                       default=config.get("fade_in_ms", 0),
                       help="Fade-in duration at start in milliseconds")
    audio.add_argument("--fade-out", type=int,
                       default=config.get("fade_out_ms", 0),
                       help="Fade-out duration at end in milliseconds")

    dl = parser.add_argument_group("download")
    dl.add_argument("-d", "--download-dir",
                    default=config.get("download_dir", "downloaded_songs"),
                    help="Directory to store downloaded songs")
    dl.add_argument("-f", "--audio-format",
                    default=config.get("audio_format", "mp3"),
                    choices=["mp3", "m4a", "opus", "wav", "flac"],
                    help="Output audio format")
    dl.add_argument("-q", "--quality", type=int,
                    default=config.get("quality", 0),
                    help="Audio quality 0=best to 9=worst")

    general = parser.add_argument_group("general")
    general.add_argument("--quiet", action="store_true",
                         help="Suppress verbose output")
    general.add_argument("--save-config", action="store_true",
                         help="Save current arguments as defaults to ytcrossfade.json")
    general.add_argument("--show-config", action="store_true",
                         help="Show current config and exit")

    args = parser.parse_args()

    if args.show_config:
        if config:
            print(json.dumps(config, indent=2))
        else:
            print("No config file found. Defaults will be used.")
        return

    verbose = not args.quiet

    config_updates = {
        "output": args.output,
        "bitrate": args.bitrate,
        "keep_downloads": args.keep_downloads,
        "crossfade_ms": args.crossfade,
        "target_loudness": args.target_loudness,
        "fade_in_ms": args.fade_in,
        "fade_out_ms": args.fade_out,
        "download_dir": args.download_dir,
        "audio_format": args.audio_format,
        "quality": args.quality,
    }

    if args.save_config:
        config.update(config_updates)
        save_config(config)
        print(f"Config saved to {CONFIG_FILE}")
        return

    if not args.url:
        parser.error("URL is required. Provide a playlist URL or use --save-config first.")

    if verbose:
        print("Downloading playlist...")

    try:
        files = download_playlist(
            url=args.url,
            out_dir=args.download_dir,
            audio_format=args.audio_format,
            quality=args.quality,
            verbose=verbose,
        )
    except RuntimeError as e:
        print(f"Download failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not files:
        print("No files were downloaded. Check the URL and try again.")
        return

    if verbose:
        print(f"\nDownloaded {len(files)} files. Building crossfade mix...")

    try:
        build_crossfade_mix(
            file_paths=files,
            crossfade_ms=args.crossfade,
            output_path=args.output,
            bitrate=args.bitrate,
            normalize=not args.no_normalize,
            target_loudness=args.target_loudness,
            equal_power=not args.linear_crossfade,
            fade_in_ms=args.fade_in,
            fade_out_ms=args.fade_out,
            verbose=verbose,
        )
    except RuntimeError as e:
        print(f"Mix failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not args.keep_downloads:
        shutil.rmtree(args.download_dir, ignore_errors=True)
        if verbose:
            print(f"Cleaned up '{args.download_dir}/'")


if __name__ == "__main__":
    main()
