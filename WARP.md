# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Polykit is a delightful Python utility library that focuses on developer happiness and production-ready tools. It provides elegant solutions for common development tasks including logging, environment variable management, file operations, CLI interfaces, and text/time formatting.

Key characteristics:

- Production-proven utilities refined through real-world usage
- Modern Python 3.12+ with comprehensive type hints
- Developer-centric design with clean APIs and intuitive interfaces
- Consistent design philosophy across all components

## Development Commands

### Environment Setup

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
pre-commit install
```

### Code Quality & Linting

```bash
# Run linting with Ruff (with preview features, fixes, and unsafe fixes)
ruff check --config ruff.toml --preview --fix --unsafe-fixes

# Format code with Ruff formatter
ruff format --config ruff.toml --preview

# Run type checking with MyPy
mypy --config-file mypy.ini

# Run all pre-commit hooks manually
pre-commit run --all-files
```

### Building & Packaging

```bash
# Build the package
poetry build

# Publish to PyPI (production)
poetry publish

# Install package in editable mode for development
pip install -e .
```

### Documentation

```bash
# Generate documentation with pdoc
pdoc src/polykit --output-dir docs

# The project uses pdoc for documentation generation, configured in pyproject.toml
```

## Architecture Overview

Polykit is organized into focused modules, each solving specific developer pain points:

### Core Structure

```text
src/polykit/
├── cli/           # Command-line interface utilities
├── core/          # Core utilities (singleton, decorators, etc.)
├── env/           # Environment variable management
├── files/         # File operations and comparison
├── log/           # Logging utilities
├── packages/      # Package version management
├── paths/         # Cross-platform path handling
├── text/          # Text formatting and manipulation
└── time/          # Time parsing and formatting
```

### Major Components

**PolyLog** (`log/`): Context-aware logging with automatic caller detection, datetime formatting, and visual distinction. The logging system is the cornerstone of the library.

**PolyEnv** (`env/`): Declarative environment variable management with hierarchical loading, type conversion, and validation.

**PolyPath** (`paths/`): Cross-platform path handling with user directory integration and app-specific conventions.

**PolyFile** (`files/`): Safe file operations with trash support, natural sorting, and duplicate detection.

**PolyArgs** (`cli/`): Enhanced argparse replacement with intelligent formatting and version integration.

**Text/Time Utilities** (`text/`, `time/`): Battle-tested formatters for text manipulation and human-readable time parsing.

### Design Principles

1. **Class Method Pattern**: Most utilities use class methods to avoid instantiation boilerplate
2. **IDE-Friendly**: Comprehensive type hints and descriptive method names
3. **Error Handling**: Meaningful error messages and graceful failure modes
4. **Production Ready**: Thread-safe, properly tested, and handles edge cases
5. **Cohesive API**: Consistent naming and behavior across components

## Code Style & Standards

### Python Style (from code-style.md and user rules)

- Use modern type hinting (|, list, dict) instead of Union, List, Dict types
- Use f-strings everywhere except in log statements (use %s formatting)
- All log statements must be properly pluralized
- Type hints in code but not in docstrings
- Proper sentence structure and punctuation in all docstrings and log messages
- Arguments and returns should begin with "The" or "A" (e.g., "The list" not "List")

### Docstring Format

```python
"""Summary sentence.

Extended description if needed with proper sentence structure.

Args:
    arg: Description of the argument.

Returns:
    Description of what is returned.

Raises:
    ErrorType: Description of when this error occurs.
"""
```

### Linting Configuration

- Ruff configuration in `ruff.toml` with extensive rule coverage
- Line length: 100 characters
- Target Python 3.12+
- Pre-commit hooks ensure code quality before commits
- MyPy for static type checking

## Development Environment

### Requirements

- Python 3.12+
- Poetry for dependency management
- Pre-commit for code quality hooks
- Ruff for linting and formatting
- MyPy for type checking
- pdoc for documentation generation

### Key Dependencies

- `python-dotenv`: Environment file loading
- `platformdirs`: Cross-platform directory locations
- `send2trash`: Safe file deletion
- `natsort`: Natural sorting
- `python-dateutil`: Date/time parsing
- `requests`: HTTP operations for version checking
- `halo`: Loading indicators

### Development Workflow

1. Changes trigger pre-commit hooks (Ruff, MyPy, basic checks)
2. Post-commit hooks run additional validation
3. Documentation is generated with pdoc
4. Package is built with Poetry and published to PyPI

The library emphasizes developer experience, so any additions should maintain the high standards of API design, type safety, and comprehensive error handling that characterize the existing codebase.
