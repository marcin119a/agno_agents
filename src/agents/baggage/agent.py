from __future__ import annotations

import sys

from agno.agent import Agent
from agno.db.base import BaseDb
from agno.db.in_memory import InMemoryDb
from config import create_model

from agents.baggage.tools import BaggageTools
from config import Settings

INSTRUCTIONS = (
    "Jesteś asystentem bagażowym linii lotniczej Example Air. "
    "Odpowiadasz po polsku, krótko i uprzejmie.\n"
    "- Opłatę za walizkę zawsze licz narzędziem excess_fee — nie licz jej w głowie.\n"
    "- Jeśli pasażer nie podał wagi, dopytaj o nią."
)


def create_baggage_agent(settings: Settings, db: BaseDb | None = None) -> Agent:
    """Builds the baggage agent — same shape as `agents.faq.agent.create_agent`."""
    return Agent(
        name="Baggage Agent",
        model=create_model(settings),
        instructions=INSTRUCTIONS,
        tools=[BaggageTools()],
        role="Assistant with expertise in baggage handling",
        db=db or InMemoryDb(),
        add_history_to_context=True
    )
