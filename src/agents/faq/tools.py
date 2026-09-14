"""Tools exposed to the agent."""

from __future__ import annotations

from typing import Callable, List

from agno.tools import Toolkit

from agents.faq import knowledge_base


class FaqTools(Toolkit):
    """Searches the airline FAQ knowledge base."""
    def __init__(self, **kwargs):
        tools: List[Callable] = [self.search_faq]
        super().__init__(name="faq", tools=tools, **kwargs)

    def search_faq(self, query: str) -> str:
        """Searches the airline FAQ knowledge base.

        Args:
            query: Keywords, e.g. "carry-on baggage dimensions"
                or "ticket refund".

        Returns:
            Matching FAQ entries, or the list of available topics when
            nothing matches.
        """
        return knowledge_base.search(query)
