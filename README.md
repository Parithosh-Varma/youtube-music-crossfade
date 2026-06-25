# ytcrossfade

Download a YouTube Music playlist and merge all tracks into a single MP3 with seamless crossfades.

## Installation

```bash
pip install -r requirements.txt
```

Requires **ffmpeg** on your PATH ([ffmpeg.org](https://ffmpeg.org)).

## Usage

```bash
# Basic
python -m ytcrossfade.cli "https://music.youtube.com/playlist?list=..."

# Custom crossfade (3 seconds)
python -m ytcrossfade.cli "URL" --crossfade 3000

# Custom output file
python -m ytcrossfade.cli "URL" --output my_mix.mp3

# Keep individual song files after mixing
python -m ytcrossfade.cli "URL" --keep-downloads

# Quiet mode
python -m ytcrossfade.cli "URL" --quiet
```

Or install the package and use the `ytcrossfade` command:

```bash
pip install -e .
ytcrossfade "URL"
```

## Jupyter Notebook

A step-by-step notebook is available at `notebook/youtube_music_crossfade.ipynb` for interactive use in Colab or Jupyter.

## How it works

1. **yt-dlp** downloads each track as MP3 with thumbnails and metadata
2. **pydub** loads each file and concatenates them with an overlapping crossfade
3. The final mix is exported as a single MP3 file
