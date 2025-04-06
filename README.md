# Polykit

[![PyPI version](https://img.shields.io/pypi/v/polykit.svg)](https://pypi.org/project/polykit/)
[![Python versions](https://img.shields.io/pypi/pyversions/polykit.svg)](https://pypi.org/project/polykit/)
[![PyPI downloads](https://img.shields.io/pypi/dm/polykit.svg)](https://pypi.org/project/polykit/)
[![License](https://img.shields.io/pypi/l/polykit.svg)](https://github.com/dannystewart/polykit/blob/main/LICENSE)

Every developer has a collection of utilities they've refined over years of solving the same problems again and again. Polykit is that collection—polished, perfected, and packaged for your enjoyment.

"*Another* utility library?" I already hear you asking. But don't close the tab just yet! What sets Polykit apart isn't just the functionality it provides but the thought behind each implementation. These are tools born from years of solving real-world problems, used in production but refined as a passion.

If you're managing environment variables, handling paths across different operating systems, formatting text for human consumption, building command-line interfaces, or just want a really nice logger, Polykit provides elegant solutions that just work, often in ways you didn't realize you needed until you experience them.

Polykit doesn't try to be everything to everyone. Instead, it focuses on doing common tasks extraordinarily well, with an emphasis on developer happiness and code that's a pleasure to use.

## Features

### `PolyLog`: Sophisticated Logging with Personality

Forget everything you know about boring, hard-to-configure logging systems. `PolyLog` is more than just another logger—it makes your application's internal dialogue clear, informative, and a pleasure to read. It's the first thing I add to any new project.

- **Context-Aware**: Automatically detects caller class and module names.
- **Time-Intelligent**: Formats datetime objects into human-readable strings.
- **Visually Distinct**: Color-coded by log level for instant visual priority assessment.
- **Exception-Friendly**: Built-in context managers and decorators for elegant error handling.
- **Configurable**: From minimalist to detailed logging formats with a single parameter.
- **Production-Ready**: Rotating file handlers, thread safety, and proper log level management.

```python
# Create a smart, context-aware logger
logger = PolyLog.get_logger()  # Automatically detects class/module name!

# Rich, informative logs with just the right amount of detail
logger.info("Processing %s items in background task.", count)
logger.warning("API rate limit at %s%%, consider throttling requests.", usage)

# Datetime objects automatically formatted into human-readable text
logger.info("Next maintenance scheduled for %s.", datetime.now() + timedelta(days=7))
# Output: "Next maintenance scheduled for next Tuesday at 3:45 PM"

# Elegant error handling with context managers
with PolyLog.catch(logger, "Failed during data processing"):
    process_complex_data()  # Any exceptions are beautifully logged
```

---

### `PolyEnv`: Environment Variables, Elevated

Environment configuration shouldn't be a source of frustration. `PolyEnv` transforms environment variables from a necessary evil into a delightful part of your application.

- **Hierarchical Loading**: Automatically loads from multiple `.env` files with smart precedence rules.
- **Type Conversion**: Transforms environment strings to Python types (`int`, `bool`, etc.) automatically.
- **Smart Boolean Handling**: Understands various truthy/falsey formats (`yes`, `1`, `true`, `on`, etc.).
- **Attribute Access**: Clean `env.VARIABLE_NAME` syntax with full IDE autocompletion support.
- **Validation Framework**: Ensure all required variables are present before your app runs.
- **Secret Protection**: Mask sensitive values in logs and debug output.
- **Sensible Defaults**: Set fallback values that make sense for your application.

```python
# Create your environment manager
env = PolyEnv()

# Declare your configuration needs
env.add_var("API_KEY", required=True, secret=True)
env.add_var("MAX_CONNECTIONS", default="10", var_type=int)
env.add_bool("ENABLE_CACHE", default=True)
env.add_var("UPLOAD_DIR", default="/tmp/uploads")

# Access variables with clean, IDE-friendly syntax
api_key = env.API_KEY
max_conn = env.MAX_CONNECTIONS  # Automatically converted to int
if env.ENABLE_CACHE:
    cache_dir = Path(env.UPLOAD_DIR) / "cache"

# Validate all variables at once on startup
try:
    env.validate_all()
    print("Environment configured correctly!")
except ValueError as e:
    print(f"Configuration error: {e}")
```

---

### `PolyPath`: Navigate File Systems with Confidence

`PolyPath` brings sanity to file management across operating systems and eliminates an entire class of cross-platform headaches:

- **Cross-Platform Consistency**: Write once, run anywhere with the right paths for each OS.
- **Automatic Directory Creation**: Parent directories are created as needed, eliminating boilerplate `mkdir` calls.
- **Environment-Aware**: Respects platform conventions and environment variables.
- **User Directory Integration**: Seamless access to Documents, Downloads, Pictures and more.
- **macOS App Domain Support**: Proper bundle identifiers (com.developer.appname) for macOS conventions.
- **Clean, Intuitive API**: Methods like `from_config()` and `from_cache()` make code self-documenting.

```python
# Create a path manager for your app
paths = PolyPath("my_awesome_app", app_author="YourName")

# Access platform-specific directories with a consistent API
config_file = paths.from_config("settings.json")   # ~/.config/my_awesome_app/settings.json on Linux
cache_dir = paths.from_cache("api_responses")      # ~/Library/Caches/my_awesome_app/api_responses on macOS
log_path = paths.from_log("debug.log")             # Appropriate log location on any platform

# Work with user directories naturally
docs = paths.from_documents("Reports", "2023")     # ~/Documents/Reports/2023
music = paths.from_music("Playlists")              # ~/Music/Playlists
downloads = paths.from_downloads("temp.zip")       # ~/Downloads/temp.zip

# Parent directories are automatically created when needed
paths.from_data("databases").mkdir(exist_ok=True)  # No need for parents=True
```

---

### `PolyFile`: File Operations Simplified

`PolyFile` brings elegance and safety to everyday file operations:

- **Intuitive Class Methods**: Access functionality through clean, descriptive methods without instantiation.
- **Trash-Aware Deletion**: Files go to the recycle bin instead of disappearing forever.
- **Natural Sorting**: "file10.txt" come after "file2.txt", not before.
- **Smart Filtering**: Combine extension filters, exclusion patterns, and recursion options.
- **Duplicate Detection**: Find identical files with efficient SHA-256 hashing.
- **Overwrite Protection**: Prevent accidental data loss with built-in safeguards.
- **Logger Integration**: All operations can report their status through your logger (hopefully `PolyLog`!).

```python
# Find files with smart filtering and natural sorting
image_files = PolyFile.list(
    Path("~/Pictures"),
    extensions=["jpg", "png"],
    recurse=True,
    exclude=["*thumbnail*"],
    hidden=False
)

# Safe deletion with trash bin support
deleted, failed = PolyFile.delete(outdated_files, logger=logger)

# Copy with overwrite protection
PolyFile.copy(source_file, destination, overwrite=False)

# Find and manage duplicate files
dupes = PolyFile.find_dupes_by_hash(files)
for hash_value, file_list in dupes.items():
    # Keep the first file, delete the rest
    PolyFile.delete(file_list[1:])
```

---

### `PolyDiff`: Elegant File Comparison

`PolyDiff` makes text and file comparison clean and intuitive by bringing the power of unified diff to your Python applications with an API that's both powerful and pleasant to use:

- **Visual Clarity**: Color-coded output makes changes immediately apparent.
- **Multiple Output Styles**: Choose between colored, simple, or minimal output formats.
- **Structured Results**: Get programmatic access to additions, deletions, and full changes.
- **Content or File Comparison**: Compare files directly or arbitrary text content.
- **Context-Aware**: Includes filenames and surrounding lines for better understanding.
- **Logger Integration**: Output changes through your logger (and you know which one to use).
- **Clean Formatting**: Consistent spacing and alignment for better readability.

```python
# Compare two files with colorized output
result = PolyDiff.files(Path("config_old.json"), Path("config_new.json"), style=DiffStyle.COLORED)

# Compare strings with context
changes = PolyDiff.content(old_text, new_text, filename="user_profile.json")

# Analyze the changes programmatically
if changes.has_changes:
    print(f"Found {len(changes.additions)} additions and {len(changes.deletions)} deletions")

    # Access specific changes
    for added_line in changes.additions:
        process(added_line)
```

---

### `PolyArgs`: Command-Line Interfaces That Look Professional

`PolyArgs` transforms the standard `argparse` experience into something you'll actually enjoy:

- **Write Once, Use Twice**: Maintain comprehensive module documentation while keeping help text concise with `lines=1` to show only the first paragraph.
- **Intelligent Column Widths**: Automatically calculates optimal formatting based on your arguments.
- **Version Integration**: Automatically adds `--version` that reports detailed package information.
- **Consistent Text Formatting**: Help text with proper capitalization and paragraph structure.

```python
# Use your full module docstring but only show the first paragraph in help text
"""Process and analyze data files with advanced filtering options.

This module provides tools for loading, filtering, and transforming data
from various file formats. It supports CSV, JSON, and XML inputs.

Examples:
    process.py --input data.csv --output results.json
    process.py --filter "created_at > 2023-01-01" --format pretty
"""

# Only the first paragraph appears in help text!
parser = PolyArgs(description=__doc__, lines=1)

# Add arguments with automatic formatting
parser.add_argument("--input", "-i", help="Input file path")
parser.add_argument("--output", "-o", help="Output file path")
parser.add_argument("--verbose", "-v", action="store_true", help="Enable detailed output")

args = parser.parse_args()
```

---

### `VersionChecker`: Package Version Intelligence

Managing package versions shouldn't require detective work. `VersionChecker` gives you visibility into your dependencies—what's installed, where it came from, and what updates are available.

- **Multi-Source Intelligence**: Check versions against PyPI, GitHub, GitLab, or any Git repository.
- **Dev Environment Awareness**: Detects when you're running from source or in editable mode.
- **Update Awareness**: Easily compare installed versions against latest available releases.
- **Smart Package Detection**: Determine package names from running scripts and entry points.
- **Rich Version Information**: Get structured data about versions, sources, and update status.
- **No Configuration**: Works out-of-the-box with sensible defaults for most scenarios.

```python
# Quick version check with smart detection
checker = VersionChecker()
info = checker.check_package("requests")

print(info)  # "requests v2.28.1 (pypi)"

# Check for updates against PyPI
if info.update_available:
    print(f"Update available: v{info.latest}")

# Check against GitHub releases
github_info = checker.check_package(
    "fastapi",
    source=PackageSource.GITHUB,
    owner="tiangolo"
)

# Detect development installations
if checker.is_development_version("my_package"):
    print("Using development version")

# Automatic package detection for CLI tools
current_package = VersionChecker.get_caller_package_name()
version_info = checker.check_package(current_package)
```

---

### `Text` and `Time`: The Swiss Army Knives of Formatting

Stop wrestling with text manipulation and datetime formatting. Polykit's `Text` and `Time` utility classes handle everything from pluralization to timezone-aware parsing.

- **Battle-Tested Reliability**: The `split_message()` function alone represents nearly a year of refinement through production use. It can survive almost anything—and it has.
- **Edge Case Mastery**: Handles tricky scenarios like nested code blocks and special characters with grace and reliability.
- **No More Pluralization Bugs**: Automatically handle singular/plural forms for cleaner messages.
- **Smart Text Handling**: Truncate, format, and manipulate text with intelligent defaults.
- **Human-Readable Times**: Parse and format dates and times in natural language.
- **Timezone Intelligence**: Automatic timezone detection and handling.

```python
# Smart pluralization that just works
print(f"Found {Text.plural('file', 5, with_count=True)}")  # "Found 5 files"
print(f"Processing {Text.plural('class', 1, with_count=True)}")  # "Processing 1 class"

# Intelligent truncation with context preservation
long_text = "This is a very long text that needs to be shortened while preserving meaning..."
print(Text.truncate(long_text, chars=50))  # Ends at sentence or word boundary
print(Text.truncate(long_text, from_middle=True))  # Preserves start and end

# Terminal colors made simple
Text.print_color("Success!", color="green", style=["bold"])
Text.print_color("Error!", color="red", style=["bold", "underline"])

# Parse human-friendly time expressions
meeting = Time.parse("3pm tomorrow")
deadline = Time.parse("Friday at 5")

# Format datetimes in a natural way
print(Time.get_pretty_time(meeting))  # "tomorrow at 3:00 PM"
print(Time.get_pretty_time(deadline))  # "Friday at 5:00 PM"

# Convert durations to readable text
print(Time.convert_sec_to_interval(3725))  # "1 hour, 2 minutes and 5 seconds"
```

These utilities solve real-world text and time challenges and have been hardened against some of the nastiest edge cases. Why spend months solving these problems when you don't have to?

---

### Honorable Mention

Polykit also has a few more tricks up its sleeve for common development challenges.

#### `Singleton` Metaclass

Singletons are deceptively difficult to implement correctly, but `Singleton` handles it all:

- **Truly Thread-Safe**: Properly handles race conditions during instantiation with class-level locks.
- **IDE-Friendly**: Designed to preserve method visibility and code intelligence in IDEs.
- **No Boilerplate**: Implement the pattern with a single metaclass declaration.
- **Transparent Usage**: No special methods needed to access the singleton instance.
- **Type-Hinting Compatible**: Works seamlessly with static type checkers and modern Python typing.

#### And even more:

- Gracefully handle keyboard interrupts with the `@handle_interrupt()` decorator.
- Auto-retry operations that might fail transiently with the `@retry_on_exception()` decorator.
- Check permissions with `is_root_user()` and elevate with `acquire_sudo()` if needed.
- Get user confirmation with a single keypress using `confirm_action()`.
- Use stylish loading indicators like spinners with the `with_spinner()` context manager…
- …or use Walking Man `<('-'<)`. (Honestly, he alone is worth the download.)

---

## Why Polykit?

When you use Polykit, you're benefiting from:

- **Reliability** that comes from components used in real production environments.
- **Developer-centric design** that prioritizes clean APIs and intuitive interfaces.
- **Attention to edge cases** that others often overlook or ignore.
- **Consistent design philosophy** across all components for a cohesive experience.
- **Modern Python practices** including comprehensive type hints and up-to-date language features.

Everything you see here was created to solve genuine problems in day-to-day development, so it prioritizes developer experience with IDE-friendly interfaces, meaningful error messages, sensible defaults, and comprehensive (if still evolving) documentation. Every detail has been considered from the perspective of the person who will actually use these tools (because that person was me!).

Polykit strives to be intuitive, handle complexity behind clean interfaces, and integrate seamlessly with each other and with your existing code. It's a toolkit from a developer who refuses to accept "good enough" and always goes for "really f*cking good." Part of that means the work is never finished—Polykit is still being actively developed, with new tools added and existing tools refined on a regular basis.

I'd love it if you gave Polykit a try, and I'd love even more if it helps you like it's helped me! If you're ready to bring some joy to your Python development, you know the way:

```bash
pip install polykit
```

### License

Polykit is licensed under the [LGPL-3.0 license](https://github.com/dannystewart/polykit/blob/main/LICENSE). Contributions and feedback are welcome!
