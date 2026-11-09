# Лабораторна робота №8

**Тема:** Алгебраїчні типи даних по-Python’івськи.  
**Студент:** Хороший Святослав  
**Група:** ФЕП-21с  
**GitHub:** [Dawerly](https://github.com/Dawerly)  
**Варіант 14:** Події системи.

## Модель ADT

У model.py описано чотири незмінні dataclass(frozen=True, slots=True):
- Login(timestamp, user);
- Logout(timestamp, user);
- FileOpened(timestamp, user, path);
- ErrorEvent(timestamp, level, message).

`Event: TypeAlias = Login | Logout | FileOpened | ErrorEvent` — сума варіантів.
`ErrorLevel: TypeAlias = Literal['warning', 'error', 'critical']` обмежує рівні.
Для timestamp потрібне скінченне невід’ємне число. ErrorEvent додатково
перевіряє level під час створення; неправильні значення дають ValueError.
Усі поля мають відповідати анотаціям. Текстові поля — довільні рядки.

`HasTimestamp(Protocol)` оголошує read-only властивість timestamp.
Функція timestamp_of приймає будь-який структурно сумісний об’єкт.
Події не успадковують Protocol. У тесті підходить також сторонній Stamp
із полем timestamp — сумісність підтверджено mypy --strict.

`EventTree: TypeAlias = Event | tuple['EventTree', ...]` додає вкладені
незмінні журнали. Вхід має бути скінченним ациклічним деревом із tuple.
Flatten рекурсивно обходить його зліва направо; глибина обмежена стеком
Python. Список не є варіантом цього ADT.

## Чистий reducer і статистика

`reducer(state, event)` використовує match/case і повертає новий Stats
через dataclasses.replace. Початкові вузли та стан не змінюються.
Операції:
- Login збільшує лічильник і додає користувача у frozenset active_users;
- Logout збільшує лічильник і вилучає користувача з активних;
- FileOpened додає шлях у tuple paths та збільшує files_opened;
- ErrorEvent через вкладений match збільшує warnings/errors/criticals.

Повторні Login враховуються як окремі події, але активний користувач
залишається єдиним елементом множини. Logout невідомого користувача
враховується, не змінюючи множини. FileOpened — запис спостереження,
тому він враховується незалежно від наявності користувача в active_users.
Paths зберігає повтори та порядок. Total — сума шести лічильників.

`last_timestamp` зберігає максимум часу серед оброблених подій або None
для нового порожнього стану. Журнал не пересортовується: active_users
визначається порядком подій у вхідному потоці. Система приймає також
покази часу не за зростанням; максимум перевірено окремим тестом.

`process(journal, initial=None)` згортає flatten(journal) через reduce.
Без initial створюється новий порожній Stats. З initial можна продовжувати
раніше обчислений стан. Порожній журнал повертає початковий незмінний стан.
Чисті функції не викликають час, мережу, файлові операції чи print.

## Друга операція та вичерпність

Pretty.py містить render_event з match для всіх чотирьох подій,
render_journal та render_stats. Вивід активних користувачів сортується,
щоб результат не залежав від порядку frozenset.

У фінальних гілках використано typing.assert_never. Якщо розширити
Event/ErrorLevel і не обробити новий варіант, mypy вкаже на невичерпний
розбір. Для типізованих викликів хибні вузли не допускаються; у тестах
через cast навмисно передано неправильні значення, щоб перевірити
захисну гілку render/flatten.

## Структура

```text
lab08/
  model.py
  evaluator.py
  pretty.py
  main.py
  tests/test_events.py
  README.md
  requirements.txt
  pyproject.toml
  mypy.ini
  pytest.ini
  .gitignore
  report/Lab_08_Khoroshyi.odt
  report/Lab_08_Khoroshyi.pdf
```

## Запуск та перевірки

Потрібен Python 3.11 або новіший (використано typing.assert_never).
Команди виконуються з lab08.

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
python -m pytest -q
python -m mypy --strict .
python -m black --check .
python -m ruff check .
```

Main моделює події, без реального входу в систему чи відкриття файлів.
Вкладений приклад має 7 подій: 2 Login, 1 Logout, 1 FileOpened та по
одній warning/error/critical. Активним залишається Sviatoslav, максимальний
timestamp — 7. Початковий Stats має 0 подій і залишається незмінним.
Повторна обробка з порожнього стану дає такий самий результат.

## Тестування та висновок

Тести покривають усі варіанти ADT й рівні помилки, вкладені журнали,
порожню та одиничну структуру, продовження стану, дублікати, порядок часу,
Protocol без успадкування, заморожені поля, неправильні timestamp/level,
невідомі вузли та текстове представлення.

ADT робить набір подій явним, match/case відокремлює правила кожного
варіанта, а assert_never допомагає підтримувати вичерпність. Незмінний
стан спрощує повторюваність і тести. Статистика зберігає tuple шляхів,
тому кожне його доповнення копіює посилання; повний render також
матеріалізує текст. Це навчальна реалізація для скінченних журналів.

Умова: наданий Lab_08.docx, варіант 14.
