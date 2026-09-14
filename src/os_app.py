from __future__ import annotations

import sys

from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from agno.tracing import setup_tracing

from agents.faq.agent import create_faq_agent
from agents.human.agent import create_human_agent
from config import Settings

settings = Settings()
# A persistent db (rather than the CLI's ephemeral InMemoryDb) so sessions,
# metrics and traces survive restarts, and AgentOS control-plane features
# like Service Accounts (which need a real db) work.
db = SqliteDb(db_file="faq_agent_os.db")

setup_tracing(db=db)
faq_agent = create_faq_agent(settings, db=db)
human_agent = create_human_agent(settings, db=db)


agent_os = AgentOS(
    name="faq-agent",
    agents=[faq_agent, human_agent],
    teams=[],
    db=db,
)
app = agent_os.get_app()


def main() -> None:
    if not settings.openai_api_key:
        sys.exit(
            "Missing API key. Set OPENAI_API_KEY in the .env file in the working directory\n"
            "(or set the OPENAI_API_KEY environment variable)."
        )
    agent_os.serve(app="os_app:app", reload=True)


if __name__ == "__main__":
    main()
