import html
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import langcodes
import requests
from langcodes import Language
from pyd2v import D2V
from pymediainfo import MediaInfo, Track
from tldextract import tldextract

from pynfogen.formatter import CustomFormats


class NFO:
    AUDIO_CHANNEL_LAYOUT_WEIGHT = {
        "LFE": 0.1
    }
    DYNAMIC_RANGE_MAP = {
        "SMPTE ST 2086": "HDR10",
        "HDR10": "HDR10",
        "SMPTE ST 2094 App 4": "HDR10+",
        "HDR10+": "HDR10+",
        "Dolby Vision": "DV"
    }

    IMDB_ID_T = re.compile(r"^tt\d{7,8}$")
    TMDB_ID_T = re.compile(r"^(tv|movie)/\d+$")
    TVDB_ID_T = re.compile(r"^\d+$")

    def __init__(self, file: Path, **config: Any) -> None:
        self.session = self.get_session()

        self.file = file
        self.media_info = MediaInfo.parse(self.file)

        self.fanart_api_key: str = config.get("fanart_api_key")
        self.source: str = config.get("source")
        self.note: str = config.get("note")
        self.preview: str = config.get("preview")

        self.season: Union[int, str] = config.get("season")
        self.episode, self.episode_name = config.get("episode") or (None, None)
        self.episodes: int = self.get_episode_count()
        self.release_name = self.get_release_name()

        self.videos = self.media_info.video_tracks
        self.audio = self.media_info.audio_tracks
        self.subtitles = self.media_info.text_tracks

        chapters = next(iter(self.media_info.menu_tracks), None)
        if chapters:
            self.chapters = {
                ".".join([k.replace("_", ".")[:-3], k[-3:]]): v.strip(":")
                for k, v in chapters.to_data().items()
                if f"1{k.replace('_', '')}".isdigit()
            }
            self.chapters_numbered = all(
                x.split(":", 1)[-1].lower() in [f"chapter {i + 1}", f"chapter {str(i + 1).zfill(2)}"]
                for i, x in enumerate(self.chapters.values())
            )
        else:
            self.chapters = {}
            self.chapters_numbered = False

        self.imdb = config.get("imdb")
        if not self.imdb:
            self.imdb = self.media_info.general_tracks[0].to_data().get("imdb")
        if not self.imdb:
            raise ValueError("An IMDB ID is required, but none were provided.")
        if not self.IMDB_ID_T.match(self.imdb):
            raise ValueError(
                f"The provided IMDB ID `{self.imdb!r}` is not valid. "
                f"Expected e.g., 'tt0487831', 'tt10810424', (i.e., include the 'tt')."
            )

        self.tmdb = config.get("tmdb")
        if not self.tmdb:
            self.tmdb = self.media_info.general_tracks[0].to_data().get("tmdb")
        if self.tmdb and not self.TMDB_ID_T.match(self.tmdb):
            raise ValueError(
                f"The provided TMDB ID {self.tmdb!r} is not valid. "
                f"Expected e.g., 'tv/2490', 'movie/14836', (i.e., include the 'tv/' or 'movie/')."
            )

        self.tvdb = config.get("tvdb")
        if not self.tvdb:
            self.tvdb = self.media_info.general_tracks[0].to_data().get("tvdb")
        if self.tvdb and not self.TVDB_ID_T.match(str(self.tvdb)):
            raise ValueError(
                f"The provided TVDB ID {self.tvdb!r} is not valid. "
                f"Expected e.g., '79216', '1395', (not the url slug e.g., 'the-office-us')."
            )

        self.title_name, self.title_year = self.get_title_name_year()

        if self.tvdb and self.fanart_api_key:
            self.banner_image = self.get_banner_image(self.tvdb)
        else:
            self.banner_image = None

        if self.preview:
            self.preview_images = self.get_preview_images(self.preview)
        else:
            self.preview_images = []

        if any(not x.language or x.language == "und" for x in self.audio + self.subtitles):
            print(
                "One or more Audio and/or Subtitle track has no Language specified.\n"
                "All Audio and Subtitle tracks require a language to be set."
            )
            sys.exit(1)

    def __repr__(self) -> str:
        return "<{c} {attrs}>".format(
            c=self.__class__.__name__,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    def run(self, template: str, art: Optional[str] = None, **kwargs: Any) -> str:
        """
        Evaluate and apply formatting on template, apply any art if provided.
        Any additional parameters are passed as extra variables to the template.
        The extra variables have priority when there's conflicting variable names.
        """
        variables = self.__dict__
        variables.update(kwargs)

        template = CustomFormats().format(template, **variables)
        if art:
            art = art.format(nfo=template)
            template = art

        for m in re.finditer(r"<\?([01])\?([\D\d]*?)\?>", template):
            # TODO: This if check is quite yucky, look into alternative options.
            #       Ideally a custom format spec would be great.
            template = template.replace(
                m.group(0),
                m.group(2) if int(m.group(1)) else ""
            )

        template = "\n".join(map(str.rstrip, template.splitlines(keepends=False)))

        return template

    def get_title_name_year(self) -> Tuple[str, str]:
        """Scrape Title Name and Year (including e.g. 2019-) from IMDB"""
        r = self.session.get(f"https://www.imdb.com/title/{self.imdb}")
        if r.status_code != 200:
            raise ValueError(f"An unexpected error occurred getting IMDB Title Page [{r.status_code}]")
        imdb_page = html.unescape(r.text)
        imdb_title = re.search(
            # testing ground: https://regex101.com/r/bEoEDn/1
            r"<title>(?P<name>.+) \(((?P<type>TV (Movie|Series|Mini[- ]Series|Short|Episode) |Video |Short |)"
            r"(?P<year>(\d{4})(|– |–\d{4})))\) - IMDb</title>",
            imdb_page
        )
        if not imdb_title:
            raise ValueError(f"Could not scrape Movie Title or Year for {self.imdb}...")
        return imdb_title.group("name").strip(), imdb_title.group("year").strip()

    def get_episode_count(self) -> int:
        """Count episodes based on neighbouring same-extension files."""
        return sum(1 for _ in self.file.parent.glob(f"*{self.file.suffix}"))

    def get_release_name(self) -> str:
        """
        Retrieve the release name based on the file used during MediaInfo.
        If a season was specified, but an episode number was not, it presumes the release is a Pack.
        Hence when pack, it uses the parent folder's name as the release name.
        """
        if self.season is not None and self.episode is None:
            return self.file.parent.name
        return self.file.stem

    def get_banner_image(self, tvdb_id: int) -> Optional[str]:
        """
        Get a wide banner image from fanart.tv.
        It will only return banners in the same language as the first audio track.
        """
        if not tvdb_id:
            return None
        if not self.fanart_api_key:
            raise ValueError("Need Fanart.tv api key for TV titles!")

        r = self.session.get(f"http://webservice.fanart.tv/v3/tv/{tvdb_id}?api_key={self.fanart_api_key}")
        if r.status_code == 404:
            return None
        res = r.json()

        error = res.get("error message")
        if error:
            if error == "Not found":
                return None
            raise ValueError(f"An unexpected error occurred while calling Fanart.tv, {res}")

        url = next((
            x["url"]
            for x in res.get("tvbanner") or []
            if langcodes.closest_supported_match(
                x["lang"],
                sorted(self.audio, key=lambda x: x.streamorder)[0].language,
                max_distance=5
            )
        ), None)

        return url

    def get_preview_images(self, url: str) -> List[Dict[str, str]]:
        if not url:
            return []

        domain = tldextract.extract(url).registered_domain
        supported_domains = ["imgbox.com", "beyondhd.co"]
        if domain not in supported_domains:
            return []

        images = []
        page = self.session.get(url).text
        if domain == "imgbox.com":
            for m in re.finditer('src="(https://thumbs2.imgbox.com.+/)(\\w+)_b.([^"]+)', page):
                images.append({
                    "url": f"https://imgbox.com/{m.group(2)}",
                    "src": f"{m.group(1)}{m.group(2)}_t.{m.group(3)}"
                })
        if domain == "beyondhd.co":
            for m in re.finditer('/image/([^"]+)"\\D+src="(https://.*beyondhd.co/images.+/(\\w+).md.[^"]+)', page):
                images.append({
                    "url": f"https://beyondhd.co/image/{m.group(1)}",
                    "src": m.group(2)
                })

        return images

    def get_video_print(self, videos: List[Track]) -> List[List[str]]:
        if not videos:
            return [["--"]]
        data = []
        for video in videos:
            codec = {
                "MPEG Video": f"MPEG-{(video.format_version or '').replace('Version ', '')}"
            }.get(video.format, video.format)
            scan_overview = video.scan_type
            vst = False
            if codec in ["MPEG-1", "MPEG-2"]:
                # parse d2v file with pyd2v, generates D2V if needed
                d2v = D2V.load(Path(self.file))
                self.file = d2v.path
                # get every frames' flag data, this contains information on displaying frames
                # add vob and cell number to each frames flag data as well
                flags = [f for line in [
                    [dict(**y, vob=x["vob"], cell=x["cell"]) for y in x["flags"]] for x in d2v.data
                ] for f in line]
                interlaced_percent = (sum(1 for f in flags if not f["progressive_frame"]) / len(flags)) * 100
                if interlaced_percent == 100:
                    scan_overview = "Interlaced (CST)"
                else:
                    scan_overview = f"{round(interlaced_percent, 2)}% Interlaced (VST)"
                    vst = True
                for ext in ["log", "d2v", "mpg", "mpeg"]:
                    fp = os.path.splitext(self.file)[0] + "." + ext
                    if os.path.exists(fp):
                        os.unlink(fp)

            if video.hdr_format:
                range_ = " ".join([self.DYNAMIC_RANGE_MAP.get(x) for x in video.hdr_format.split(" / ")])
            elif "HLG" in ((video.transfer_characteristics or ""), (video.transfer_characteristics_original or "")):
                range_ = "HLG"
            else:
                range_ = "SDR"

            if video.language and video.language != "und":
                language = Language.get(video.language).display_name()
            else:
                language = None

            line_1 = CustomFormats().format(
                "- <?{language:true}?{language}, ?>{codec} ({profile}) {width}x{height} ({aspect}) @ {bitrate}",
                language=language,
                codec=codec,
                profile=video.format_profile,
                width=video.width, height=video.height,
                aspect=video.other_display_aspect_ratio[0],
                bitrate=f"{video.other_bit_rate[0]}{f' ({video.bit_rate_mode})' if video.bit_rate_mode else ''}"
            )

            line_2 = CustomFormats().format(
                "  {fps} FPS ({fps_mode}), {color_space}{subsampling}P{bit_depth}, {range}, {scan}",
                fps=f"{video.framerate_num}/{video.framerate_den}" if video.framerate_num else video.frame_rate,
                fps_mode="VFR" if vst else video.frame_rate_mode,
                color_space=video.color_space,
                subsampling=video.chroma_subsampling.replace(":", ""),
                bit_depth=video.bit_depth,
                range=range_,
                scan=scan_overview
            )

            data.append([line_1, line_2])
        return data

    def get_audio_print(self, audio: List[Track]) -> List[str]:
        if not audio:
            return ["--"]
        data = []
        for t in audio:
            if t.title and "Commentary" in t.title:
                title = t.title
            else:
                title = Language.get(t.language).display_name()
            if t.channel_layout:
                channels = float(sum(self.AUDIO_CHANNEL_LAYOUT_WEIGHT.get(x, 1) for x in t.channel_layout.split(" ")))
            else:
                channels = float(t.channel_s)
            bit_rate_mode = f" ({t.bit_rate_mode})" if t.bit_rate_mode else ""
            l1 = f"- {title}, {t.format} {channels} @ {t.other_bit_rate[0]}{bit_rate_mode}"
            data += [("  " + x if i > 0 else x) for i, x in enumerate(textwrap.wrap(l1, 64))]
        return data

    @staticmethod
    def get_subtitle_print(subs: List[Track]) -> List[str]:
        """
        Return a list of a brief subtitle overview per-subtitle.

        e.g.
        - English, Forced, SubRip (SRT)
        - English, SubRip (SRT)
        - English, SDH, SubRip (SRT)
        - Spanish, Latin American (SDH), SubRip (SRT)

        The bit of text between the Language and the Subtitle format is the Track Title.
        It can be of any format, but it is recommended to be used as shown above.

        It will be returned as a list of strings with the `- ` already pre-pended to each entry.
        """
        data = []
        if not subs:
            data.append("--")
        for sub in subs:
            line_items = []

            # following sub.title tree checks and supports three different language and title scenarios
            # The second scenario is the recommended option to choose if you are open to choosing any
            # The third scenario should be used if you have nothing unique to state about the track
            # | Language     | Track Title                   | Output                                        |
            # | ------------ | ----------------------------- | --------------------------------------------- |
            # | es / Spanish | Spanish (Latin American, SDH) | - Spanish (Latin American, SDH), SubRip (SRT) |
            # | es / Spanish | Latin American (SDH)          | - Spanish, Latin American (SDH), SubRip (SRT) |
            # | es / Spanish | None                          | - Spanish, SubRip (SRT)                       |
            language = Language.get(sub.language).display_name()
            if sub.title:
                if language.lower() in sub.title.lower():
                    line_items.append(sub.title)
                else:
                    line_items.append(f"{language}, {sub.title}")
            else:
                line_items.append(language)

            line_items.append(sub.format.replace("UTF-8", "SubRip (SRT)"))

            line = "- " + ", ".join(line_items)
            data += [
                ("  " + x if i > 0 else x)
                for i, x in enumerate(textwrap.wrap(line, 64))
            ]
        return data

    @staticmethod
    def get_chapter_print(chapters: Dict[str, str]) -> List[str]:
        if not chapters:
            return ["--"]
        return [
            f"- {k}: {v}"
            for k, v in chapters.items()
        ]

    def get_chapter_print_short(self, chapters: Dict[str, str]) -> str:
        if not chapters:
            return "No"
        if self.chapters_numbered:
            return f"Yes (Numbered 01-{str(len(chapters)).zfill(2)})"
        return "Yes (Named)"

    @staticmethod
    def get_session() -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0",
            "Accept-Language": "en-US,en;q=0.5"
        })
        return session
