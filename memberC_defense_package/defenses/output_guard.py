"""D3: Output guard for blocking sensitive leakage in model answers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from .rules import DEFAULT_OUTPUT_THRESHOLD, SAFE_REFUSAL, SENSITIVE_OUTPUT_RULES, Rule
from .doc_filter import _normalize, _snippet


@dataclass
class OutputGuardResult:
    """Result of output safety checking."""

    blocked: bool
    score: int
    matched_rules: List[str] = field(default_factory=list)
    snippets: List[str] = field(default_factory=list)
    safe_answer: str = ""

    @property
    def reason(self) -> str:
        if not self.matched_rules:
            return "输出未命中敏感信息规则"
        return f"输出命中敏感信息规则: {', '.join(self.matched_rules)}; 风险分: {self.score}"


def detect_sensitive_output(
    answer: str,
    *,
    threshold: int = DEFAULT_OUTPUT_THRESHOLD,
    rules: Sequence[Rule] = SENSITIVE_OUTPUT_RULES,
) -> OutputGuardResult:
    """Detect whether the model answer contains likely sensitive leakage."""
    normalized = _normalize(answer)
    score = 0
    matched_rules: List[str] = []
    snippets: List[str] = []

    for rule in rules:
        pattern = rule.compile()
        match = pattern.search(normalized)
        if match:
            score += rule.weight
            matched_rules.append(rule.name)
            snippets.append(_snippet(normalized, match.start(), match.end()))

    blocked = score >= threshold
    return OutputGuardResult(
        blocked=blocked,
        score=score,
        matched_rules=matched_rules,
        snippets=snippets[:5],
        safe_answer=SAFE_REFUSAL if blocked else answer,
    )


def guard_output(
    answer: str,
    *,
    threshold: int = DEFAULT_OUTPUT_THRESHOLD,
    safe_refusal: str = SAFE_REFUSAL,
    return_result: bool = False,
):
    """Return safe answer after output checking.

    Args:
        answer: Raw LLM answer.
        threshold: Blocking threshold.
        safe_refusal: Replacement answer if blocked.
        return_result: If True, return (safe_answer, OutputGuardResult).
    """
    result = detect_sensitive_output(answer, threshold=threshold)
    if result.blocked:
        result.safe_answer = safe_refusal
    if return_result:
        return result.safe_answer, result
    return result.safe_answer
