from pathlib import Path

import toml
from appdirs import user_data_dir


class Directories:
    user = Path(user_data_dir("pynfogen", "PHOENiX"))
    artwork = user / "artwork"
    templates = user / "templates"


class Files:
    config = Directories.user / "config.toml"
    artwork = Directories.artwork / "{name}.nfo"
    template = Directories.templates / "{name}.nfo"
    description = Directories.templates / "{name}.txt"


if Files.config.exists():
    config = toml.load(Files.config)
else:
    config = {}


__ALL__ = (config, Directories, Files)
