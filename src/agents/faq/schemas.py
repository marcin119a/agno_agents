"""Structured output of the FAQ agent."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FaqAnswer(BaseModel):
    """Ustrukturyzowana odpowiedź agenta FAQ."""
    answer: str = Field(description="Krótka, uprzejma odpowiedź po polsku.")
    topics: list[str] = Field(description="Tematy z search_faq; [] jeśli brak.")
    found_in_faq: bool = Field(description="Czy odpowiedź znaleziono w FAQ.")


def format_answer(answer: FaqAnswer) -> str:
    """Renders a FaqAnswer for a console user: the text plus the FAQ topics used."""
    if not answer.topics:
        return answer.answer
    return f"{answer.answer}\n[FAQ: {', '.join(answer.topics)}]"
