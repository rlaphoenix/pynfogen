from __future__ import annotations

from pathlib import Path
from typing import Optional

import pymediainfo

from pynfogen.tracks.BaseTrack import BaseTrack


class Audio(BaseTrack):
    AUDIO_CHANNEL_LAYOUT_WEIGHT = {
        "LFE": 0.1
    }

    def __init__(self, track: pymediainfo.Track, path: Path):
        super().__init__(track, path)

    @property
    def codec(self) -> str:
        """
        Get track codec in common P2P simplified form.
        E.g., 'DD+' instead of 'E-AC-3'.
        """
        return {
            "E-AC-3": "DD+",
            "AC-3": "DD"
        }.get(self._x.format, self._x.format)

    @property
    def channels(self) -> float:
        """Get track channels as channel layout representation."""
        if self._x.channel_layout:
            return float(sum(
                self.AUDIO_CHANNEL_LAYOUT_WEIGHT.get(x, 1)
                for x in self._x.channel_layout.split(" ")
            ))
        return float(self._x.channel_s)

    @property
    def title(self) -> Optional[str]:
        """
        Get track title in it's simplest form.
        Returns None if the title is just stating the Language, Audio Codec, or Channels.
        """
        if not self._x.title or any(str(x) in self._x.title.lower() for x in (
            self.language.lower(),  # Language Display Name (e.g. Spanish)
            self._x.language.lower(),  # Language Code (e.g. und, or es)
            self._x.format.lower(),  # Codec (e.g. E-AC-3)
            self._x.format.replace("-", "").lower(),  # Alphanumeric Codec (e.g. EAC3)
            self.codec.lower(),  # Simplified Codec (e.g. DD+)
            self.codec.replace("-", "").replace("+", "P").lower(),  # Alphanumeric Simplified Codec (e.g. DDP)
            "stereo",
            "surround",
            self.channels,  # Channel Layout Float Representation
        )):
            return None

        return self._x.title
