from __future__ import annotations

from typing import Callable, List

from agno.tools import Toolkit

from agents.faq.knowledge_base import FAQ


class HandoffTools(Toolkit):
    """Produces the hand-off reply for the passenger.

    Exposed as a tool so an *agent* can run it: a `Team`'s members must be
    agents, not plain functions.
    """

    def __init__(self, **kwargs):
        tools: List[Callable] = [self.handoff_to_consultant]
        super().__init__(name="handoff", tools=tools, **kwargs)

    def handoff_to_consultant(self, question: str, reason: str) -> str:
        """Hands the passenger's question over to a human consultant.

        Args:
            question: The passenger's message, verbatim.
            reason: Short reason why a human is needed, e.g.
                "status konkretnego lotu" or "reklamacja biletu".

        Returns:
            The reply to send to the passenger, word for word.
        """
        return f"To pytanie wymaga kontaktu z konsultantem ({reason}).\n\n{FAQ['helpline contact']}"
