# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

## [0.7.0] (2025-04-05)

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

### Fixed

- Updates license information in the README to reflect the MIT license.

### Removed

- Removes deprecated features from the codebase and documentation.

<!-- Links -->
[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html

<!-- Versions -->
[unreleased]: https://github.com/dannystewart/polykit/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/dannystewart/polykit/releases/tag/v0.7.0
