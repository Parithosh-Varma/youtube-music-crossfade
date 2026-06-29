# ytcrossfade

Download a YouTube Music playlist and merge all tracks into a single MP3 with seamless crossfades, loudness normalization, and configurable fade curves.

## Features

- Downloads entire YouTube Music playlists via yt-dlp
- **Loudness normalization** — all tracks leveled to the same perceived volume (EBU R128 style, target -16 dBFS by default)
- **Equal-power crossfade** — smoother transitions than linear, or use linear if preferred
- **Config file** (`ytcrossfade.json`) — save your preferred settings so you don't need CLI flags every time
- **Fade-in / fade-out** — optional intro/outro fades on the final mix
- **Graceful error recovery** — corrupt or unreadable tracks are skipped without aborting

## Installation

```bash
pip install -r requirements.txt
```

Requires **ffmpeg** on your PATH ([ffmpeg.org](https://ffmpeg.org)).

## Usage

```bash
# Basic — download and mix with defaults
python -m ytcrossfade.cli "https://music.youtube.com/playlist?list=..."

# Custom crossfade (3 seconds), fade in/out, no normalization
python -m ytcrossfade.cli "URL" --crossfade 3000 --fade-in 2000 --fade-out 5000 --no-normalize

# Save your preferences as defaults
python -m ytcrossfade.cli --save-config --crossfade 3000 --fade-in 2000

# Then subsequent runs just need the URL
python -m ytcrossfade.cli "URL"
```

Or install the package and use the `ytcrossfade` command:

```bash
pip install -e .
ytcrossfade "URL"
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-o --output` | `crossfade_mix.mp3` | Output file path |
| `--bitrate` | `320k` | Output MP3 bitrate |
| `-c --crossfade` | `5000` | Crossfade duration in ms |
| `--no-normalize` | `false` | Disable loudness normalization |
| `--target-loudness` | `-16.0` | Target loudness in dBFS |
| `--linear-crossfade` | `false` | Use linear (not equal-power) crossfade |
| `--fade-in` | `0` | Fade-in at start in ms |
| `--fade-out` | `0` | Fade-out at end in ms |
| `--keep-downloads` | `false` | Keep individual MP3s after mixing |
| `--save-config` | — | Save current args as defaults |
| `--show-config` | — | Display current saved config |

## Jupyter Notebook

A step-by-step notebook is available at `notebook/youtube_music_crossfade.ipynb` for use in Colab or Jupyter.

## How it works

1. **yt-dlp** downloads each track as MP3 with metadata
2. **pydub** loads each file and applies loudness normalization (optional)
3. Tracks are concatenated with an **equal-power** or **linear** crossfade
4. Optional fade-in / fade-out applied to the final mix
5. Exported as a single high-bitrate MP3
