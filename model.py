"""ADT подій системи, незмінний стан та структурний контракт timestamp."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal, Protocol, TypeAlias

ErrorLevel: TypeAlias = Literal["warning", "error", "critical"]


class HasTimestamp(Protocol):
    @property
    def timestamp(self) -> float: ...


def timestamp_of(event: HasTimestamp) -> float:
    return event.timestamp


def check_timestamp(value: float) -> None:
    if not isfinite(value) or value < 0:
        raise ValueError("timestamp має бути скінченним невід'ємним числом")


@dataclass(frozen=True, slots=True)
class Login:
    timestamp: float
    user: str

    def __post_init__(self) -> None:
        check_timestamp(self.timestamp)


@dataclass(frozen=True, slots=True)
class Logout:
    timestamp: float
    user: str

    def __post_init__(self) -> None:
        check_timestamp(self.timestamp)


@dataclass(frozen=True, slots=True)
class FileOpened:
    timestamp: float
    user: str
    path: str

    def __post_init__(self) -> None:
        check_timestamp(self.timestamp)


@dataclass(frozen=True, slots=True)
class ErrorEvent:
    timestamp: float
    level: ErrorLevel
    message: str

    def __post_init__(self) -> None:
        check_timestamp(self.timestamp)
        if self.level not in {"warning", "error", "critical"}:
            raise ValueError("Невідомий рівень помилки")


Event: TypeAlias = Login | Logout | FileOpened | ErrorEvent
EventTree: TypeAlias = Event | tuple["EventTree", ...]


@dataclass(frozen=True, slots=True)
class Stats:
    logins: int = 0
    logouts: int = 0
    files_opened: int = 0
    warnings: int = 0
    errors: int = 0
    criticals: int = 0
    active_users: frozenset[str] = frozenset()
    paths: tuple[str, ...] = ()
    last_timestamp: float | None = None

    @property
    def total(self) -> int:
        return (
            self.logins
            + self.logouts
            + self.files_opened
            + self.warnings
            + self.errors
            + self.criticals
        )
