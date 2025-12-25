"""Supabase logging handler for remote log streaming.

This module provides a custom logging handler that streams log entries to Supabase
in real-time, matching the behavior of the Swift LogRemote implementation.

Logs are buffered in memory and flushed periodically to minimize network overhead.
All network operations happen in a background thread to avoid blocking the main application.

Configuration:
    Set these environment variables:
    - POLYLOG_APP_ID: Your application identifier (required)
    - POLYLOG_SUPABASE_URL: Your Supabase project URL (required)
    - POLYLOG_SUPABASE_KEY: Your Supabase anon key (required)
    - POLYLOG_TABLE: Table name for logs (optional, defaults to "polylogs")

Example:
    from polykit.log import PolyLog

    # Start with remote logging
    logger = PolyLog.get_logger(remote=True)
    logger.info("This log streams to Supabase!")
"""

from __future__ import annotations

import contextlib
import logging
import os
import queue
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from polykit.core.ulid import ULID, generate_ulid


class SupabaseLogHandler(logging.Handler):
    """Logging handler that streams log entries to Supabase.

    This handler buffers log records and flushes them periodically in a background
    thread. Network failures are handled gracefully - logs are dropped if push fails.
    """

    # Buffer configuration
    BUFFER_FLUSH_THRESHOLD = 10
    FLUSH_INTERVAL = 0.15  # seconds

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        app_id: str,
        table_name: str = "polylogs",
    ):
        """Initialize the Supabase log handler.

        Args:
            supabase_url: Supabase project URL.
            supabase_key: Supabase anon key.
            app_id: Application identifier.
            table_name: Table name for logs.

        Raises:
            ImportError: If supabase-py is not installed.
        """
        super().__init__()

        # Import supabase here to avoid import errors if not installed
        try:
            from supabase import Client, create_client
        except ImportError as e:
            msg = "supabase-py is required for remote logging. Install with: pip install supabase"
            raise ImportError(
                msg,
            ) from e

        self.client: Client = create_client(supabase_url, supabase_key)
        self.app_id = app_id
        self.table_name = table_name

        # Device and session identification
        self.device_id = self._get_device_id()
        self.session_id = generate_ulid()

        # Buffering
        self.buffer: queue.Queue[logging.LogRecord] = queue.Queue()
        self._shutdown = threading.Event()

        # Background flush thread
        self.flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.flush_thread.start()

    def emit(self, record: logging.LogRecord) -> None:
        """Queue a log record for processing.

        Args:
            record: The log record to emit.
        """
        with contextlib.suppress(queue.Full):
            self.buffer.put_nowait(record)

    def close(self) -> None:
        """Clean shutdown of the handler."""
        self._shutdown.set()
        self.flush_thread.join(timeout=1.0)

        # Flush remaining entries
        self._flush_buffer()

        super().close()

    def _flush_loop(self) -> None:
        """Background thread that periodically flushes the buffer."""
        while not self._shutdown.is_set():
            self._shutdown.wait(timeout=self.FLUSH_INTERVAL)
            if self.buffer.qsize() >= self.BUFFER_FLUSH_THRESHOLD or not self.buffer.empty():
                self._flush_buffer()

    def _flush_buffer(self) -> None:
        """Flush buffered log entries to Supabase."""
        if self.buffer.empty():
            return

        # Collect all pending entries
        entries: list[logging.LogRecord] = []
        while not self.buffer.empty():
            try:
                entries.append(self.buffer.get_nowait())
            except queue.Empty:
                break

        if not entries:
            return

        # Build records for Supabase
        records = self._build_records(entries)

        # Push to Supabase (with retry)
        self._push_records(records)

    def _build_records(self, entries: list[logging.LogRecord]) -> list[dict[str, Any]]:
        """Build Supabase records from log entries.

        Args:
            entries: Log records to convert.

        Returns:
            List of dictionaries ready for Supabase insert.
        """
        records = []

        for entry in entries:
            # Generate ULID from the log entry's timestamp
            timestamp = datetime.fromtimestamp(entry.created, tz=UTC)
            ulid = ULID.generate(timestamp)

            record: dict[str, Any] = {
                "id": ulid,
                "timestamp": timestamp.isoformat(),
                "level": entry.levelname.lower(),
                "message": entry.getMessage(),
                "device_id": self.device_id,
                "session_id": self.session_id,
                "app_bundle_id": self.app_id,
            }

            # Optional: Add logger name as group identifier
            if entry.name and entry.name != "root":
                record["group_identifier"] = entry.name

            records.append(record)

        return records

    def _push_records(self, records: list[dict[str, Any]]) -> None:
        """Push log records to Supabase.

        Args:
            records: Records to push.
        """
        if not records:
            return

        # Retry once on transient network errors
        last_error = None
        for attempt in range(2):
            try:
                self.client.table(self.table_name).insert(records).execute()
                return  # Success
            except Exception as error:
                last_error = error

                # Check for transient network errors
                error_str = str(error).lower()
                is_transient = any(
                    (keyword in error_str for keyword in ["connection", "timeout", "network"]),
                )

                if is_transient and attempt == 0:
                    # Brief delay before retry
                    import time

                    time.sleep(0.1)
                    continue

                break

        # Log error but don't crash - remote logging is best-effort
        if last_error:
            # Print to stderr to avoid recursion
            import sys

            print(
                f"SupabaseLogHandler: Push failed: {last_error!s}",
                file=sys.stderr,
            )

    @staticmethod
    def _get_device_id() -> str:
        """Get a stable device identifier.

        Tries to use MAC address for hardware-based identification,
        falls back to a persistent ULID stored in the user's home directory.

        Returns:
            A stable device identifier string.
        """
        # Try MAC address first (hardware-based, stable)
        mac_id = SupabaseLogHandler._get_mac_address()
        if mac_id:
            return mac_id

        # Fall back to persistent ULID
        device_id_file = Path.home() / ".polykit_device_id"

        try:
            if device_id_file.exists():
                return device_id_file.read_text().strip()
        except OSError:
            pass

        # Generate new ULID
        new_id = generate_ulid()

        with contextlib.suppress(OSError):
            device_id_file.write_text(new_id)

        return new_id

    @staticmethod
    def _get_mac_address() -> str | None:
        """Get the MAC address of the primary network interface.

        Returns:
            MAC address as a string, or None if unavailable.
        """
        try:
            # Get the UUID based on hardware address
            mac = uuid.getnode()

            # Check if it's a real MAC (not a random fallback)
            if (mac >> 40) % 2:  # Check if multicast bit is set
                return None

            # Format as standard MAC address
            mac_str = f"{mac:012x}"
            return ":".join(mac_str[i : i + 2] for i in range(0, 12, 2))
        except Exception:
            return None

    @classmethod
    def from_env(cls) -> SupabaseLogHandler | None:
        """Create a handler from environment variables.

        Looks for:
        - POLYLOG_APP_ID
        - POLYLOG_SUPABASE_URL
        - POLYLOG_SUPABASE_KEY
        - POLYLOG_TABLE (optional, defaults to "polylogs")

        Returns:
            A configured handler, or None if required env vars are missing.
        """
        app_id = os.environ.get("POLYLOG_APP_ID")
        supabase_url = os.environ.get("POLYLOG_SUPABASE_URL")
        supabase_key = os.environ.get("POLYLOG_SUPABASE_KEY")
        table_name = os.environ.get("POLYLOG_TABLE", "polylogs")

        if not app_id or not supabase_url or not supabase_key:
            return None

        return cls(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            app_id=app_id,
            table_name=table_name,
        )
