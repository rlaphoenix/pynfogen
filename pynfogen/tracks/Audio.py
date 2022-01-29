from __future__ import annotations

from pathlib import Path

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
    def title(self) -> str:
        """
        Get track title in it's simplest form.

        If the track title is just the Audio Codec/Channels, it will be replaced with
        the track language. Otherwise, the track title will be used as-is, with the
        track languages appended before it.
        """
        bad_title = not self._x.title or any(str(x) in self._x.title for x in (
            self._x.format,  # Codec (e.g. E-AC-3)
            self._x.format.replace("-", ""),  # Alphanumeric Codec (e.g. EAC3)
            self.codec,  # Simplified Codec (e.g. DD+)
            self.codec.replace("-", "").replace("+", "P"),  # Alphanumeric Simplified Codec (e.g. DDP)
            "Stereo",
            "Surround",
            self.channels,  # Channel Layout Float Representation
        ))

        if bad_title:
            return self.language

        return f"{self.language}, {self._x.title}"
