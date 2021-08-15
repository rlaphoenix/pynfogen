# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.3] - 2021-07-12

### Added

- (github) Added GitHub actions CI build and release workflows.
- (readme) Add some Badges including new CI build status.
- (artwork) Add nfo artwork explore with the same functionality as nfo template explore.

### Removed

- Unnecessary `/__init__.py` file at root.

### Fixed

- (artwork) Fix possibility of a no-print result if the directory exists but is empty.
- (template) Fix possibility of a no-print result if the directory exists but is empty.
- (config) Ensure the config directory exists before attempting to write to it.

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

- (generate) Run `nfo.set_config` even if there's no config or no data in the config.
- (generate) Ensure sure the input file or folder path exists before running generate code.

## [0.4.0] - 2021-06-05

### ⚠️ Breaking Changes

- Deleted `pynfogen.py` to move away from a split use-case project to a unified CLI-only project.

### Fixed

- (generate) Fix extra template variable name conflicts with base NFO class variable names. Requires template file
  updates, see commit ID [15c66d8] for more information, and see it's changes to the example template files to know
  what to change.
- (template) Add missing `--bbcode` option to `delete` subcommand.
- (readme) Fix the syntax and semantics of the custom formatter `If statement` examples.

  [15c66d8]: <https://github.com/rlaphoenix/pynfogen/commit/15c66d8d6767abb04fc26a354aec3bac09f1b542>

### Added

- (nfo) Support for IMDb `Short` titles in `get_title_name_year`.
- (readme) Advertise that PyPI/PIP is a valid installation method.
- (readme) Clarify `poetry config virtualenvs.in-project true` as being recommended, yet optional.

## [0.3.3] - 2021-05-27

### Fixed

- (generate) Ensure `-s` is optional by checking `-s` has a value before using it for the int cast check.

## [0.3.2] - 2021-05-11

### Fixed

- (generate) Ensure file path is absolute so `release_name` can be correctly retrieved in some scenarios.

## [0.3.1] - 2021-05-07

### Fixed

- (config) Fix crash when no valid commands and/or options are used. Return help information in those cases.
- (generate) Fix/Update the doc-string information for `nfo generate`.
- (generate) Use `-N/--note` not `-N/--notes` as to match the already defined `note` variable used by NFO object.

## [0.3.0] - 2021-05-06

### Added

- (changelog) This HISTORY.md document.
- (template) `--bbcode` switch for specifying creation/editing of a BBCode Description template.
- (template) `template explore` command to open template directory in file explorer.
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
- (generate) Artwork is now optional.

## [0.1.0] - 2021-05-05

- Initial release.

[Unreleased]: https://github.com/rlaphoenix/pynfogen/compare/v0.4.3...HEAD
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
