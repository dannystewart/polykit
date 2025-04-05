# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

## [0.5.2] (2025-04-04)

### Changed

- Replaces `EnvManager` with `Enviromancer` for environment variable management in `PathKeeper`.
- Changes folder structure by renaming `parsers` to `formatters` (breaking change: update imports from `polykit.parsers` to `polykit.formatters`).
- Updates `.pre-commit-config.yaml` to enhance hook execution by checking availability beforehand.
- Updates `poetry.lock` and `pyproject.toml` with improved dependency grouping and version constraints for consistency.
- Updates Visual Studio Code workspace settings for conventional commits.
- Enhances `__init__.py` module docstring to align with the README.

### Fixed

- Fixes an issue where `env_file` was not properly converted to a `Path` object when provided as a string.
- Fixes import statement for `VideoHelper` in `media_manager`.
- Fixes path handling in `EnvManager` for better compatibility with `env_files`.

### Documentation

- Updates installation instructions and clarifies feature migration in `README.md`.

<!-- Links -->
[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html

<!-- Versions -->
[unreleased]: https://github.com/dannystewart/polykit/compare/v0.5.2...HEAD
[0.5.2]: https://github.com/dannystewart/polykit/releases/tag/v0.5.2
