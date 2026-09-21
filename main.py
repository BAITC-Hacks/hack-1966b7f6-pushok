"""Терминальный FAQ-бот с поиском по ключевым словам."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


FAQ_FILE = Path(__file__).with_name("faq.txt")
QUIT_WORDS = {"выход", "exit", "quit"}


@dataclass(frozen=True)
class FaqItem:
    """Одна запись FAQ, загруженная из текстового файла."""

    question: str
    keywords: frozenset[str]
    answer: str


def words(text: str) -> set[str]:
    """Возвращает слова в нижнем регистре, включая русские буквы."""
    return set(re.findall(r"[a-zа-яё0-9]+", text.lower()))


def load_faq(path: Path) -> list[FaqItem]:
    """Читает FAQ в формате полей «Вопрос», «Ключевые слова», «Ответ»."""
    entries: list[FaqItem] = []
    for block in path.read_text(encoding="utf-8").split("---"):
        fields: dict[str, str] = {}
        for line in block.strip().splitlines():
            if ":" not in line:
                continue
            name, value = line.split(":", maxsplit=1)
            fields[name.strip().lower()] = value.strip()

        question = fields.get("вопрос")
        keyword_text = fields.get("ключевые слова")
        answer = fields.get("ответ")
        if not (question and keyword_text and answer):
            raise ValueError(f"Некорректная запись FAQ: {block!r}")

        entries.append(
            FaqItem(question, frozenset(words(keyword_text)), answer)
        )
    return entries


def find_answer(question: str, faq: list[FaqItem]) -> str | None:
    """Ищет запись с наибольшим числом общих с вопросом ключевых слов."""
    question_words = words(question)
    best_item: FaqItem | None = None
    best_score = 0

    for item in faq:
        score = len(question_words & item.keywords)
        if score > best_score:
            best_item = item
            best_score = score

    return best_item.answer if best_item else None


def main() -> None:
    faq = load_faq(FAQ_FILE)
    print("FAQ-бот готов. Задайте вопрос (для выхода: выход).")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДо встречи!")
            return

        if question.lower() in QUIT_WORDS:
            print("До встречи!")
            return
        if not question:
            print("Введите вопрос или напишите «выход».")
            continue

        print(find_answer(question, faq) or "Не знаю.")


if __name__ == "__main__":
    main()
