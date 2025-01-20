from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from dsutil import LocalLogger, Singleton
from dsutil.db import DatabaseError, QueryResult

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class SQLiteConfig:
    """Configuration for a SQLite database."""

    database: str
    pragmas: dict[str, str | int] | None = None

    def __post_init__(self):
        if self.pragmas is None:
            self.pragmas = {
                "journal_mode": "WAL",
                "synchronous": 1,
                "foreign_keys": 1,
                "cache_size": -64000,
            }


class SQLiteHelper(metaclass=Singleton):
    """Singleton helper class for interacting with SQLite databases."""

    def __init__(self, config: SQLiteConfig | None = None):
        self.config = config
        self.logger = LocalLogger().get_logger()
        self._connection: sqlite3.Connection | None = None

    @property
    def connection(self) -> sqlite3.Connection:
        """Lazy initialization of SQLite connection.

        Raises:
            DatabaseError: If the database connection fails.
        """
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(
                    self.config.database,
                    isolation_level=None,
                    check_same_thread=False,
                )
                self._connection.row_factory = sqlite3.Row

                with self._connection as conn:
                    for pragma, value in self.config.pragmas.items():
                        conn.execute(f"PRAGMA {pragma} = {value}")

            except sqlite3.Error as e:
                self.logger.critical("Failed to initialize database connection: %s", str(e))
                msg = "Failed to initialize SQLite connection."
                raise DatabaseError(msg) from e
        return self._connection

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> QueryResult[dict[str, Any]]:
        """Fetch a single row from the database.

        Args:
            query: The SQL query to execute.
            params: The query parameters as a tuple.

        Raises:
            DatabaseError: If the query fails.
        """
        try:
            with self.connection as conn:
                cur = conn.execute(query, params)
                if row := cur.fetchone():
                    return QueryResult(
                        data=dict(row),
                        affected_rows=cur.rowcount,
                    )
                return QueryResult(data=None, affected_rows=0)
        except sqlite3.Error as e:
            msg = f"Database error: {e!s}"
            raise DatabaseError(msg) from e

    def fetch_many(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> QueryResult[list[dict[str, Any]]]:
        """Fetch multiple rows from the database.

        Args:
            query: The SQL query to execute.
            params: The query parameters as a tuple.

        Raises:
            DatabaseError: If the query fails.
        """
        try:
            with self.connection as conn:
                cur = conn.execute(query, params)
                rows = cur.fetchall()
                return QueryResult(
                    data=[dict(row) for row in rows],
                    affected_rows=cur.rowcount,
                )
        except sqlite3.Error as e:
            msg = f"Database error: {e!s}"
            raise DatabaseError(msg) from e

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> QueryResult[None]:
        """Execute a write operation.

        Args:
            query: The SQL query to execute.
            params: The query parameters as a tuple.

        Raises:
            DatabaseError: If the query fails.
        """
        try:
            with self.transaction() as conn:
                cur = conn.execute(query, params)
                return QueryResult(data=None, affected_rows=cur.rowcount)
        except sqlite3.Error as e:
            msg = f"Database error: {e!s}"
            raise DatabaseError(msg) from e

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for managing database transactions.

        Yields:
            sqlite3.Connection: The database connection.
        """
        with self.connection as conn:
            try:
                conn.execute("BEGIN")
                yield conn
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
