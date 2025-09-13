# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

## [0.14.1] (2025-09-13)

### Added

- Makes `end_message` in `halo_progress` optional by passing `None`, which will clear the spinner without a message for cleaner output when a completion message is not needed.

### Changed

- Updates project dependencies including `platformdirs` (4.3.8 → 4.4.0), `requests` (2.32.4 → 2.32.5), `ruff` (0.12.9 → 0.12.11), and `typing-extensions` (4.14.1 → 4.15.0).

## [0.14.0] (2025-08-01)

More breaking changes in this one, reverting the new split class approach to the original approach in 0.12.0 and earlier.

### Added

- Adds comma formatting option to the `plural` method in `PolyNum` class, with a new `commas` parameter (enabled by default).
- Adds support for date objects in `get_pretty_time`, allowing date-only formatting, and introduces the `get_date_only` convenience function.
- Adds Peacock color customizations with a purple theme for better visual identification of the workspace.

### Fixed

- Fixes help text processing in `PolyArgs` to preserve uppercase in acronyms, preventing "API" from becoming "aPI" in help messages.

### Changed

- **BREAKING:** Deprecates `PolyText`, `PolyColors`, `PolyMoji`, `PolyNum`, `PolySplit`, and `PolyTruncate` classes and returns to the previous structure with the `Text` and `Time` classes, plus the addition of the `Markup` class so that `Text` can be a normal class instead of a `StrEnum`. Backward compatibility is maintained for now. I realized that the previous attempt at separation caused more headaches than it avoided and is not worth applying that level of granular separation. I'm sorry, mostly to myself, who now has to undo all this across all my other scripts.
- **BREAKING:** Renames parameter `with_count` to `show_num` in plural methods for better clarity across `PolyNum` and `PolyTime` classes.
- Reverts the more complicated pluralization logic in `PolyNum` to fix issues like "photoes." Turns out the simpler approach is best.
- Adds usage guidance for `PolyNum.format` method, recommending the use of the simpler `PolyNum.plural` method if pluralization is all you need.
- Deprecates the `html_escape` method, recommending the use of `html.escape` from the standard library instead.
- Updates development dependencies including `mypy` (1.17.0 to 1.17.1), `ruff` (0.12.5 to 0.12.7), `distlib`, `virtualenv`, and `certifi`.

## [0.13.0] (2025-07-11)

More breaking changes in this one.

### Added

- Adds optional parameters to `log_traceback` function, making it more flexible in various error handling scenarios.

### Changed

- Renames `PolyNumbers` to `PolyNum` for consistency and brevity.
- Removes `capitalize` parameter from all methods in `PolyNum`. You should use standard string capitalization with `.capitalize()` going forward.
- Updates dependencies to their latest versions:
  - certifi from 2025.6.15 to 2025.7.9
  - ruff from 0.12.0 to 0.12.3
  - typing-extensions from 4.14.0 to 4.14.1

### Removed

- Removes the deprecated `formatters` package and its modules (`text.py`, `time.py`, `types.py`) that contained the old `Text` and `Time` utility classes.

### Fixed

- Fixes `log_traceback` to properly handle being used directly as `sys.excepthook` by checking for None parameters and falling back to `sys.exc_info()`.

## [0.12.0] (2025-07-07)

Releasing beta [0.12.0b1] after additional testing. Please note the breaking changes made from 0.11. You will receive deprecation warnings when calling things that have been restructured, and they will eventually be removed.

### Added

- Adds enhanced plural method with more comprehensive English pluralization rules compared to the previous approach, including special case handling for words ending in 'y', 's', 'x', 'z', 'ch', 'sh', 'o', 'f', and 'fe', as well as support for negative numbers.

## [0.12.0b1] (2025-06-25)

**NOTE:** This is a major breaking release with several modules deprecated and split into new modules. Functionality remains the same, but imports will need to be updated. Things are mostly in place but I'm considering this a beta until I can finish testing with my own scripts.

### Added

- Replaces monolith `Text` class with specialized utility classes with more consistent naming for text and time manipulation:
  - `PolyText`, `PolyColors`, `PolyMoji`, `PolyNumbers`, `PolySplit`, `PolyTruncate`, and `PolyTime`
- Adds direct access to commonly used functions in the package's root namespace:
  - `truncate`, `split`, `plural`, `to_word`, `ordinal`, and `format` (from `PolyNumbers`)
- Adds thousands separator option to number formatting with new `commas` parameter in `PolyNumbers.format` method.

### Changed

- Changes the default behavior of pluralization methods to include the count with the word by default.
- Renames `format_number` method to `format` for better clarity and less redundancy when importing or calling via `PolyNumbers.format`.
- Updates dependencies to their latest versions:
  - `mypy` from 1.16.0 to 1.16.1
  - `ruff` from 0.11.13 to 0.12.0
  - `pygments` from 2.19.1 to 2.19.2
  - `python-dotenv` from 1.1.0 to 1.1.1
  - `certifi` from 2025.4.26 to 2025.6.15
  - `urllib3` from 2.4.0 to 2.5.0

### Deprecated

