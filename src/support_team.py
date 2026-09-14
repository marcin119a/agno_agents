import sys

from agno.agent import Agent
from agno.db.base import BaseDb
from agno.models.base import Model
from agno.models.openai import OpenAIChat
from config import create_model
from agno.team import Team, TeamMode

from agents.faq.agent import create_faq_agent
from agents.faq.schemas import FaqAnswer
from agents.human.agent import create_human_agent
from config import Settings
from agno.db.sqlite import SqliteDb

TEAM_INSTRUCTIONS = (
    "Jesteś recepcją obsługi klienta linii lotniczej Example Air.\n"
    "- Sprawy dotyczące konkretnej rezerwacji, lotu, biletu lub reklamacji pasażera "
    "kieruj do Human Agent.\n"
    "- Wszystkie pozostałe pytania (zasady, opłaty, procedury) kieruj do FAQ Agent.\n"
)


def create_support_team(
    settings: Settings,
    db: BaseDb | None = None,
    faq_agent: Agent | None = None,
    human_agent: Agent | None = None,
    leader_model: Model | None = None,
) -> Team:
    """Builds the leader -> (FAQ Agent | Human Agent) team.
    """
    faq_agent = faq_agent or create_faq_agent(settings, db=db)
    human_agent = human_agent or create_human_agent(settings, db=db)

    leader_model = leader_model or create_model(settings)

    return Team(
        name="Support Team",
        mode=TeamMode.route,
        model=leader_model,
        members=[faq_agent, human_agent],
        instructions=TEAM_INSTRUCTIONS,
        determine_input_for_members=False,
        db=db,
    )



def answer_text(content: object) -> str:
    """Flattens a member's reply to plain text.

    In route mode the team returns the member's content as-is: a
    `FaqAnswer` from the FAQ Agent, a string from the other members.
    """
    if isinstance(content, FaqAnswer):
        return content.answer
    return str(content)


def ask(question: str, settings: Settings | None = None, db: BaseDb | None = None) -> str:
    """Runs the support team and returns the chosen member's answer as text."""
    settings = settings or Settings()
    team = create_support_team(settings, db=db)
    return answer_text(team.run(question).content)



def main() -> None:
    settings = Settings()
    db = SqliteDb(db_file="faq_agent_os.db")

    if not settings.openai_api_key:
        sys.exit("Missing API key. Set OPENAI_API_KEY in the .env file.")
    question = " ".join(sys.argv[1:]) or "Ile kosztuje nadbagaż?"
    print(ask(question, settings=settings, db=db))


if __name__ == "__main__":
    main()
