"""Демонстрація варіанта 14, без реального входу чи читання файлів."""

from evaluator import process
from model import ErrorEvent, EventTree, FileOpened, Login, Logout, Stats
from pretty import render_journal, render_stats


def main() -> None:
    journal: EventTree = (
        Login(1, "Sviatoslav"),
        (
            FileOpened(2, "Sviatoslav", "report.odt"),
            ErrorEvent(3, "warning", "slow task"),
        ),
        (Login(4, "Guest"), (ErrorEvent(5, "error", "timeout"),)),
        Logout(6, "Guest"),
        ErrorEvent(7, "critical", "service unavailable"),
    )
    original = Stats()
    result = process(journal, original)
    print("=== ПОДІЇ СИСТЕМИ | ВАРІАНТ 14 ===")
    print(render_journal(journal))
    print("--- Статистика ---")
    print(render_stats(result))
    print("Початковий стан, подій:", original.total)
    print("Повторний запуск дає той самий результат:", process(journal) == result)


if __name__ == "__main__":
    main()
