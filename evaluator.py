"""Чиста інтерпретація ADT через вичерпний match/case."""

from collections.abc import Iterator
from dataclasses import replace
from functools import reduce
from typing import assert_never

from model import (
    ErrorEvent,
    Event,
    EventTree,
    FileOpened,
    Login,
    Logout,
    Stats,
    timestamp_of,
)


def reducer(state: Stats, event: Event) -> Stats:
    timestamp = timestamp_of(event)
    latest = (
        timestamp
        if state.last_timestamp is None
        else max(timestamp, state.last_timestamp)
    )
    base = replace(state, last_timestamp=latest)
    match event:
        case Login(user=user):
            return replace(
                base, logins=base.logins + 1, active_users=base.active_users | {user}
            )
        case Logout(user=user):
            return replace(
                base, logouts=base.logouts + 1, active_users=base.active_users - {user}
            )
        case FileOpened(path=path):
            return replace(
                base, files_opened=base.files_opened + 1, paths=base.paths + (path,)
            )
        case ErrorEvent(level=level):
            match level:
                case "warning":
                    return replace(base, warnings=base.warnings + 1)
                case "error":
                    return replace(base, errors=base.errors + 1)
                case "critical":
                    return replace(base, criticals=base.criticals + 1)
                case _:
                    assert_never(level)
        case _:
            assert_never(event)


def flatten(journal: EventTree) -> Iterator[Event]:
    match journal:
        case tuple(children):
            for child in children:
                yield from flatten(child)
        case Login() | Logout() | FileOpened() | ErrorEvent():
            yield journal
        case _:
            assert_never(journal)


def process(journal: EventTree, initial: Stats | None = None) -> Stats:
    state = Stats() if initial is None else initial
    return reduce(reducer, flatten(journal), state)
