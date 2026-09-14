"""FAQ agent definition."""

from __future__ import annotations

from agno.agent import Agent
from agno.db.base import BaseDb
from agno.db.in_memory import InMemoryDb

from config import Settings, create_model
from agents.faq.schemas import FaqAnswer
from agents.faq.tools import FaqTools

INSTRUCTIONS = (
    "Jesteś asystentem obsługi klienta linii lotniczej Example Air. "
    "Odpowiadasz po polsku, krótko i uprzejmie.\n"
    "Zasady:\n"
    "- Zanim odpowiesz na pytanie o zasady przewozu, opłaty czy procedury, "
    "zawsze sprawdź bazę FAQ narzędziem search_faq.\n"
    "- Baza FAQ jest po angielsku — szukaj angielskich słów kluczowych, "
    "a pasażerowi odpowiadaj po polsku.\n"
    "- Odpowiadaj wyłącznie na podstawie informacji z FAQ. Nie wymyślaj "
    "cen, limitów ani procedur, których tam nie ma.\n"
    "- Jeśli FAQ nie zawiera odpowiedzi, powiedz to wprost i skieruj "
    "pasażera na infolinię (temat 'helpline contact').\n"
    "- Nie masz dostępu do rezerwacji pasażerów — sprawy indywidualne "
    "(np. status konkretnego lotu) kieruj na infolinię.\n"
    "- Odpowiadasz w ustalonej strukturze: `answer` to tekst dla pasażera, "
    "`topics` to tematy FAQ, z których korzystałeś, a `found_in_faq` mówi, "
    "czy odpowiedź pochodzi z FAQ."
)

ROLE = "Odpowiada na ogólne pytania o zasady, opłaty i procedury z bazy FAQ"

def create_faq_agent(settings: Settings, db: BaseDb | None = None) -> Agent:
    """
    Builds the FAQ agent with the configured model and tools.
    """
    return Agent(
        name="FAQ Agent",
        model=create_model(settings),
        role=ROLE,
        instructions=INSTRUCTIONS,
        tools=[FaqTools()],
        output_schema=FaqAnswer,
        use_json_mode=settings.model_provider == "ollama",
        db=db or InMemoryDb(),
        add_history_to_context=True,
    )
