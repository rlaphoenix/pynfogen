# Release History

## 0.4.2

- Remove: pvsfunc as it's highly integrated with VapourSynth use-cases causing unnecessary VapourSynth installation
  requirements which can be a pain in the a--! I only ever used it for one small function which I moved to pyd2v.
- Remove: poetry-dynamic-versioning as it's caused some problems in some pip related nonsense, and this project
  isn't often updated enough to justify its pros vs. it's current cons.
- Improvement: Update pyd2v to v1.3.0 to use the `_get_d2v()` which was originally part of pvsfunc, hence why it's
  removal is now possible.

- All removed top-root dependencies: jinja2, markupsafe, more-itertools, poetry-dynamic-versioning, pvsfunc, tomlkit,
  vapoursynth

## 0.4.1

- New: Add support for `Mini Series` IMDB titles. Previously I only knew of `Mini-Series` titles (note the `-`).
- Remove: config.example.yml file remnant that isn't needed due to breaking changes in v0.4.0.
- Update: pyd2v, pvsfunc, click, poetry-dynamic-versioning, and their dependencies.
- Fix: Run nfo.set_config even if there's no config or no data in the config.
- Fix: Ensure sure the input file or folder path exists before running generate code.

## 0.4.0

### ⚠️Breaking Changes

- Delete `pynfogen.py` to move away from a split use-case project to a unified CLI-only project.

#### nfo generate

- Fix extra template variable name conflicts with base NFO class variable names. Requires template file updates,
  see commit ID [15c66d8] for more information, and see it's changes to the example template files to know what to
  change.

  [15c66d8]: <https://github.com/rlaphoenix/pynfogen/commit/15c66d8d6767abb04fc26a354aec3bac09f1b542>

### Improvements

#### NFO

- Add support for IMDB `Short` IDs in `get_title_name_year`.

#### README

- Advertise that PyPI/PIP is a valid installation method.
- Clarify `poetry config virtualenvs.in-project true` as being recommended, yet optional.

### Bug fixes

#### nfo template

- Fix `delete` subcommand's use of it's missing `bbcode` argument.

#### README

- Fix the syntax and semantics of the custom formatter If statement examples.

## 0.3.3

### Bug fixes

#### nfo generate

- Ensure `-s` is optional by checking `-s` has a value before using it for the int cast check.

## 0.3.2

### Bug fixes

#### nfo generate

- Ensure file path is absolute so `release_name` can be correctly retrieved in some scenarios.

## 0.3.1

### Bug fixes

#### nfo config

- Fix crash when no valid commands and/or options are used. Return help information in those cases.

#### nfo generate

- Fix/Update the doc-string information for `nfo generate`.
- Use -N/--note not -N/--notes as to match the already defined `note` variable used by NFO object.

## 0.3.0

### Additions

- This HISTORY.md document.
- `--bbcode` switch for specifying creation/editing of a BBCode Description template.
- `template explore` command to open template directory in file explorer.
- `__version__` string is now available for external use by other scripts and `version` command.

### Bug fixes

- `version` command no longer errors out if it's installed outside a git repository.
- Custom formatter spec `layout` no longer panics if it receives a null/length of 0 item.
- Custom formatter specs `boolean` and `length` now returns as ints, but gets cast to str when needed.

## 0.2.0

### Additions

- poetry-dynamic-versioning for git tag based automated versioning.
- Poetry now deals with all dependencies.
- README now has information on requirements, setup, installation, e.t.c.
- Python Click has been installed for a new CLI Interface.
- New custom format spec: len. It returns the `len()` of an object.

### Improvements

- Project has been reworked as a python module.
- Formatter has been improved to be more readable and more maintainable.
- NFO class has had a lot of unnecessary and repetitiveness cleaned up, a fair bit.
- Artwork is now optional.
- Readability and maintainability has been improved across the board.
- Main interface's config.yml file is now a bit simpler and more condensed than before.
- Code Documentation has been improved a small bit.

## 0.1.0

- Initial real version.
- Long gap in time since previous version.
- Poetry installed, setuptools ditched.

## 0.0.0

- Slow development, mostly a rushed test to just get it working.
