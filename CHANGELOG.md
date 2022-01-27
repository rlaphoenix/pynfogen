# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2022-01-27

### Added

- Added export() and import(), which is the ability to backup and restore configuration, artwork,
  and templates to and from one gzip compressed file.
- Video Range is now shown in Video Track print line 2. Includes fallback range.
- Added a LICENSE for the /examples/art that is separate to main license.
- Added a `.gitattributes` file to enforce lf line-endings on all text files.
- Added `jsonpickle` to dependencies.
- Added `isort` test to CI workflow, added tests on 3.10.
- Added `pre-commit` to dev dependencies and a config with tests for isort, flake8, and more.

### Changed

- Advanced Development Status PyPI trove classifier to 4 (Beta).
- Replaced all uses of `pycountry` with `langcodes`.
- Renamed GitHub Workflows from Build and Release to CI, CD.
- Refactored CD workflow to auto-create releases when version tags are made.

### Removed

- Dropped support for Python versions below 3.7.
- Dropped CI workflow tests on 3.6.

### Fixed

- Editorconfig will no longer trim trailing whitespace on Markdown files.
- Updated the README for v1.0.0 changes.
- Fixed the custom `if` formatter example which had a syntax error.
- LICENSE and README.md is no longer explicitly included.

## [1.0.0] - 2021-08-28

### Added

- (nfo generate) It now prints the location of the generated NFO and Description files.
- (nfo generate) Added new option -e/--encoding to control the output text-encoding. It defaults to UTF-8. It's
  recommended to use `cp437` for ANSI art, or `utf8` for generally anything else. Ensure the software, page, forum,
  and so on actually supports the output text-encoding you choose. Any characters that do not map to the wanted
  text-encoding will use unidecode to map to a best-match character. Any characters unidecode also cannot map to
  a suitable character, will simply be ignored (i.e., deleted).
- (nfo) It now ensures that all tracks have language information associated with them on the provided file path.
  If not, it will tell you which tracks did not have any language information and ask you to add it. Language
  checks happen for various reasons across the codebase on multiple track types, so it's important to have them.
  Yes, even Video tracks should have language information!

### Changed

- (nfo generate) The template argument has been replaced with sub-commands named `season`, `episode`, and `movie`.
  These sub-commands directly use templates named respectively, and directly relate to the type of content for the
  generate command to expect. This makes it possible to move -s and -e to only the ones it needs to be used in.
- (nfo) No longer prints its own NFO object instance representation at the end of set_config calls.
- (cli) Replaced `os.path` calls with `Path` across the nfo CLI codebase.
- (formatter) The multiple if checks in format_field has been replaced with a list of tuples for easier glances at
  what custom specs are available, and how they are to be used.
- (examples) The release_name variable on the NFO templates have been changed from centered-wrap, to left-wrap with
  a 2-space indent. Centered wrapping never looked good due to typical release names not containing spaces or any
  characters that could be cleanly wrapped at.
- (examples) The `- - - ...` dashed line and `\n Video : ` (and so on) lines have been replaced with a hard line
  separator with two windows, one for the section name, and the other for the section number/count. This reduces the
  height footprint and helps distinguish between sections.

### Removed

- The term BBCode in relation to Description Templates has been removed. Description templates can use any kind of
  format, or no particular format at all.
- (examples) The `Greetz` text at the end of the example Description templates.

### Fixed

- (nfo generate) Artwork and template files are now explicitly UTF-8. This was a problem on systems that did not use
  UTF-8 by default (e.g., Windows using cp1257 instead).
- (nfo) Only try to get a banner image if a fanart API key is available.

### Security

- (nfo generate) You can no longer get values from the users' config using the config key as a variable name. This
  allowed malicious template files to leak possibly sensitive information.

## [0.5.1] - 2021-08-26

### Added

- (dependencies) Added `pytomlpp` for TOML parsing.
- (config) Created new config file to manage declaration of important directories and filenames. All code that used
  files or directories have been updated to use these new importable config objects.
- (nfo generate) Load settings from the config under the `generate` key. This means the defaults for any of the
  arguments for nfo generate is now able to set by the config.

### Changed

- (config) All uses of YAML for the config file has been replaced with TOML. Any existing `config.yml` files are now
  invalid and should be re-written entirely due to other config changes.
