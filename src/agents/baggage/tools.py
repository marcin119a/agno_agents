
from __future__ import annotations

import math

from agno.tools import Toolkit


class BaggageTools(Toolkit):
    """Calculates the excess baggage fee for Example Air."""

    def __init__(self, **kwargs):
        self.free_kg = 23
        self.max_kg = 32
        self.fee_per_kg = 50
        super().__init__(name="baggage", tools=[self.excess_fee], **kwargs)

    def excess_fee(self, weight_kg: float) -> str:
        """Calculates the excess baggage fee for one checked bag.

        Args:
            weight_kg: total weight of the bag in kilograms, e.g. 27.5.
        """
        if weight_kg > self.max_kg:
            return f"Too heavy: a single bag may weigh at most {self.max_kg} kg — it cannot be checked in."
        if weight_kg <= self.free_kg:
            return f"No fee: the bag is within the {self.free_kg} kg allowance."
        started_kg = math.ceil(weight_kg - self.free_kg)
        fee = started_kg * self.fee_per_kg
        return f"Excess baggage fee: PLN {fee} ({started_kg} started kg over {self.free_kg} kg x PLN {self.fee_per_kg})."
