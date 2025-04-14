# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

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
[unreleased]: https://github.com/dannystewart/polykit/compare/v0.10.1...HEAD
[0.10.1]: https://github.com/dannystewart/polykit/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/dannystewart/polykit/compare/v0.9.1...v0.10.0
[0.9.1]: https://github.com/dannystewart/polykit/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/dannystewart/polykit/releases/tag/v0.9.0
