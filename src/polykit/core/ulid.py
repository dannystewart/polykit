"""ULID (Universally Unique Lexicographically Sortable Identifier) implementation.

This module provides a Python port of the Crockford Base32 ULID specification, matching
the Swift implementation in PolyKit. ULIDs are superior to UUIDs for several reasons:
- Lexicographically sortable by timestamp
- 26 characters (vs UUID's 36)
- Crockford Base32 encoding (URL-safe, no ambiguous characters)
- Embedded millisecond timestamp enables time-based queries

Format:
    - 48-bit millisecond timestamp
    - 80-bit randomness
    - Total: 128 bits encoded as 26 Crockford Base32 characters

Example:
    01ARZ3NDEKTSV4RRFFQ69G5FAV
    └─────────┘ └──────────────┘
    Timestamp     Randomness
"""

from __future__ import annotations

import os
import threading
from datetime import UTC, datetime
from typing import ClassVar, NamedTuple


class DecodedULID(NamedTuple):
    """Decoded ULID components."""

    timestamp_ms: int
    random_bytes: bytes


class ULID:
    """ULID generation and encoding/decoding utilities.

    This class provides static methods for ULID operations. For normal ID generation,
    use ULIDGenerator.shared.next() which provides monotonic guarantees.
    """

    LENGTH = 26
    ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

    # Build decode table for fast lookup
    _DECODE_TABLE: ClassVar[dict[int, int]] = {}

    @classmethod
    def _init_decode_table(cls) -> None:
        """Initialize the decode table for Crockford Base32."""
        if cls._DECODE_TABLE:
            return

        # Standard alphabet
        for i, c in enumerate(cls.ALPHABET):
            cls._DECODE_TABLE[ord(c)] = i
            cls._DECODE_TABLE[ord(c.lower())] = i

        # Crockford ambiguous character handling
        cls._DECODE_TABLE[ord("i")] = 1
        cls._DECODE_TABLE[ord("I")] = 1
        cls._DECODE_TABLE[ord("l")] = 1
        cls._DECODE_TABLE[ord("L")] = 1
        cls._DECODE_TABLE[ord("o")] = 0
        cls._DECODE_TABLE[ord("O")] = 0

    @classmethod
    def generate(cls, date: datetime | None = None) -> str:
        """Generate a ULID for a specific timestamp (non-monotonic).

        Prefer ULIDGenerator.shared.next() for normal ID generation, which guarantees
        monotonicity within a process. This API is intended for cases where you want
        the ULID timestamp to match a specific datetime.

        Args:
            date: The timestamp to encode. Defaults to current time.

        Returns:
            A 26-character ULID string.
        """
        if date is None:
            date = datetime.now(UTC)

        timestamp_ms = int(max(0, date.timestamp()) * 1000)
        random_bytes = os.urandom(10)

        return cls.encode(timestamp_ms, random_bytes)

    @classmethod
    def decode(cls, ulid: str) -> DecodedULID | None:
        """Decode a ULID string into its timestamp and random components.

        Args:
            ulid: The ULID string to decode.

        Returns:
            A tuple of (timestamp_ms, random_bytes) or None if invalid.
        """
        if len(ulid) != cls.LENGTH:
            return None

        cls._init_decode_table()

        # Parse base32 digits into 130-bit value (17 bytes, big-endian)
        acc = bytearray(17)

        try:
            for c in ulid:
                value = cls._DECODE_TABLE.get(ord(c))
                if value is None:
                    return None
                cls._shift_left(acc, 5)
                acc[-1] |= value
        except (KeyError, IndexError):
            return None

        # ULID spec prefixes two leading 0 bits, so highest byte should be 0
        if acc[0] != 0:
            return None

        # Extract timestamp (6 bytes) and random (10 bytes)
        bytes_data = bytes(acc[1:17])

        timestamp_ms = 0
        for i in range(6):
            timestamp_ms = (timestamp_ms << 8) | bytes_data[i]

        random_bytes = bytes_data[6:16]

        return DecodedULID(timestamp_ms, random_bytes)

    @classmethod
    def encode(cls, timestamp_ms: int, random_bytes: bytes) -> str:
        """Encode timestamp and randomness into a ULID string.

        Args:
            timestamp_ms: Milliseconds since Unix epoch (48-bit).
            random_bytes: 10 bytes of randomness (80-bit).

        Returns:
            A 26-character ULID string.

        Raises:
            ValueError: If the random bytes are not 10 bytes.
        """
        if len(random_bytes) != 10:
            msg = f"ULID random component must be 10 bytes, got {len(random_bytes)}"
            raise ValueError(msg)

        # Build 16-byte array (6 bytes timestamp + 10 bytes random)
        bytes_data = bytearray(16)

        # 48-bit timestamp, big-endian
        bytes_data[0] = (timestamp_ms >> 40) & 0xFF
        bytes_data[1] = (timestamp_ms >> 32) & 0xFF
        bytes_data[2] = (timestamp_ms >> 24) & 0xFF
        bytes_data[3] = (timestamp_ms >> 16) & 0xFF
        bytes_data[4] = (timestamp_ms >> 8) & 0xFF
        bytes_data[5] = timestamp_ms & 0xFF

        # 80-bit random
        bytes_data[6:16] = random_bytes

        # Encode 128 bits into 26 base32 chars (with 2-bit prefix = 130 bits total)
        output = []
        buffer = 0
        bits_left = 2  # prefix two 0 bits

        for byte in bytes_data:
            buffer = (buffer << 8) | byte
            bits_left += 8

            while bits_left >= 5:
                shift = bits_left - 5
                index = (buffer >> shift) & 0x1F
                output.append(cls.ALPHABET[index])
                bits_left -= 5

                # Mask out consumed bits
                buffer = 0 if bits_left == 0 else buffer & (1 << bits_left) - 1

        if len(output) != cls.LENGTH:
            msg = f"ULID encoding produced {len(output)} chars, expected {cls.LENGTH}"
            raise ValueError(msg)

        return "".join(output)

    @staticmethod
    def _shift_left(bytes_data: bytearray, bits: int) -> None:
        """Shift a byte array left by the specified number of bits (in-place).

        Raises:
            ValueError: If the number of bits is not between 1 and 7.
        """
        if not (0 < bits < 8):
            msg = f"Shift bits must be between 1 and 7, got {bits}"
            raise ValueError(msg)

        carry = 0
        for i in range(len(bytes_data) - 1, -1, -1):
            value = bytes_data[i]
            shifted = (value << bits) | carry
            bytes_data[i] = shifted & 0xFF
            carry = shifted >> 8