- Deprecates all methods in the `Text` and `Time` classes, pointing to corresponding methods in the new text and time classes.

### Fixed

- Fixes pluralization behavior by explicitly setting `with_count=False` parameter in internal method calls to ensure consistent output format.

## [0.11.4] (2025-06-20)

### Fixed

- Fixes the `num_to_word` method by passing `with_count=False` when calling `Text.plural` to match the change in its method signature.

## [0.11.3] (2025-06-20)

### Added

- Now includes the number count by default in `Text.plural` (e.g. "2 cats" rather than "cats"), making it more intuitive for most use cases.

### Changed

- Improves documentation for the `Text.format_number` method. Read it.

## [0.11.2] (2025-06-10)

### Added

- Exposes additional `polykit` modules at package level, including `PolyArgs`, `PolyEnv`, `PolyFile`, `PolyPath`, and `Text` and `Time` formatters for more concise imports.
- Adds improved text formatting to the help formatter in `PolyArgs` with intelligent line break preservation for lists, indented text, and better handling of intentional formatting.
- Adds documentation for the `lines` parameter in `PolyArgs` class docstring and clarifies that the `add_version` parameter defaults to True.

### Changed

- Updates multiple dependencies:
  - Poetry from 2.1.2 to 2.1.3
  - `charset-normalizer` from 3.4.1 to 3.4.2
  - `identify` from 2.6.10 to 2.6.12
  - `mypy` from 1.15.0 to 1.16.0
  - `pdoc` from 15.0.3 to 15.0.4
  - `platformdirs` from 4.3.7 to 4.3.8
  - `requests` from 2.32.3 to 2.32.4
  - `ruff` from 0.11.7 to 0.11.13
  - `typing-extensions` from 4.13.2 to 4.14.0
- `virtualenv` from 20.30.0 to 20.31.2

### Removed

- Removes the `conversion_list_context` context manager from the `progress` module as it was designed for a specific use case and wasn't broadly applicable.

## [0.11.1] (2025-05-01)

### Changed

- Updates package dependencies to their latest versions, including `packaging` (24.2 → 25.0) and `termcolor` (3.0.1 → 3.1.0), plus dev dependencies.

## [0.11.0] (2025-05-01)

Tiny update, but with a parameter name change in `PolyFile`.

### Changed

- **BREAKING:** Renames the `hidden` parameter in the `list` method in `PolyFile` to `include_dotfiles` to make the parameter more self-documenting by clearly illustrating what it does (include) and how it defines "hidden" (dotfiles).

## [0.10.2] (2025-04-18)

### Added

- Adds `PolyEnv` support directly to `PolyLog`, allowing log level to be easily determined from environment variables, and opening the door for further integration and environment-specific configuration down the line.

### Changed

- Improves documentation for `Text` class methods with detailed docstrings, additional examples, and new parameters.
- Improves documentation readability by wrapping example code blocks in Markdown code fences for better syntax highlighting.
- Simplifies module docstrings with more concise formatting.
- Enhances README organization with better section hierarchy and more descriptive component explanations.
- Renames shadowed variables to improve code clarity and prevent potential bugs.

### Fixed

- Corrects pluralization logic for time units to handle zero and negative values properly.
- Removes unused imports.
- Fixes incorrect license references to correctly show LGPLv3.

## [0.10.1] (2025-04-13)

### Added

