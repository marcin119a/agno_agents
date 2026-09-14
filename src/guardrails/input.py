from __future__ import annotations

from typing import Iterable, Union

from agno.exceptions import CheckTrigger, InputCheckError
from agno.guardrails import BaseGuardrail, PIIDetectionGuardrail, PromptInjectionGuardrail

POLISH_PII_PATTERNS: dict[str, str] = {
    "PESEL": r"(?<!\d)\d{11}(?!\d)",
    "Polish phone": r"(?<!\d)(?:\+48[\s-]?)?\d{3}[\s-]?\d{3}[\s-]?\d{3}(?!\d)",
    "NIP": r"(?<!\d)\d{9}(?!\d)",
    "REGON": r"(?<!\d)\d{10}(?!\d)"
}

from agno.run.agent import RunInput
from agno.run.team import TeamRunInput

INJECTION_REFUSAL = (
    "Nie mogę wykonać tej prośby. Chętnie odpowiem na pytania dotyczące "
    "lotów, bagażu, odprawy i innych usług Example Air."
)

POLISH_INJECTION_PATTERNS: list[str] = [
    "zignoruj poprzednie instrukcje",
    "zignoruj wcześniejsze instrukcje",
    "zignoruj swoje instrukcje",
    "zignoruj wszystkie instrukcje",
    "zapomnij o instrukcjach",
    "zapomnij wszystko",
    "od teraz jesteś",
    "udawaj, że jesteś",
    "udawaj że jesteś",
    "wciel się w rolę",
    "tryb deweloperski",
    "tryb developerski",
    "prompt systemowy",
    "pokaż swoje instrukcje",
    "pokaż swój prompt",
]

class MaxInputLengthGuardrail(BaseGuardrail):
    """Rejects messages longer than `max_chars` (cost control, crude anti-abuse)."""

    def __init__(self, max_chars: int = 2000):
        self.max_chars = max_chars

    def check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        length = len(run_input.input_content_string())
        if length > self.max_chars:
            raise InputCheckError(
                f"Wiadomość jest za długa ({length} znaków, limit {self.max_chars}). "
                "Proszę ją skrócić.",
                check_trigger=CheckTrigger.INPUT_NOT_ALLOWED,
                additional_data={"length": length, "max_chars": self.max_chars},
            )

    async def async_check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        self.check(run_input)


class PolishPromptInjectionGuardrail(PromptInjectionGuardrail):
    """agno's keyword guardrail extended with Polish patterns and a Polish refusal."""

    def __init__(self, extra_patterns: Iterable[str] = ()):
        super().__init__()  # loads agno's English defaults
        self.injection_patterns = self.injection_patterns + POLISH_INJECTION_PATTERNS + list(extra_patterns)

    def check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        text = run_input.input_content_string().lower()
        hits = [pattern for pattern in self.injection_patterns if pattern in text]
        if hits:
            raise InputCheckError(
                INJECTION_REFUSAL,
                check_trigger=CheckTrigger.PROMPT_INJECTION,
                additional_data={"patterns": hits},
            )

    async def async_check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        self.check(run_input)

def pii_masking_guardrail() -> PIIDetectionGuardrail:
    return PIIDetectionGuardrail(mask_pii=True, custom_patterns=POLISH_PII_PATTERNS)

def default_input_guardrails(*, mask_pii: bool = True, max_chars: int = 2000) -> list[BaseGuardrail]:
    guardrails: list[BaseGuardrail] = [
        MaxInputLengthGuardrail(max_chars=max_chars),
        PolishPromptInjectionGuardrail(),
    ]
    if mask_pii:
        guardrails.append(pii_masking_guardrail())
    return guardrails