class ULIDGenerator:
    """Thread-safe monotonic ULID generator.

    This generator ensures that ULIDs generated within the same millisecond remain
    strictly increasing by incrementing the random component when the timestamp
    doesn't advance.

    Example:
        from polykit.core import generate_ulid

        ulid1 = generate_ulid()
        ulid2 = generate_ulid()  # Guaranteed to sort after ulid1
    """

    # Singleton instance
    _shared: ULIDGenerator | None = None
    _shared_lock = threading.Lock()

    def __init__(self) -> None:
        """Initialize the generator."""
        self._lock = threading.Lock()
        self._last_timestamp_ms = 0
        self._last_random = bytearray(10)

    @classmethod
    def get_shared(cls) -> ULIDGenerator:
        """Get the shared singleton instance."""
        if cls._shared is None:
            with cls._shared_lock:
                if cls._shared is None:
                    cls._shared = cls()
        return cls._shared

    def next(self, date: datetime | None = None) -> str:
        """Generate the next ULID with monotonic guarantees.

        Args:
            date: The timestamp to use. Defaults to current time.

        Returns:
            A 26-character ULID string guaranteed to sort after previously generated ULIDs.
        """
        if date is None:
            date = datetime.now(UTC)

        now_ms = int(max(0, date.timestamp()) * 1000)

        with self._lock:
            if now_ms > self._last_timestamp_ms:
                # Time advanced, use new timestamp and fresh randomness
                self._last_timestamp_ms = now_ms
                self._last_random = bytearray(os.urandom(10))
            else:
                # Same millisecond or clock skew - increment random component
                self._increment_random()

            return ULID.encode(self._last_timestamp_ms, bytes(self._last_random))

    def seed(self, existing_ulid: str) -> None:
        """Seed the generator from an existing ULID.

        This ensures newly generated ULIDs sort after existing ones, even across
        app restarts and clock skew.

        Args:
            existing_ulid: A ULID string to seed from.
        """
        decoded = ULID.decode(existing_ulid)
        if decoded is None:
            return

        with self._lock:
            # Only update if the existing ULID is greater than our current state
            should_replace = False

            if decoded.timestamp_ms > self._last_timestamp_ms:
                should_replace = True
            elif decoded.timestamp_ms == self._last_timestamp_ms:
                # Same timestamp - compare random bytes lexicographically
                should_replace = bytes(self._last_random) < decoded.random_bytes

            if should_replace:
                self._last_timestamp_ms = decoded.timestamp_ms
                self._last_random = bytearray(decoded.random_bytes)

    def _increment_random(self) -> None:
        """Increment the random component as a big-endian 80-bit integer."""
        # Add 1 to the 10-byte random value (big-endian)
        for i in range(9, -1, -1):
            if self._last_random[i] == 0xFF:
                self._last_random[i] = 0
                continue
            self._last_random[i] = (self._last_random[i] + 1) & 0xFF
            return

        # Overflow (extremely unlikely) - reseed with fresh randomness
        self._last_random = bytearray(os.urandom(10))


# Convenience singleton access
_generator_instance: ULIDGenerator | None = None
_generator_lock = threading.Lock()


def get_ulid_generator() -> ULIDGenerator:
    """Get the shared ULIDGenerator instance.

    This is a module-level convenience function for accessing the singleton generator.
    """
    global _generator_instance  # noqa: PLW0603

    if _generator_instance is None:
        with _generator_lock:
            if _generator_instance is None:
                _generator_instance = ULIDGenerator()
    return _generator_instance


# Convenience module-level functions for common operations
def generate_ulid(date: datetime | None = None) -> str:
    """Generate a ULID using the shared generator.

    Args:
        date: The timestamp to use. Defaults to current time.

    Returns:
        A 26-character ULID string.
    """
    return get_ulid_generator().next(date)