- (git) Update `.gitignore` to latest from <https://github.com/github/gitignore>.

### Deprecated

- (config) `art` option is no longer used. It has been renamed to `artwork` and moved under the `generate` key.
  The config `art` option hasn't actually been used since the move to CLI, by mistake.

### Removed

- (dependencies) `PyYAML` as it's been replaced in favor of `pytomlpp` to switch from YAML to TOML, see above.
- (git) Unnecessary `config.yml` exclusion has been removed.

### Fixed

- (nfo) Fix Runtime type-error in get_tvdb_id when click converts the provided TVDB ID string from CLI to an integer.

## [0.5.0] - 2021-08-22

### Added

- (dependencies) Added `flake8`, `mypy`, `types-requests` and `isort` to dev-dependencies.
- (nfo) The get_banner_image method now returns banners in the same language of the primary audio track.
- (nfo) The chapter_entries scripting variable now shows the timecode to the left of the Chapter Name/Title.
- (examples) Added example output NFO and Description TXT generated by `nfo generate`.

### Changed

- (pycharm) Disabled the AttributeOutsideInit Inspection. This is to follow a more modern approach of type-hinting
  in the init function, instead of out-right initializing it with a value it probably doesn't need nor want.
- (nfo) get_database_ids method has been replaced with separate methods for each database ID. The new methods and
  code are more optimized too, with tightened checks on the ID values provided either by the user or the file metadata.
- (nfo) Replaced the uses of the scrape function from helpers with a new `requests` session which is stored in the NFO
  class directly.
- (nfo) The chapters attribute value is now a Dict with the key being the chapter timecode and the value being the
  chapter name/title.

### Fixed

- (nfo) The chapters_numbered check now checks case-insensitively.
- (nfo) The get_banner_image method now correctly returns banner URLs in expected languages.
- (examples) Removed typo `%` from the end of the if check syntax in templates near the chapter_entries variable.
- (examples) Fixed the list->indented newline-separated paragraph conversion on the chapters_entries variable.
- (examples) Removed unnecessary trailing whitespace from some artwork and templates.

### Removed

- (dependencies) Dropped support for Python 3.6.0 due to bugs in it. Python 3.6.1 and above is still supported.

## [0.4.4] - 2021-08-21

### Added

- Created `.markdownlint.yaml` and `.editorconfig` files for cross-editor configuration.
- Added the Contributor Covenant as `CODE_OF_CONDUCT.md`.
- (readme) Mention that scripting is not recommended on artwork templates.

### Changed

- (changelog) Updated the changelog to use Keep a Changelog. This makes the changelog a lot easier to read and write.
- (readme) Update the usage, installation, general layout, fixes. It was previously stating instructions for the old
  non-cli versions.
- (examples) Moved the artwork, nfo, and description templates from within the python-module directory to the new
  `/examples` directory.
- (license) Update year and username of the copyright line near the bottom of the file. The license is otherwise the
  exact same.

### Fixed

- (nfo) Subtitle print list no longer skips printing the subtitle language if it isn't included in the subtitle track
  title. It now supports scenarios in which the language is or isn't in the subtitle track title for compatibility.

### Security

- All YAML loads now use `yaml.safe_load` for extra security protection.

## [0.4.3] - 2021-07-12

### Added

- (github) Added GitHub actions CI build and release workflows.
- (readme) Add some Badges including new CI build status.
- (nfo artwork) Add nfo artwork explore with the same functionality as nfo template explore.

### Removed

- Unnecessary `/__init__.py` file at root.

### Fixed

- (nfo artwork) Fix possibility of a no-print result if the directory exists but is empty.
- (nfo template) Fix possibility of a no-print result if the directory exists but is empty.
- (nfo config) Ensure the config directory exists before attempting to write to it.

## [0.4.2] - 2021-06-26

### Changed

- (dependencies) Updated `pyd2v` to v1.3.0 to use the `_get_d2v()` which was originally part of `pvsfunc`, hence why
  it's removal was possible.

### Removed

- (dependencies) `pvsfunc` as it's highly integrated with VapourSynth causing unnecessary VapourSynth requirements.
  I only ever used it for one small function which has been moved to `pyd2v`.
