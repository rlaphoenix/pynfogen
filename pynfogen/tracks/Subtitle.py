from __future__ import annotations

from pathlib import Path

import pymediainfo

from pynfogen.tracks.BaseTrack import BaseTrack


class Subtitle(BaseTrack):
    def __init__(self, track: pymediainfo.Track, path: Path):
        super().__init__(track, path)

    @property
    def codec(self) -> str:
        """
        Get track codec in common P2P simplified form.
        E.g., 'SubRip (SRT)' instead of 'UTF-8'.
        """
        return {
            "UTF-8": "SubRip (SRT)",
        }.get(self._x.format, self._x.format)

    @property
    def title(self) -> str:
        """
        Get track title in it's simplest form.

        Supports the following different language and title scenarios.
        The third scenario is the recommended option to choose if you are open to choosing any,
        but the fourth scenario should be used if you have nothing unique to state about the track.

        | Language     | Track Title                   | Output                        |
        | ------------ | ----------------------------- | ----------------------------- |
        | es / Spanish | Spanish                       | Spanish                       |
        | es / Spanish | Spanish (Latin American, SDH) | Spanish (Latin American, SDH) |
        | es / Spanish | Latin American (SDH)          | Spanish, Latin American (SDH) |
        | es / Spanish | None                          | Spanish                       |
        """
        # TODO: Exclude Language from all Title scenarios.
        #       Only return the title/tags.
        if not self._x.title:
            return self.language
        if not self.language:
            return self._x.title
        if self.language.lower() in self._x.title.lower():
            return self._x.title
        return f"{self.language}, {self._x.title}"
