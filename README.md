# pynfogen

> [!IMPORTANT]  
> This has been functionally replaced with <https://nfog.vercel.app>
> 
> This original version of pynfogen had upstream packages break that were quite critical,
> but even then, a vast majority of users struggled to grasp the templating and CLI commands.
> And to > be honest I can't blame anyone since really too many things were going on for a simple task.
>
> The new Web App version is a lot nicer to use with a lot of automation built into it
> as well as an on-the-fly previewing system where you can see the variables available.

[![License](https://img.shields.io/github/license/rlaphoenix/pynfogen)](https://github.com/rlaphoenix/pynfogen/blob/master/LICENSE)
[![Build status](https://github.com/rlaphoenix/pynfogen/actions/workflows/ci.yml/badge.svg)](https://github.com/rlaphoenix/pynfogen/actions/workflows/ci.yml)
[![Python version](https://img.shields.io/pypi/pyversions/pynfogen)](https://pypi.python.org/pypi/pynfogen)
[![PyPI version](https://img.shields.io/pypi/v/pynfogen)](https://pypi.python.org/pypi/pynfogen)
[![DeepSource issues](https://deepsource.io/gh/rlaphoenix/pynfogen.svg/?label=active+issues)](https://deepsource.io/gh/rlaphoenix/pynfogen)

Scriptable MediaInfo-fed NFO Generator for Movies and TV.

## Installation

    pip install --user pynfogen

## F.A.Q

Using pynfogen is fairly simple, it's a multi-command CLI program. You can see up-to-date help information by
running `nfo --help`, or reading the readme file.

On initial installation, you won't have any [Artwork](#artwork) or [Templates](#templates), which are needed. You can
take a look at some examples at [/examples/art](/examples/art) and [/examples/templates](/examples/templates) in the
git. You may also want to take a look at [Configuration](#configuration).

Once you have everything set up as much as you want, simply take a look at the available commands with `nfo --help`.
The main command you want to take a look at would be `nfo generate -h`, which will create NFO and Description files
based on *one* provided video file.

What is an NFO and Description file, you may ask? tl-dr; Think of an NFO as a Receipt with information about your
release to be shared alongside it, and a Description file as the body for your post, thread, topic, message, or
such. You could also think of a Description file as an alternative output you could use.

More information can be found in the sections below.

### What is an NFO?

An NFO (aka .nfo, .NFO, a contraction of "Info" or "Information") is a commonly used filename extension for text files
that accompany various releases with information about them.

They are for delivering release information about the media, such as the title, release date, authorship, etc. They
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

### What is a Description file?

It's like an NFO, without any rules whatsoever. You can use a description template as an alternative output to the NFO
output. This alternative output can be used for any purpose you like, but most commonly used for forum posts, IRC
messages, and such.

### What file should I pass to `nfo generate`?

It's best-practice to provide the first-most file that best represents the majority of the release. E.g., If Episode 1
and 2 has a fault not found on Episodes 3 onwards, then provide Episode 3.

### What Text-encoding is supported?

The input file templates and artwork must be UTF-8. The output generated files' text-encoding can be chosen by you,
but defaults to UTF-8.

To choose a text-encoding for the output, see `-e/--encoding` of `nfo generate`. This can also be set in the config
with `nfo config generate.encoding cp437` (sets to CP437).

NFOs with elaborate ANSI art may need to use CP437 text-encoding, where-as any other NFO can get away with just about
any encoding. The default UTF-8 will work fine for most scenarios. However, some applications or websites may require
your NFO to be a specific text-encoding, which is usually either CP437 or UTF-8.

### How is it detecting or getting ...?

#### Database IDs (IMDB, TMDB, TVDB)

CLI options (`-imdb`, `-tmdb`, `-tvdb`), the Config, or the provided file's global tags (in that order).

#### Title Name and Year

The IMDB page's `<title>` tag for the provided IMDB ID.

#### Release Name

Season releases get it from the parent folder name of the provided file.
Movie and Episode releases get it from the filename.

#### Preview Images

It scrapes the provided Preview URL (`-P`) for thumbnail and full image URLs.
The Preview URL must be for a Gallery or Album.
Supported hosts:

- <https://imgbox.com>
- <https://beyondhd.co>

#### Banner Image

The Fanart.tv API if a TVDB ID has been provided, and a Fanart.tv API key has been set.
It only returns banners that match the language of the primary Audio tracks language.

#### Season Episode Count

It counts the amount of neighbouring files of the same file-extension as the provided file. Make sure all files
matching this check is going to be part of the release as an episode file, or the episode count will be inaccurate.

## Templates

| Type                 | Description                                                                        | File Extension |
| -------------------- | ---------------------------------------------------------------------------------- | -------------- |
| NFO Template         | Primary Scriptable, structural data, like the Title, Year, Media Information, etc. | .nfo           |
| Description Template | Similar to NFO templates, but for the content of a forum post, IRC message, etc.   | .desc.txt      |

You can add, delete, edit, and list templates with `nfo template -h`.

Tip: If you notice you are copying and pasting something between templates that is not structural or media information,
then you should probably put it into an [Artwork](#artwork) instead.

## Artwork

Artworks are for surrounding an NFO templates generated output with artwork or common text. Artwork templates aren't
currently applied to Description templates.

You can add, delete, edit, and list artwork with `nfo artwork -h`.

**Important:**
The provided example Artwork files are for viewing and studying only, for more information see their
[LICENSE](/examples/art/LICENSE).

## Configuration

All configuration values is entirely optional, but may require to be set to enable some features.

Configuration values can be set with `nfo config`, e.g., `nfo config generate.artwork phoenix`.
See `nfo config -h` for more information.

| Config Key     | Description                                                                   |
| -------------- | ----------------------------------------------------------------------------- |
| fanart_api_key | A Fanart.tv API Key to use for the fanart banner image (if available)         |
| generate.*     | Allows you to set a default for any of the arguments in use by `nfo generate` |

## Scripting

The scripting system used by pynfogen is by no means ideal. It is however, consistent.
It's mostly a mix of python's normal new-style string formatting, with custom formatters.
It also uses a PHP-like `<?{x:y}..?>` custom syntax for if statements.

Scripting is generally not recommended to be used within Artwork templates.

### If statement

For example the following will check if the `{note}` variable (python new-style formatting) is a truthy value,
and only if so, print it:

    # note = "Hello World!"
    <?{note:true}?Has note: {note}?>
    # returns: `Has note: Hello World!`

    # note = ""  # or None, 0, False, 1==2, e.t.c
    <?{note:true}?Has note: {note}?>
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

## License

[MIT License](LICENSE)
