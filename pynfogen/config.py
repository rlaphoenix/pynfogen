from pathlib import Path

import yaml
from appdirs import user_data_dir


class Directories:
    user = Path(user_data_dir("pynfogen", "PHOENiX"))
    artwork = user / "artwork"
    templates = user / "templates"


class Files:
    config = Directories.user / "config.yml"
    artwork = Directories.artwork / "{name}.nfo"
    template = Directories.templates / "{name}.nfo"
    description = Directories.templates / "{name}.txt"


if Files.config.exists():
    with Files.config.open(encoding="utf8") as f:
        config = yaml.safe_load(f)
else:
    config = {}


__ALL__ = (config, Directories, Files)
