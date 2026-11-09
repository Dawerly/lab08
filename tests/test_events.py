from dataclasses import FrozenInstanceError, dataclass
from typing import cast

import pytest

from evaluator import flatten, process, reducer
from model import (
    ErrorEvent,
    ErrorLevel,
    Event,
    EventTree,
    FileOpened,
    Login,
    Logout,
    Stats,
    timestamp_of,
)
from pretty import render_event, render_journal, render_stats


@pytest.mark.parametrize(
    "event,field",
    [
        (Login(1, "A"), "logins"),
        (Logout(1, "A"), "logouts"),
        (FileOpened(1, "A", "a.txt"), "files_opened"),
        (ErrorEvent(1, "warning", "w"), "warnings"),
        (ErrorEvent(1, "error", "e"), "errors"),
        (ErrorEvent(1, "critical", "c"), "criticals"),
    ],
)
def test_each_variant(event: Event, field: str) -> None:
    original = Stats()
    result = reducer(original, event)
    assert getattr(result, field) == 1 and result.total == 1
    assert original.total == 0 and result is not original
    assert result.last_timestamp == 1


def test_nested_journal_and_sessions() -> None:
    journal: EventTree = (
        Login(1, "A"),
        (Login(2, "B"), (FileOpened(3, "A", "x"),)),
        Logout(4, "B"),
        ErrorEvent(5, "warning", "w"),
    )
    initial = Stats()
    result = process(journal, initial)
    assert result.total == 5 and result.active_users == frozenset({"A"})
    assert result.paths == ("x",) and result.last_timestamp == 5
    assert initial == Stats()
    assert process(journal) == process(journal)
    assert len(tuple(flatten(journal))) == 5


def test_empty_single_and_incremental() -> None:
    assert process(()) == Stats()
    assert render_journal(()) == ""
    initial = process(Login(1, "A"))
    result = process((Logout(2, "A"),), initial)
    assert result.total == 2 and not result.active_users
    assert initial.active_users == frozenset({"A"})


def test_duplicates_and_out_of_order() -> None:
    result = process((Login(10, "A"), Login(2, "A"), Logout(3, "unknown")))
    assert result.logins == 2 and result.logouts == 1
    assert result.active_users == frozenset({"A"})
    assert result.last_timestamp == 10


def test_protocol_without_inheritance() -> None:
    @dataclass(frozen=True)
    class Stamp:
        timestamp: float

    assert timestamp_of(Stamp(12.0)) == 12.0
    assert timestamp_of(Login(1, "A")) == 1


def test_frozen_nodes_and_state() -> None:
    node = Login(1, "A")
    state = process(node)
    with pytest.raises(FrozenInstanceError):
        node.user = "B"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        state.logins = 99  # type: ignore[misc]
    assert state.active_users == frozenset({"A"})


@pytest.mark.parametrize("timestamp", [-1, float("inf"), float("nan")])
def test_invalid_timestamp(timestamp: float) -> None:
    for build in (
        lambda: Login(timestamp, "A"),
        lambda: Logout(timestamp, "A"),
        lambda: FileOpened(timestamp, "A", "x"),
        lambda: ErrorEvent(timestamp, "error", "x"),
    ):
        with pytest.raises(ValueError):
            build()


def test_invalid_level_and_unknown_node() -> None:
    with pytest.raises(ValueError):
        ErrorEvent(1, cast(ErrorLevel, "fatal"), "bad")
    with pytest.raises(AssertionError):
        render_event(cast(Event, object()))
    with pytest.raises(AssertionError):
        tuple(flatten(cast(EventTree, "invalid")))


@pytest.mark.parametrize(
    "event,expected",
    [
        (Login(1, "A"), "t=1 LOGIN A"),
        (Logout(2, "A"), "t=2 LOGOUT A"),
        (FileOpened(3, "A", "x"), "t=3 FILE A: x"),
        (ErrorEvent(4, "error", "bad"), "t=4 ERROR: bad"),
    ],
)
def test_render(event: Event, expected: str) -> None:
    assert render_event(event) == expected
    assert render_journal((event,)) == expected
    assert "Усього подій: 1" in render_stats(process(event))
