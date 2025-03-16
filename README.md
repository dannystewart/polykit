# dsbase

This is a shared base utility library for my Python scripts and programs.

More documentation is coming soon, but this library includes (in no particular order):

- An elegant and sophisticated [`LocalLogger`](src/dsbase/log/local_logger.py) logging system
- A tool for [comparing and updating code configs](src/dsbase/configs/code_configs.py) like `ruff.toml` and `mypy.ini`
- Database [helper interfaces](src/dsbase/db/db_common.py) for [MySQL](src/dsbase/db/mysql_helper.py) and [SQLite](src/dsbase/db/sqlite_helper.py)
- A custom [`DSEnv`](src/dsbase/env/env.py) environment variable manager
- A custom [`DSPaths`](src/dsbase/paths.py) path manager
- [File helpers](src/dsbase/files/file_manager.py) for comparing, copying, deleting, and listing files
- [Media helpers](src/dsbase/media/media_manager.py) for audio and video transcoding with `ffmpeg`
- A generalized [singleton](src/dsbase/common/singleton.py) metaclass for use in other projects
- Simple classes that can send notifications via [email](src/dsbase/notifiers/send_mail.py) or [Telegram](src/dsbase/notifiers/send_telegram.py)
- Various [time](src/dsbase/time/time.py) parsers and utilities
- Fun [loading animations](src/dsbase/animation.py)
- An [argparse interface](src/dsbase/argparser.py) that makes it easier to set column widths
- A simple [diffing tool](src/dsbase/diff.py)
- Simple helpers for [progress indication](src/dsbase/progress.py), [shell handling](src/dsbase/shell.py), and [text manipulation](src/dsbase/text.py)