- Upgrades documentation to a beautiful new [Tokyo Night](https://github.com/dannystewart/pdoc-tokyo-night) theme, created by yours truly, replacing the basic dark theme with improved typography, visual hierarchy, and enhanced syntax highlighting for a more polished, professional appearance.

### Changed

- Formats pre-commit config YAML for consistency.
- Updates `ruff.toml` with new configuration version and file-specific ignores.

## [0.10.0] (2025-04-11)

### Changed

- **BREAKING:** Relocates shell functionality to CLI package, moving `interrupt.py` and `permissions.py` from `shell/` to `cli/` package for better organizational clarity and to eliminate ongoing confusion between CLI and shell modules.
- **BREAKING:** Renames `recurse` parameter to `recursive` in the `PolyFile.list` method for better readability and consistency with Python naming conventions. Your files will now be recursively listed in a more Pythonic way.

## [0.9.1] (2025-04-09)

### Changed

- Improves platform detection by switching to more compatible `platform.system()` method instead of `os.uname()`, making the application run reliably across different operating systems.
- Enhances macOS compatibility by normalizing "macOS" and "Darwin" references.

## [0.9.0] (2025-04-07)

**Polykit's development status has changed from Beta to Production/Stable!** 🎉

Polykit has been around long enough (in some shape or form) that I consider it stable enough for use. It's not the kind of project I think will ever hit 1.0 because of its constant evolution, but I'm trying to take minor version bumps more seriously for breaking changes. This means 0.9.0 and 0.10.0 could come out the same day if changes are severe enough, but at least nothing should break in between (hopefully).

### Added

- Updating to version 0.9.0 due to breaking changes (see below).

- `PolyLog`
  - Adds `LogLevelOverride` context manager for temporarily changing log levels, making it easier to control verbosity in specific code blocks.

- `PolyEnv`
  - Adds `print_all_values` method for more easily displaying currently stored environment variables, with smart handling of secret values.

### Changed

- Platform utilities have moved to the `core` module. `polykit_setup` must now be imported from `polykit.core` rather than `polykit.platform`.

- `PolyEnv`
  - Improves environment variable debugging with counters, better secret detection, and helpful summary messages.

- **Documentation**
  - Enhances README with a snazzy table of contents, feature section links, and clearer descriptions that won't put you to sleep.
  - Updates library introduction docs with detailed sections on features and use cases—now with 100% more examples!

### Fixed

- `PolyEnv`
  - Fixes missing variable errors in `print_all_values` method with try/except handling. No more crashes when variables play hide and seek.
  - Replaces print statements with proper `logger.debug` calls. Printing is so 1990s.

## 0.7.4 (2025-04-06)

### Changed

- Simplifies Walking Man's wave animation. (Waving with both arms made it look like he was doing finger guns!)

## 0.7.3 (2025-04-06)

### Added

- Adds enhanced handling for the `--version` argument in the CLI to avoid duplication and ensure user-defined arguments are respected. Improves detection of version flags for smoother parsing.

### Changed

- Improves README structure for better clarity and navigation.

## 0.7.2 (2025-04-06)

### Added

#### `<('-')>` **Walking Man 2.0: The Waving Man Update!**  `<('-')/`

- Introduces a middle position state for Walking Man, for smoother turns and improved alignment.
- Adds a waving animation for Walking Man, triggered after multiple rotations, complete with new character frames and logic.

### Changed

- Updates README to improve structure, clarity, and navigation, expanding feature descriptions with examples and streamlining content flow.
- Refines and expands changelog details for Walking Man 2.0, covering features like the middle position state, waving animation, and improved boundary handling.
- Improves Walking Man's boundary handling for more accurate position updates.
- Enhances character alignment during movement by refining spacing logic.

## 0.7.1 (2025-04-05)

### Added

- Enhances README with detailed usage examples for core utilities such as `PolyLog`, `PolyEnv`, `PolyPath`, `PolyFile`, and `PolyDiff`. Includes code snippets, usage scenarios, and explanations to improve onboarding and highlight key features.

### Changed

- Renames `ArgParser` to `PolyArgs` for improved clarity and alignment with project naming conventions. Updates imports and documentation accordingly.
- Improves documentation across module initialization files, reorganizing imports for better logical grouping and readability. Adds examples and refines descriptions for enhanced developer experience.

### Fixed

- Updates type hints for the `delete` method in the `files` module to ensure consistency and correctness by using `PathList`.

## 0.7.0 (2025-04-05)

### Added

- Adds exception handling utilities to `PolyLog`: `exception` for logging exceptions, `catch` as a context manager, and `decorate` as a decorator for wrapping functions with exception logging.
- Adds `PolyDiff` class for file comparison with intuitive files and content methods for diff output.
- Adds `PolyFile` utility class for file operations with integration of natsort and send2trash dependencies.

### Changed

- Renames `Logician` to `PolyLog` and `PathKeeper` to `PolyPath` for clarity and consistency.
- Converts instance methods to class methods in `PolyFile` and `PolyDiff` to provide a more functional interface without requiring instantiation.
- Updates the `delete` method in `PolyFile` to return lists of successful and failed file paths instead of just counts.
- Streamlines file operations and enhances logging functionality in `PolyFile`.
- Reorganizes imports and moves `VersionChecker` and `platform_check` to new modules.
- Moves interrupt-handling decorators to the `shell` folder.
- Updates the import statement for `PolyVar` to use the `types` module.
- Condenses the module docstring in `__init__.py` for clarity.
- Removes an outdated note on version handling requirements in argument parsing.

### Removed

- Removes deprecated features from the codebase and documentation.

<!-- Links -->
[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html

<!-- Versions -->
[unreleased]: https://github.com/dannystewart/polykit/compare/v0.14.1...HEAD
[0.14.1]: https://github.com/dannystewart/polykit/compare/v0.14.0...v0.14.1
[0.14.0]: https://github.com/dannystewart/polykit/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/dannystewart/polykit/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/dannystewart/polykit/compare/v0.11.4...v0.12.0
[0.11.4]: https://github.com/dannystewart/polykit/compare/v0.11.3...v0.11.4
[0.11.3]: https://github.com/dannystewart/polykit/compare/v0.11.2...v0.11.3
[0.11.2]: https://github.com/dannystewart/polykit/compare/v0.11.1...v0.11.2
[0.11.1]: https://github.com/dannystewart/polykit/compare/v0.11.0...v0.11.1
[0.11.0]: https://github.com/dannystewart/polykit/compare/v0.10.2...v0.11.0
[0.10.2]: https://github.com/dannystewart/polykit/compare/v0.10.1...v0.10.2
[0.10.1]: https://github.com/dannystewart/polykit/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/dannystewart/polykit/compare/v0.9.1...v0.10.0
[0.9.1]: https://github.com/dannystewart/polykit/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/dannystewart/polykit/releases/tag/v0.9.0
