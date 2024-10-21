from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

import pymediainfo
from langcodes import Language


class BaseTrack:
    """Track to aide in overriding properties of a PyMediaInfo Track instance."""
    def __init__(self, track: pymediainfo.Track, path: Path):
        self._x = track
        self._path = path
        # common shorthands
        self.bitrate = self._x.other_bit_rate[0] if self._x.track_type != "Text" else None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._x, name)

    @property
    def all_properties(self) -> defaultdict[str, Any]:
        """Get all non-callable attributes from this and it's sub-track object."""
        props = defaultdict(lambda: None)

        for obj in (self, self._x):
            for k, v in obj.__dict__.items():
                if k in ("_x", "_path"):
                    continue
                props[k] = v

        for subclass in (BaseTrack, self.__class__):
            for k, v in vars(subclass).items():
                if not isinstance(v, property):
                    continue
                if k in ("all_properties",):
                    continue
                props[k] = getattr(self, k)

        return props

    @property
    def language(self) -> Optional[str]:
        """
        Override MediaInfo language with English Display Name.
        Returns None if no language is specified.
        """
        if self._x.language and self._x.language != "und":
            return Language.get(self._x.language).display_name("en")
        return None
