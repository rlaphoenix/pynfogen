from __future__ import annotations

from pathlib import Path

import pymediainfo
from pyd2v import D2V

from pynfogen.tracks.BaseTrack import BaseTrack


class Video(BaseTrack):
    DYNAMIC_RANGE_MAP = {
        "SMPTE ST 2086": "HDR10",
        "HDR10": "HDR10",
        "SMPTE ST 2094 App 4": "HDR10+",
        "HDR10+": "HDR10+",
        "Dolby Vision": "DV"
    }

    def __init__(self, track: pymediainfo.Track, path: Path):
        super().__init__(track, path)
        # quick shorthands
        self.profile = self._x.format_profile
        self.dar = self._x.other_display_aspect_ratio[0]
        if self._x.framerate_num:
            self.fps = f"{self._x.framerate_num}/{self._x.framerate_den}"
        else:
            self.fps = self._x.frame_rate

    @property
    def codec(self) -> str:
        """
        Get video codec in common P2P simplified form.
        E.g., 'MPEG-2' instead of 'MPEG Video, Version 2'.
        """
        return {
            "MPEG Video": f"MPEG-{(self._x.format_version or '').replace('Version ', '')}"
        }.get(self._x.format, self._x.format)

    @property
    def range(self) -> str:
        """
        Get video range as typical shortname.
        Returns multiple ranges in space-separated format if a fallback range is
        available. E.g., 'DV HDR10'.
        """
        if self._x.hdr_format:
            return " ".join([
                self.DYNAMIC_RANGE_MAP.get(x)
                for x in self._x.hdr_format.split(" / ")
            ])
        elif "HLG" in ((self._x.transfer_characteristics or ""), (self._x.transfer_characteristics_original or "")):
            return "HLG"
        return "SDR"

    @property
    def scan(self) -> str:
        """
        Get video scan type in string form.
        Will accurately check using DGIndex if codec is MPEG-1/2.

        Examples:
            'Interlaced'
            'Progressive'
            When there's information on scan type percentages:
            'Interlaced (CST)'
            'Progressive (CST)'
            '99.78% Progressive (VST)'
            '0.01% Interlaced (VST)'
        """
        scan_type = self._x.scan_type
        if not scan_type:
            # some videos may not state scan, presume progressive
            scan_type = "Progressive"

        if self.codec in ["MPEG-1", "MPEG-2"]:
            d2v = D2V.load(self._path)
            for ext in ("log", "d2v", "mpg", "mpeg"):
                d2v.path.with_suffix(f".{ext}").unlink(missing_ok=True)

            flags = [
                dict(**flag, vob=d["vob"], cell=d["cell"])
                for d in d2v.data
                for flag in d["flags"]
            ]
            progressive_frames = sum(f["progressive_frame"] for f in flags)
            progressive_percent = (progressive_frames / len(flags)) * 100
            is_constant = progressive_percent in (0.0, 100.0)

            scan_type = ["Interlaced", "Progressive"][progressive_percent >= 50.0]
            scan_type += f" ({['VST', 'CST'][is_constant]})"
            if not is_constant:
                scan_type = f"{progressive_percent:.2f}% {scan_type}"

        return scan_type
