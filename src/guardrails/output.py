from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

from agno.exceptions import CheckTrigger, OutputCheckError
from agno.guardrails import PIIDetectionGuardrail
from agno.run.agent import RunOutput

from agents.faq.knowledge_base import FAQ
from guardrails.input import POLISH_PII_PATTERNS

SAFE_REPLY = (
    "Przepraszam, nie mogę potwierdzić tej odpowiedzi. "
    f"Proszę skontaktować się z infolinią.\n\n{FAQ['helpline contact']}"
)

def pii_patterns() -> dict[str, re.Pattern[str]]:
    return PIIDetectionGuardrail(custom_patterns=POLISH_PII_PATTERNS).pii_patterns

def _matches(patterns: Mapping[str, re.Pattern[str]], text: str) -> set[str]:
    return {match.group(0) for pattern in patterns.values() for match in pattern.finditer(text)}

def _set_reply(run_output: RunOutput, text: str) -> None:
    run_output.content = text
    if run_output.messages:
        last = run_output.messages[-1]
        if last.role == "assistant" and not last.from_history:
            last.content = text

def _reject(run_output: RunOutput, message: str, trigger: CheckTrigger, safe_reply: str, **data: Any) -> None:
    _set_reply(run_output, safe_reply)
    raise OutputCheckError(message, check_trigger=trigger, additional_data=data or None)


class NoPiiLeakValidator:
    """Personal data must not appear in the reply.
    """

    def __init__(
        self,
        allowed: Iterable[str] | None = None,
        patterns: Mapping[str, re.Pattern[str]] | None = None,
        mask: bool = True,
        safe_reply: str = SAFE_REPLY,
    ):
        self.patterns = dict(patterns or pii_patterns())
        self.allowed = set(allowed) if allowed is not None else _matches(self.patterns, FAQ["helpline contact"])
        self.mask = mask
        self.safe_reply = safe_reply

    def __call__(self, run_output: RunOutput) -> None:
        text = run_output.content
        if not isinstance(text, str) or not text:
            return
        found: dict[str, list[str]] = {}
        for name, pattern in self.patterns.items():

            def mask_match(match: re.Match[str], name: str = name) -> str:
                token = match.group(0)
                if token in self.allowed:
                    return token
                found.setdefault(name, []).append(token)
                return "*" * len(token)

            text = pattern.sub(mask_match, text)
        if not found:
            return
        if self.mask:
            _set_reply(run_output, text)
            return
        _reject(
            run_output,
            f"Odpowiedź zawiera dane osobowe: {', '.join(found)}",
            CheckTrigger.PII_DETECTED,
            self.safe_reply,
            detected_pii=sorted(found),
        )


_UNITS = r"(?:zł|złot\w*|pln|euro?|€|kg|kilogram\w*|cm|centymetr\w*|godz(?:in\w*|\.)?|h|min(?:ut\w*)?|%)"
_AMOUNT = re.compile(rf"(?<![\d,.])(\d+(?:[.,]\d+)?)\s*{_UNITS}(?![\wł])", re.IGNORECASE)
_AMOUNT_UNIT_FIRST = re.compile(r"(?<![\wł])(?:zł|pln|eur|€)\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)
_NUMBER = re.compile(r"\d+(?:[.,]\d+)?")

def _text(value: Any) -> str:
    return value if isinstance(value, str) else ("" if value is None else str(value))

def _as_number(token: str) -> float:
    return float(token.replace(",", "."))


class GroundedNumbersValidator:

    def __init__(self, safe_reply: str = SAFE_REPLY):
        self.safe_reply = safe_reply

    @staticmethod
    def amounts(text: str) -> list[str]:
        """Amount tokens in `text`, e.g. ['27,5', '150'] for '27,5 kg ... 150 zł'."""
        return [m.group(1) for m in _AMOUNT.finditer(text)] + [m.group(1) for m in _AMOUNT_UNIT_FIRST.finditer(text)]

    @staticmethod
    def evidence(run_output: RunOutput) -> str:
        parts: list[str] = []
        if run_output.input is not None:
            parts.append(run_output.input.input_content_string())
        for message in run_output.messages or []:
            # The answer under validation is the run's own assistant text; skip it.
            if message.role == "assistant" and not message.from_history:
                continue
            parts.append(_text(message.content))
        for tool in run_output.tools or []:
            parts.append(_text(tool.tool_args))
            parts.append(_text(tool.result))
        return "\n".join(parts)

    def ungrounded(self, run_output: RunOutput) -> list[str]:
        text = run_output.content
        if not isinstance(text, str) or not text:
            return []
        known = {_as_number(token) for token in _NUMBER.findall(self.evidence(run_output))}
        return sorted({token for token in self.amounts(text) if _as_number(token) not in known})

    def __call__(self, run_output: RunOutput) -> None:
        ungrounded = self.ungrounded(run_output)
        if ungrounded:
            _reject(
                run_output,
                f"Odpowiedź zawiera liczby bez pokrycia w źródłach: {', '.join(ungrounded)}",
                CheckTrigger.VALIDATION_FAILED,
                self.safe_reply,
                ungrounded=ungrounded,
            )

def default_output_validators(*, safe_reply: str = SAFE_REPLY) -> list[Any]:
    """The standard `post_hooks` list for an Example Air agent that quotes figures."""
    return [NoPiiLeakValidator(safe_reply=safe_reply), GroundedNumbersValidator(safe_reply=safe_reply)]
