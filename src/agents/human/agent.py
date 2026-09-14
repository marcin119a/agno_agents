"""Human hand-off agent definition.

The "human" member of the support Team (`support_team.py`). It answers no
question itself: it calls the `handoff_to_consultant` tool and repeats
the canned reply to the passenger.
"""

from __future__ import annotations

from agno.agent import Agent
from agno.db.base import BaseDb
from agno.models.openai import OpenAIChat

from agents.human.tools import HandoffTools
from config import Settings, create_model

ROLE = "Przejmuje sprawy dotyczące konkretnej rezerwacji, lotu lub reklamacji pasażera"

INSTRUCTIONS = (
    "Jesteś agentem przekazującym sprawy pasażerów linii Example Air do konsultanta. "
    "Nie odpowiadasz merytorycznie i nie masz dostępu do rezerwacji.\n"
    "- Zawsze wywołaj narzędzie handoff_to_consultant: w `question` podaj wiadomość pasażera "
    "słowo w słowo, w `reason` krótki powód (np. 'status konkretnego lotu').\n"
    "- Odpowiedz pasażerowi DOKŁADNIE tekstem zwróconym przez narzędzie — "
    "bez zmian, skrótów ani dopisków."
)


def create_human_agent(
    settings: Settings,
    db: BaseDb | None = None,
) -> Agent:
    """Builds the human hand-off agent."""
    return Agent(
        name="Human Agent",
        role=ROLE,
        model=create_model(settings),
        instructions=INSTRUCTIONS,
        tools=[HandoffTools()],
        db=db,
    )
