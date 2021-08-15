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

## Development

### Dependencies

- [Python](https://python.org/downloads) (v3.6 or newer)
- [PIP](https://pip.pypa.io/en/stable/installing) (v19.0 or newer)
- [Poetry](https://python-poetry.org/docs) (latest recommended)

### Installation

1. `git clone https://github.com/rlaphoenix/pynfogen`
2. `cd pynfogen`
3. `poetry config virtualenvs.in-project true` (optional, but recommended)
4. `poetry install`
5. `nfo -h`

## F.A.Q

Using pynfogen is fairly simple, it's a multi-command CLI program. You can see up-to-date help information by
running `nfo --help`, or reading the readme file.

The main command is `generate`, which will create NFO and description files based on *one* file. The description file
is intended to be used for a forum or post, while the NFO file is intended to be shared alongside the release.
However, modern day media sharing platforms do not allow either to be shared with the files, but allow them to be with
the forum thread or post instead.

### What is an NFO?

An NFO (aka .nfo, .NFO, a contraction of "Info" or "Information") is a commonly used filename extension for text files
that accompany various releases with information about them.

They are used to deliver release information about the media, such as the title, release date, authorship, etc. They
also commonly contain elaborate [ANSI art](https://en.wikipedia.org/wiki/ANSI_art).

An NFO is generally archaic, do not think otherwise. Originally, NFO files would be shared through IRC, Usenet,
Email, etc. However, these days, most platforms do not allow NFO files to be shared with the release itself, but
rather within a forum thread or post. NFOs are becoming more and more phased out in P2P sharing, but still remains
in use in some cases.

While there isn't any hard-rules, If you plan to create a modern-style NFO then the following is recommended:

- Max line-length of 70 characters.
- Text should not reach the edge of the file (col. 1 and 70), instead it should be padded by spacing or ANSI art.
- Text-encoding should be UTF-8 and not CP437. CP437 is far too restricted compared to UTF-8.

Note that, elaborate ANSI art is no longer really used or wanted. Modern NFO files tend to be verbose with minimal
ANSI art, rather than concise with elaborate ANSI art.

### What should I do after installation?

On initial installation, you won't have any [artwork](#templates) or [templates](#templates). You can take a
look at some example artwork and template files within the git project.
However, please see the [Copyright](#copyright-agreement-for-included-artwork-and-template-files) relating to the
included artwork and template files before you start using them.

You may also want to take a look at the [Configuration](#configuration) options.

Once you have everything set up as much as you want, simply take a look at the available commands with `nfo --help`.
The main command you want to take a look at would be `nfo generate -h`.

### What file do I pass to `nfo generate`?

It's simple actually. Pass whichever file you wish best describes the release, as in whichever gives the most
appropriate metadata and such that will be used within the NFO.

Let's say you're doing an NFO for a full season release, but the first episode has a problem and isn't representative
of most of the season, then use the second episode.

It's important to specify the appropriate `-s/--season`, `-e/--episode` parameters (or not!) as they clue in pynfogen
what kind of media this release is (wheter it's a Movie, a Season, or a Episode). More information on this can be seen
in `nfo generate -h`.

Finally, if pynfogen get's clued in that it's a season release, then it takes the release name from the folder name
of the parent folder of the file you passed. It's also important not to include any other file except the files you
will be releasing within said folder. Otherwise it may cause mistakes with the season episode count.

## Templates

There are three kinds of templates to use. NFO Template, Description Template, and Artwork Templates.

| Template             | Description                                                                        | File Extension |
| -------------------- | ---------------------------------------------------------------------------------- | -------------- |
| NFO Template         | Primary Scriptable, structural data, like the Title, Year, Media Information, etc. | .nfo           |
| Description Template | Similar to NFO templates, but are used for the description output.                 | .desc.txt      |
| Artwork Template     | Used for surrounding the template output with art, common text, etc.               | .nfo           |

To give you an example scenerio. I would create an Artwork template named 'phoenix' with concise ASCII artwork placed
above the NFO, and an NFO template for 'season', 'episode', and 'movie' releases. I would also make a corresponding
Description template for each of those NFO templates. I now have the ability to create NFO files for a Full Season
release, a Single Episode release, or a Single Movie release. E.g. `nfo generate movie Movie.2021.mkv -a phoenix`.

If you notice you are copy pasting something between templates that is not structural or media information, then
you should probably put it into the Artwork Template instead. Or, if you notice you are changing something in a
template often, for a different kind of release, perhaps think of making a seperate template for those kinds of
releases.

Artwork templates are not applied to the Description output, they are only used for the NFO output.

Description templates are intended to be the contents or body of your forum post, IRC message, Email, etc.
Not the NFO to share alongside you're release directly.

Where-as, NFO templates are intended to be shared alongside the release. However, not all platforms allow you to
share the .NFO directly with the file, but may ask you to share it separately, e.g. a specific input field.

## Configuration

All configuration is optional, and currently quite minimal. Configuration can be done manually to the configuration
file, or via `nfo config` (see `nfo config -h`). All available config options are listed below (with descriptions).

| Key            | Type   | Description                                                                    |
| -------------- | ------ | ------------------------------------------------------------------------------ |
| art            | string | The default artwork template to use, unless overridden by the `-a/--art` flag. |
| fanart_api_key | string | A Fanart.tv API Key to use for the fanart banner image (if available).         |

## Copyright Agreement for included Artwork and Template files

There's already example template files and artwork files for you to look at.
However, the Artwork files are copyright to whomever committed them where-as the templates are not copyright.
The copyrighted files may not be used, even under the conditions of the License, except for viewing as examples.
No derivative work is permitted based on their general concept.
Simply remember that artwork files are themselves pieces of Art, and should be treated as such.

## Text-encoding

Traditional NFOs expect to use the codepage 437 (cp437) "ascii" text-encoding.
pynfogen generally doesn't care what you use, but may not respect you're choice correctly in the NFO output.
It has not been set up for specific text-encoding choice and generally speaking UTF-8 is expected.

## Scripting

The scripting system used by pynfogen is by no means ideal. It is however, consistent.
It's mostly a mix of python's normal new-style string formatting, with custom formatters.
It also uses a PHP-like `<?{x:y}..?>` custom syntax for if statements.

Scripting is generally not recommended to be used within Artwork templates.

### If statement

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

### Custom Formatting

The following custom additional formatting to pythons new-style formatting is available:

#### Chaining

Example: `{var:bbimg:layout,2x2x0}`

Using `:` you can chain formatter results from left to right, passing previous value as it goes on.
The previous value does not necessarily need to be used.

For less confusion, since `:` is already used as standard in new-string formatting, look at the above example as
`{(var:bbimg):(layout,2x2x0)}`

#### Boolean

Example: `{var:true}` or `{var:!false}`.  
Type-hint: func(var: Any) -> Fixed\[1, 0]

Returns `1` if `var` is a truthy value, otherwise `0`.

There's also `{var:false}` and `{var:!true}` which is the flip-reverse of the above result.

#### BBCode Image Links

Example: `{var:bbimg}`  
Type-hint: bbimg(var: Union\[List\[dict], dict]) -> Union\[List\[str], str]  
Each dictionary: e.g. `{url: 'https://url/to/image/page', src: 'https://url/to/image/src.png'}`

Every dictionary is converted to BBCode `[IMG]` wrapped in `[URL]`. For example:
`[URL=https://url/to/image/page][IMG]https://url/to/image/src.png[/IMG][/URL]`

Returns a list of converted bbcode strings, or a single string if only one dictionary was provided.

#### Layout

Example: `{var:layout,3x2x1}`  
Type-hint: layout(var: Union\[List\[Any], Any], width: int, height: int, spacing: int) -> str

Lays out items in a grid-like layout, spacing out items using spaces (or new lines) as specified.
New-lines are used when spacing vertically.

#### Wrapping

Example: `{var:>>2x68}`  
Type-hint: wrap(var: Any, indent: int, wrap: int)

Text-wrap to a specific length. Each subsequent new-line caused by the wrapping can be intended (or not if 0).

#### Centering

Example: `{var:^>70x68}`  
Type-hint: center(var: Any, centering: int, wrap: int)

Centers and also Text-wraps (while also centering wraps) to a specific width.

## Contribute

Please do contribute! Issues, pull requests, and discussion topics are welcome.

Thank you to anyone who helps contribute to the project!
