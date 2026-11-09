"""Чисте текстове представлення подій і підсумків."""

from typing import assert_never

from evaluator import flatten
from model import ErrorEvent, Event, EventTree, FileOpened, Login, Logout, Stats


def render_event(event: Event) -> str:
    match event:
        case Login(timestamp=t, user=user):
            return f"t={t:g} LOGIN {user}"
        case Logout(timestamp=t, user=user):
            return f"t={t:g} LOGOUT {user}"
        case FileOpened(timestamp=t, user=user, path=path):
            return f"t={t:g} FILE {user}: {path}"
        case ErrorEvent(timestamp=t, level=level, message=message):
            return f"t={t:g} {level.upper()}: {message}"
        case _:
            assert_never(event)


def render_journal(journal: EventTree) -> str:
    return "\n".join(map(render_event, flatten(journal)))


def render_stats(state: Stats) -> str:
    return (
        f"Усього подій: {state.total}\n"
        f"Login: {state.logins}; Logout: {state.logouts}; файлів: {state.files_opened}\n"
        f"warning: {state.warnings}; error: {state.errors}; critical: {state.criticals}\n"
        f"Активні користувачі: {', '.join(sorted(state.active_users)) or 'немає'}\n"
        f"Максимальний timestamp: {state.last_timestamp}"
    )
