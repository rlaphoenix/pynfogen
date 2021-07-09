# pynfogen

[![License](https://img.shields.io/github/license/rlaphoenix/pynfogen)](https://github.com/rlaphoenix/pynfogen/blob/master/LICENSE)
[![Python version tests](https://img.shields.io/github/workflow/status/rlaphoenix/pynfogen/Build)](https://github.com/rlaphoenix/pynfogen/releases)
[![Python versions](https://img.shields.io/pypi/pyversions/pynfogen)](https://pypi.python.org/pypi/pynfogen)
[![PyPI version](https://img.shields.io/pypi/v/pynfogen)](https://pypi.python.org/pypi/pynfogen)
[![GitHub issues](https://img.shields.io/github/issues/rlaphoenix/pynfogen)](https://github.com/rlaphoenix/pynfogen/issues)
[![DeepSource issues](https://deepsource.io/gh/rlaphoenix/pynfogen.svg/?label=active+issues)](https://deepsource.io/gh/rlaphoenix/pynfogen)

Scriptable MediaInfo-fed NFO Generator for Movies and TV.

## Installation

    pip install --user pynfogen

### Or, Install from Source

#### Requirements

1. [pip], v19.0 or newer
2. [poetry], latest recommended

#### Steps

1. `poetry config virtualenvs.in-project true` (optional, but recommended)
2. `poetry install`
3. You now have a `.venv` folder in your project root directory. Python and dependencies are installed here.
4. To use the venv, follow [Poetry Docs: Using your virtual environment]

Note: Step 1 is recommended as it creates the virtual environment in one unified location per-project instead of
hidden away somewhere in Poetry's Cache directory.

  [pip]: <https://pip.pypa.io/en/stable/installing>
  [poetry]: <https://python-poetry.org/docs>
  [Poetry Docs: Using your virtual environment]: <https://python-poetry.org/docs/basic-usage/#using-your-virtual-environment>

## Usage

### Introduction

Using pynfogen is fairly simple. You have a configuration file ([config.yml](config.yml)) which holds external
information about the file(s) you are feeding to the output NFO, including templates and artwork.

When generating an NFO (by running [pynfogen.py](pynfogen.py)) it reads the primary input file for mediainfo (metadata)
using pymediainfo and use that information in the output NFO wherever the template asks.

- Artwork files ([/art](/art)): Should only contain artwork that goes around the template contents.
  Generally no scripting should be made.
- Template files ([/templates](/templates)): These are the main scriptable files. You can make templates for specific
  scenarios like TV, Movies, Episodes, etc. If you are changing a template often, consider putting the changes as a new
  template instead, or perhaps as part of the artwork.

### Copyright Agreement for included Artwork and Template files

There's already example template files and artwork files for you to look at.
However, the Artwork files are copyright to whomever committed them where-as the templates are not copyright.
The copyrighted files may not be used, even under the conditions of the License, except for viewing as examples.
No derivative work is permitted based on their general concept.
Simply remember that artwork files are themselves pieces of Art, and should be treated as such.

### Text-encoding

Traditional NFOs expect to use the codepage 437 (cp437) "ascii" text-encoding.
pynfogen generally doesn't care what you use, but may not respect you're choice correctly in the NFO output.
It has not been set up for specific text-encoding choice and generally speaking UTF-8 is expected.

### Scripting

The scripting system used by pynfogen is by no means ideal. It is however, consistent.
It's mostly a mix of python's normal new-style string formatting, with custom formatters.
It also uses a PHP-like `<?{x:y}..?>` custom syntax for if statements.

#### If statement

For example the following will check if the `{note}` variable (python new-style formatting) is a truthy value,
and only if so, print it:

    # note = "Hello World!"
    <?{note:true}Has note: {note}?>
    # returns: `Has note: Hello World!`

    # note = ""  # or None, 0, False, 1==2, e.t.c
    <?{note:true}Has note: {note}?>
    # returns: ``

It's obvious this is in no way good syntax for `if` statements (no `else` or `elif` support either), but it works.

It uses `1` and `0` in the `<?{here}?...>` section to determine if it should print or not.
Essentially speaking any time the If statement is used, you should be using the [Boolean custom formatter](#boolean).

#### Custom Formatting

The following custom additional formatting to pythons new-style formatting is available:

##### Chaining

Example: `{var:bbimg:layout,2x2x0}`

Using `:` you can chain formatter results from left to right, passing previous value as it goes on.
The previous value does not necessarily need to be used.

For less confusion, since `:` is already used as standard in new-string formatting, look at the above example as
`{(var:bbimg):(layout,2x2x0)}`

##### Boolean

Example: `{var:true}` or `{var:!false}`.  
Type-hint: func(var: Any) -> Fixed\[1, 0]

Returns `1` if `var` is a truthy value, otherwise `0`.

There's also `{var:false}` and `{var:!true}` which is the flip-reverse of the above result.

##### BBCode Image Links

Example: `{var:bbimg}`  
Type-hint: bbimg(var: Union\[List\[dict], dict]) -> Union\[List\[str], str]  
Each dictionary: e.g. `{url: 'https://url/to/image/page', src: 'https://url/to/image/src.png'}`

Every dictionary is converted to BBCode `[IMG]` wrapped in `[URL]`. For example:
`[URL=https://url/to/image/page][IMG]https://url/to/image/src.png[/IMG][/URL]`

Returns a list of converted bbcode strings, or a single string if only one dictionary was provided.

##### Layout

Example: `{var:layout,3x2x1}`  
Type-hint: layout(var: Union\[List\[Any], Any], width: int, height: int, spacing: int) -> str

Lays out items in a grid-like layout, spacing out items using spaces (or new lines) as specified.
New-lines are used when spacing vertically.

##### Wrapping

Example: `{var:>>2x68}`  
Type-hint: wrap(var: Any, indent: int, wrap: int)

Text-wrap to a specific length. Each subsequent new-line caused by the wrapping can be intended (or not if 0).

##### Centering

Example: `{var:^>70x68}`  
Type-hint: center(var: Any, centering: int, wrap: int)

Centers and also Text-wraps (while also centering wraps) to a specific width.
