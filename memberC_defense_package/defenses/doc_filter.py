"""D2: Retrieved-document detection and cleaning for RAG systems.

The key idea: retrieved documents are untrusted data, not instructions.
Before passing them into the LLM prompt, detect and remove content that looks
like prompt injection, task hijacking, or secret exfiltration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Sequence, Tuple, Union
import copy
import re

from .rules import DEFAULT_SUSPICIOUS_THRESHOLD, SAFE_DOC_REMOVED_NOTE, SUSPICIOUS_RULES, Rule

Doc = Union[str, Dict[str, Any], Any]


@dataclass
class DetectionResult:
    """Result of suspicious text detection."""

    is_suspicious: bool
    score: int
    matched_rules: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    snippets: List[str] = field(default_factory=list)

    @property
    def reason(self) -> str:
        if not self.matched_rules:
            return "未命中风险规则"
        cats = ", ".join(sorted(set(self.categories)))
        rules = ", ".join(self.matched_rules)
        return f"命中类别: {cats}; 命中规则: {rules}; 风险分: {self.score}"


def _normalize(text: str) -> str:
    """Normalize whitespace for easier matching."""
    return re.sub(r"\s+", " ", text or "").strip()


def _snippet(text: str, start: int, end: int, width: int = 36) -> str:
    left = max(0, start - width)
    right = min(len(text), end + width)
    return text[left:right].replace("\n", " ")


def detect_suspicious_text(
    text: str,
    *,
    threshold: int = DEFAULT_SUSPICIOUS_THRESHOLD,
    rules: Sequence[Rule] = SUSPICIOUS_RULES,
) -> DetectionResult:
    """Detect whether text contains suspicious instruction-like content.

    Args:
        text: User query or retrieved document text.
        threshold: Risk score threshold. Score >= threshold is suspicious.
        rules: List of regex rules.

    Returns:
        DetectionResult with score, matched rules, categories, and snippets.
    """
    normalized = _normalize(text)
    score = 0
    matched_rules: List[str] = []
    categories: List[str] = []
    snippets: List[str] = []

    for rule in rules:
        pattern = rule.compile()
        match = pattern.search(normalized)
        if match:
            score += rule.weight
            matched_rules.append(rule.name)
            categories.append(rule.category)
            snippets.append(_snippet(normalized, match.start(), match.end()))

    return DetectionResult(
        is_suspicious=score >= threshold,
        score=score,
        matched_rules=matched_rules,
        categories=categories,
        snippets=snippets[:5],
    )


def split_sentences(text: str) -> List[str]:
    """Split Chinese/English mixed text into rough sentences."""
    if not text:
        return []
    # Keep punctuation as part of the preceding sentence.
    pieces = re.split(r"(?<=[。！？!?；;\n])\s*", text.strip())
    return [p.strip() for p in pieces if p.strip()]


def clean_document(
    text: str,
    *,
    threshold: int = DEFAULT_SUSPICIOUS_THRESHOLD,
    min_remaining_chars: int = 8,
) -> Tuple[str, DetectionResult, List[str]]:
    """Remove suspicious sentences from one document.

    Args:
        text: Original document text.
        threshold: Sentence-level threshold for removal.
        min_remaining_chars: If too little useful text remains, return empty.

    Returns:
        cleaned_text, document_detection_result, removed_sentences
    """
    doc_result = detect_suspicious_text(text, threshold=threshold)
    if not doc_result.is_suspicious:
        return text, doc_result, []

    kept: List[str] = []
    removed: List[str] = []

    for sent in split_sentences(text):
        sent_result = detect_suspicious_text(sent, threshold=threshold)
        if sent_result.is_suspicious:
            removed.append(sent)
        else:
            kept.append(sent)

    cleaned = "\n".join(kept).strip()
    if len(cleaned) < min_remaining_chars:
        cleaned = ""
    return cleaned, doc_result, removed


def get_doc_text(doc: Doc) -> str:
    """Extract text from common document formats.

    Supports:
    - str
    - dict with keys: content, text, page_content, document
    - LangChain-like object with page_content attribute
    """
    if isinstance(doc, str):
        return doc
    if isinstance(doc, dict):
        for key in ("content", "text", "page_content", "document"):
            value = doc.get(key)
            if isinstance(value, str):
                return value
        return str(doc)
    if hasattr(doc, "page_content"):
        value = getattr(doc, "page_content")
        if isinstance(value, str):
            return value
    return str(doc)


def set_doc_text(doc: Doc, new_text: str) -> Doc:
    """Return a copy of doc with its text replaced when possible."""
    if isinstance(doc, str):
        return new_text
    if isinstance(doc, dict):
        new_doc = copy.deepcopy(doc)
        for key in ("content", "text", "page_content", "document"):
            if key in new_doc and isinstance(new_doc[key], str):
                new_doc[key] = new_text
                new_doc.setdefault("defense_note", "document cleaned by D2")
                return new_doc
        new_doc["content"] = new_text
        new_doc.setdefault("defense_note", "document cleaned by D2")
        return new_doc
    # Avoid mutating unknown objects. Return cleaned text instead.
    return new_text


def filter_docs(
    docs: Iterable[Doc],
    *,
    mode: str = "drop",
    threshold: int = DEFAULT_SUSPICIOUS_THRESHOLD,
    add_notice: bool = False,
    return_details: bool = False,
) -> Union[List[Doc], Tuple[List[Doc], List[Dict[str, Any]]]]:
    """Filter or clean retrieved documents.

    Args:
        docs: Retrieved documents.
        mode: "drop" removes suspicious docs; "clean" removes suspicious
            sentences and keeps safe remainder.
        threshold: Detection threshold.
        add_notice: Whether to append a safe filtering note when documents were
            removed. Usually False for production; True can be useful in demos.
        return_details: Whether to return detection details for evaluation/PPT.

    Returns:
        filtered_docs or (filtered_docs, details).
    """
    if mode not in {"drop", "clean"}:
        raise ValueError("mode must be 'drop' or 'clean'")

    filtered: List[Doc] = []
    details: List[Dict[str, Any]] = []
    removed_count = 0

    for idx, doc in enumerate(docs):
        text = get_doc_text(doc)
        result = detect_suspicious_text(text, threshold=threshold)
        detail: Dict[str, Any] = {
            "index": idx,
            "is_suspicious": result.is_suspicious,
            "score": result.score,
            "reason": result.reason,
            "snippets": result.snippets,
            "action": "keep",
        }

        if not result.is_suspicious:
            filtered.append(doc)
        elif mode == "drop":
            removed_count += 1
            detail["action"] = "drop"
        else:
            cleaned, doc_result, removed_sentences = clean_document(text, threshold=threshold)
            detail.update(
                {
                    "score": doc_result.score,
                    "reason": doc_result.reason,
                    "removed_sentences": removed_sentences,
                    "action": "clean" if cleaned else "drop_after_clean",
                }
            )
            if cleaned:
                filtered.append(set_doc_text(doc, cleaned))
            else:
                removed_count += 1

        details.append(detail)

    if add_notice and removed_count > 0:
        filtered.append(SAFE_DOC_REMOVED_NOTE)

    if return_details:
        return filtered, details
    return filtered
