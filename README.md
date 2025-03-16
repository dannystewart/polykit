# dsbase

This is a comprehensive utility library containing tools and helpers refined through years of practical Python development. It includes an advanced logging system, environment variable management, path handling, database interfaces, media processing tools, and various helpers for common tasks. It was originally developed for personal use, but always to high standards with quality and flexibility in mind.

Some of the features include:

- An elegant and sophisticated [`LocalLogger`](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/log/local_logger.py) logging system
- A tool for [comparing and updating code configs](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/configs/code_configs.py) like `ruff.toml` and `mypy.ini`
- Database [helper interfaces](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/db/db_common.py) for [MySQL](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/db/mysql_helper.py) and [SQLite](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/db/sqlite_helper.py)
- A custom [`DSEnv`](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/env/env.py) environment variable manager
- A custom [`DSPaths`](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/paths.py) path manager
- [File helpers](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/files/file_manager.py) for comparing, copying, deleting, and listing files
- [Media helpers](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/media/media_manager.py) for audio and video transcoding with `ffmpeg`
- A generalized [singleton](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/common/singleton.py) metaclass for use in other projects
- Simple classes that can send notifications via [email](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/notifiers/send_mail.py) or [Telegram](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/notifiers/send_telegram.py)
- Various [time](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/time/time.py) parsers and utilities
- Fun [loading animations](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/animation.py)
- An [argparse interface](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/argparser.py) that makes it easier to set column widths
- A simple [diffing tool](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/diff.py)
- Simple helpers for [progress indication](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/progress.py), [shell handling](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/shell.py), and [text manipulation](https://github.com/dannystewart/dsbase/blob/main/src/dsbase/text.py)

The library continues to evolve and expand on a regular basis, so more will come over time.
