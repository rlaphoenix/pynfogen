# Release History

## 0.3.0

**Additions**

- This HISTORY.md document.
- `--bbcode` switch for specifying creation/editing of a BBCode Description template.
- `template explore` command to open template directory in file explorer.
- `__version__` string is now available for external use by other scripts and `version` command.

**Bug fixes**

- `version` command no longer errors out if it's installed outside a git repository.
- Custom formatter spec `layout` no longer panics if it receives a null/length of 0 item.
- Custom formatter specs `boolean` and `length` now returns as ints, but gets cast to str when needed.

## 0.2.0

**Additions**

- poetry-dynamic-versioning for git tag based automated versioning.
- Poetry now deals with all dependencies.
- README now has information on requirements, setup, installation, e.t.c.
- Python Click has been installed for a new CLI Interface.
- New custom format spec: len. It returns the `len()` of an object.

**Improvements**

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
