from pathlib import Path
from unittest.mock import patch

import pytest

from ytcrossfade.mixer import build_crossfade_mix


def test_raises_on_empty_file_list():
    with pytest.raises(ValueError, match="No audio files provided"):
        build_crossfade_mix([], verbose=False)


@patch("ytcrossfade.mixer.AudioSegment")
def test_returns_path(mock_segment):
    mock_segment.from_file.return_value = mock_segment
    mock_segment.__len__.return_value = 10_000
    mock_segment.__getitem__.return_value = mock_segment
    mock_segment.__add__.return_value = mock_segment
    mock_segment.append.return_value = mock_segment
    mock_segment.fade_out.return_value = mock_segment
    mock_segment.fade_in.return_value = mock_segment
    mock_segment.overlay.return_value = mock_segment

    files = [Path("a.mp3"), Path("b.mp3")]
    result = build_crossfade_mix(files, normalize=False, verbose=False)

    assert result.suffix == ".mp3"
    mock_segment.export.assert_called_once()
