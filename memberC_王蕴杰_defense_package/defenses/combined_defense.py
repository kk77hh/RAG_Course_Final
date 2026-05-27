"""D4: Combined defense pipeline for RAG systems.

This module combines:
- D1: prompt hardening
- D2: retrieved document filtering / cleaning
- D3: output guard

The pipeline does not call an LLM by itself. It exposes simple interfaces so
Member A can plug it into the existing RAG system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from .doc_filter import DetectionResult, detect_suspicious_text, filter_docs
from .output_guard import OutputGuardResult, guard_output
from .prompt_defense import build_safe_prompt
from .rules import DEFAULT_SUSPICIOUS_THRESHOLD


@dataclass
class DefenseReport:
    """Report object for evaluation and PPT case analysis."""

    question_suspicious: bool = False
    question_detection: Optional[DetectionResult] = None
    doc_details: List[Dict[str, Any]] = field(default_factory=list)
    raw_doc_count: int = 0
    safe_doc_count: int = 0
    output_guard: Optional[OutputGuardResult] = None
    final_action: str = "answered"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_suspicious": self.question_suspicious,
            "question_reason": self.question_detection.reason if self.question_detection else "",
            "raw_doc_count": self.raw_doc_count,
            "safe_doc_count": self.safe_doc_count,
            "doc_details": self.doc_details,
            "output_blocked": self.output_guard.blocked if self.output_guard else False,
            "output_reason": self.output_guard.reason if self.output_guard else "",
            "final_action": self.final_action,
        }


class DefensePipeline:
    """Combined defense pipeline.

    Typical usage in RAG:
        pipeline = DefensePipeline()
        safe_prompt, report = pipeline.build_prompt(question, retrieved_docs)
        raw_answer = llm(safe_prompt)
        final_answer, report = pipeline.postprocess(raw_answer, report)
    """

    def __init__(
        self,
        *,
        enable_prompt_defense: bool = True,
        enable_doc_filter: bool = True,
        enable_output_guard: bool = True,
        doc_filter_mode: str = "drop",
        suspicious_threshold: int = DEFAULT_SUSPICIOUS_THRESHOLD,
        max_context_chars: int = 6000,
    ) -> None:
        self.enable_prompt_defense = enable_prompt_defense
        self.enable_doc_filter = enable_doc_filter
        self.enable_output_guard = enable_output_guard
        self.doc_filter_mode = doc_filter_mode
        self.suspicious_threshold = suspicious_threshold
        self.max_context_chars = max_context_chars

    def build_prompt(self, question: str, retrieved_docs: Iterable[Any]) -> Tuple[str, DefenseReport]:
        """Apply D2 and D1, then return safe prompt and report."""
        docs_list = list(retrieved_docs)
        report = DefenseReport(raw_doc_count=len(docs_list))

        question_detection = detect_suspicious_text(question, threshold=self.suspicious_threshold)
        report.question_detection = question_detection
        report.question_suspicious = question_detection.is_suspicious

        safe_docs = docs_list
        if self.enable_doc_filter:
            safe_docs, details = filter_docs(
                docs_list,
                mode=self.doc_filter_mode,
                threshold=self.suspicious_threshold,
                return_details=True,
            )
            report.doc_details = details

        report.safe_doc_count = len(safe_docs)

        if self.enable_prompt_defense:
            prompt = build_safe_prompt(question, safe_docs, max_context_chars=self.max_context_chars)
        else:
            # Minimal fallback. D0 should preferably use build_d0_prompt from prompt_defense.py.
            context = "\n\n".join(str(d) for d in safe_docs)
            prompt = f"资料：\n{context}\n\n问题：{question}\n请回答。"

        return prompt, report

    def postprocess(self, answer: str, report: Optional[DefenseReport] = None) -> Tuple[str, DefenseReport]:
        """Apply D3 output guard."""
        report = report or DefenseReport()
        final_answer = answer
        if self.enable_output_guard:
            final_answer, output_result = guard_output(answer, return_result=True)
            report.output_guard = output_result
            if output_result.blocked:
                report.final_action = "blocked_output"
        return final_answer, report

    def run(
        self,
        question: str,
        retrieved_docs: Iterable[Any],
        llm_generate: Callable[[str], str],
    ) -> Tuple[str, DefenseReport]:
        """Full D4 flow when an LLM function is available."""
        prompt, report = self.build_prompt(question, retrieved_docs)
        raw_answer = llm_generate(prompt)
        return self.postprocess(raw_answer, report)


def apply_defense(
    question: str,
    retrieved_docs: Iterable[Any],
    model_answer: Optional[str] = None,
    *,
    doc_filter_mode: str = "drop",
) -> Dict[str, Any]:
    """Convenience function for integration tests.

    If model_answer is None, it only returns safe prompt and filtered-doc report.
    If model_answer is provided, it also returns guarded final answer.
    """
    pipeline = DefensePipeline(doc_filter_mode=doc_filter_mode)
    prompt, report = pipeline.build_prompt(question, retrieved_docs)
    result: Dict[str, Any] = {
        "safe_prompt": prompt,
        "report": report.to_dict(),
    }
    if model_answer is not None:
        final_answer, report = pipeline.postprocess(model_answer, report)
        result["final_answer"] = final_answer
        result["report"] = report.to_dict()
    return result
