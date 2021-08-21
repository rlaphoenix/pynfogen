import os
import platform
import subprocess


def open_file(path: str) -> None:
    """Open file in file-associated text-editor."""
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.run(("open", path), check=True)
    else:
        # TODO: What about systems that do not use a WM/GUI?
        subprocess.run(("xdg-open", path), check=True)