- (dependencies) `poetry-dynamic-versioning` as it's caused some problems in some pip related nonsense, and this
  project isn't often updated enough to justify its PROs vs. CONs.

## [0.4.1] - 2021-06-24

### Added

- (nfo) Support for IMDb `Mini Series` titles. Previously I only knew of `Mini-Series` titles (note the `-`).

### Changed

- (dependencies) Updated `click`, `poetry-dynamic-versioning`, `pvsfunc`, and `pyd2v`.

### Removed

- config.example.yml file remnant that isn't needed due to breaking changes in [0.4.0].

### Fixed

- (nfo generate) Run `nfo.set_config` even if there's no config or no data in the config.
- (nfo generate) Ensure sure the input file or folder path exists before running generate code.

## [0.4.0] - 2021-06-05

### ⚠️ Breaking Changes

- Deleted `pynfogen.py` to move away from a split use-case project to a unified CLI-only project.

### Fixed

- (nfo generate) Fix extra template variable name conflicts with base NFO class variable names. Requires template file
  updates, see commit ID [15c66d8] for more information, and see it's changes to the example template files to know
  what to change.
- (nfo template) Add missing `--bbcode` option to `delete` subcommand.
- (readme) Fix the syntax and semantics of the custom formatter `If statement` examples.

  [15c66d8]: <https://github.com/rlaphoenix/pynfogen/commit/15c66d8d6767abb04fc26a354aec3bac09f1b542>

### Added

- (nfo) Support for IMDb `Short` titles in `get_title_name_year`.
- (readme) Advertise that PyPI/PIP is a valid installation method.
- (readme) Clarify `poetry config virtualenvs.in-project true` as being recommended, yet optional.

## [0.3.3] - 2021-05-27

### Fixed

- (nfo generate) Ensure `-s` is optional by checking `-s` has a value before using it for the int cast check.

## [0.3.2] - 2021-05-11

### Fixed

- (nfo generate) Ensure file path is absolute so `release_name` can be correctly retrieved in some scenarios.

## [0.3.1] - 2021-05-07

### Fixed

- (nfo config) Fix crash when no valid commands and/or options are used. Return help information in those cases.
- (nfo generate) Fix/Update the doc-string information for `nfo generate`.
- (nfo generate) Use `-N/--note` not `-N/--notes` as to match the already defined `note` variable used by NFO object.

## [0.3.0] - 2021-05-06

### Added

- (changelog) This HISTORY.md document.
- (nfo template) `--bbcode` switch for specifying creation/editing of a BBCode Description template.
- (nfo template) `template explore` command to open template directory in file explorer.
- (init) `__version__` string is now available for external use by other scripts and `version` command.

### Changed

- (formatter) Custom formatter specs `boolean` and `length` now returns as ints, but gets cast to str when needed.

### Fixed

- (version) `version` command no longer errors out if it's installed outside a git repository.
- (formatter) Custom formatter spec `layout` no longer panics if it receives a null/length of 0 items.

## [0.2.0] - 2021-05-05

### Added

- (dependencies) Added `poetry-dynamic-versioning` and `click`.
- (cli) Created CLI Interface using click.
- (versioning) Added `poetry-dynamic-versioning` for git tag based automated versioning.
- (readme) README now has information on requirements, setup, installation, etc.
- (formatter) New `len` formatter. It returns the `len()` of an object.

## Changed

- (packaging) Replaced setuptools with Poetry (<https://python-poetry.org>).
- (packaging) Project has been reworked as a python module.
- (nfo generate) Artwork is now optional.

## [0.1.0] - 2021-05-05

- Initial release.

[Unreleased]: https://github.com/rlaphoenix/pynfogen/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/rlaphoenix/pynfogen/releases/tag/v1.1.0
[1.0.0]: https://github.com/rlaphoenix/pynfogen/releases/tag/v1.0.0
[0.5.1]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.5.1
[0.5.0]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.5.0
[0.4.4]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.4.4
[0.4.3]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.4.3
[0.4.2]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.4.2
[0.4.1]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.4.1
[0.4.0]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.4.0
[0.3.3]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.3.3
[0.3.2]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.3.2
[0.3.1]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.3.1
[0.3.0]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.3.0
[0.2.0]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.2.0
[0.1.0]: https://github.com/rlaphoenix/pynfogen/releases/tag/v0.1.0
