from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, MutableMapping
from typing import Any


class AttrDict(MutableMapping[str, Any]):
    """A dictionary that allows for attribute-style access with nested merging."""

    def __init__(self, *args: Mapping[str, Any] | Iterable[tuple[str, Any]], **kwargs: Any):
        self._data: dict[str, Any] = {}
        self.update(dict[str, Any](*args, **kwargs))

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = self._convert(value)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"AttrDict({self._data})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AttrDict):
            return self._data == other._data
        if isinstance(other, dict):
            return self._data == other
        return False

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as e:
            msg = f"'AttrDict' object has no attribute '{name}'"
            raise AttributeError(msg) from e

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_data":
            super().__setattr__(name, value)
        else:
            self[name] = value

    def __dir__(self) -> list[str]:
        return list[str](set[str](super().__dir__()) | {str(k) for k in self._data})

    def __or__(self, other: Mapping[str, Any] | Iterable[tuple[str, Any]] | None) -> AttrDict:
        """Implement the | operator for AttrDict with nested merging."""
        if other is None:
            return self.copy()

        result = self.copy()
        other_dict = dict[str, Any](other)

        for key, value in other_dict.items():
            current = result._data.get(key)
            if isinstance(current, AttrDict) and isinstance(value, (dict, AttrDict)):
                result._data[key] = current | AttrDict(value)
            else:
                result._data[key] = self._convert(value)

        return result

    def __ror__(self, other: Mapping[str, Any] | Iterable[tuple[str, Any]] | None) -> AttrDict:
        """Implement reverse | operator for AttrDict with nested merging."""
        return self.copy() if other is None else AttrDict(other) | self

    @classmethod
    def _convert(cls, value: Any) -> Any:
        if isinstance(value, Mapping) and not isinstance(value, AttrDict):
            return cls(value)
        if isinstance(value, list):
            return [cls._convert(v) for v in value]
        return value

    def to_dict(self) -> dict[str, Any]:
        """Convert AttrDict to a regular dictionary recursively."""

        def _to_dict(value: Any) -> Any:
            if isinstance(value, AttrDict):
                return value.to_dict()
            if isinstance(value, list):
                return [_to_dict(v) for v in value]
            return value

        return {k: _to_dict(v) for k, v in self._data.items()}

    def copy(self) -> AttrDict:
        """Return a shallow copy of the AttrDict."""
        return AttrDict(self._data)

    def deep_copy(self) -> AttrDict:
        """Return a deep copy of the AttrDict."""
        from copy import deepcopy

        return AttrDict(deepcopy(self._data))

    def __contains__(self, key: object) -> bool:
        return key in self._data
