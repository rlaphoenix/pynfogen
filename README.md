# pynfogen

Scriptable MediaInfo-fed NFO Generator for Movies and TV.

## Installation

### Requirements

1. [pip], v19.0 or newer
2. [poetry], latest recommended

### Steps

1. `poetry config virtualenvs.in-project true` (optional)
2. `poetry install`
3. You now have a `.venv` folder in your project root directory. Python and dependencies are installed here.
4. To use the venv, follow [Poetry Docs: Using your virtual environment]

Note: Step 1 is recommended as it creates the virtual environment in one unified location per-project instead of
hidden away somewhere in Poetry's Cache directory.

  [pip]: <https://pip.pypa.io/en/stable/installing>
  [poetry]: <https://python-poetry.org/docs>
  [Poetry Docs: Using your virtual environment]: <https://python-poetry.org/docs/basic-usage/#using-your-virtual-environment>

## Usage

### Requirements

This project uses [VapourSynth] and [pvsfunc] for various functions and purposes.
Make sure to check [pvsfunc's dependencies] as they cannot be installed automatically.

  [VapourSynth]: <https://vapoursynth.com>
  [pvsfunc]: <https://github.com/rlaphoenix/pvsfunc>
  [pvsfunc's dependencies]: <https://github.com/rlaPHOENiX/pvsfunc#dependencies>

### Introduction

Using pynfogen is fairly simple. You have a configuration file ([config.yml](config.yml)) which holds external
information about the file(s) you are feeding to the output NFO, including templates and artwork.

When generating an NFO (by running [pynfogen.py](pynfogen.py)) it reads the primary input file for mediainfo (metadata)
using pymediainfo and use that information in the output NFO wherever the template asks.

- Artwork files (`/art`): Should only contain artwork that goes around the template contents.
  Generally no scripting should be made.
- Template files (`/templates`): These are the main scriptable files. You can make templates for specific scenarios
  like TV, Movies, Episodes, etc. If you are changing a template often, consider putting the changes as a new template
  instead, or perhaps as part of the artwork.
