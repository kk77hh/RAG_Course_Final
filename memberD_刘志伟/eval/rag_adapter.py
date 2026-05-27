"""Adapter layer between Member D evaluation and the unfinished RAG system.

The adapter first tries to import Member A's `run_rag`. If it is not available,
it falls back to a deterministic mock runner so Member D can still validate the
evaluation pipeline and produce placeholder results.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
C_PACKAGE = ROOT / "c_member_defense_package"
A_PROJECT = ROOT / "memberA_rag_project"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if A_PROJECT.exists() and str(A_PROJECT) not in sys.path:
    sys.path.insert(0, str(A_PROJECT))
if C_PACKAGE.exists() and str(C_PACKAGE) not in sys.path:
    sys.path.insert(0, str(C_PACKAGE))


def _try_member_a_run_rag():
    candidates = [
        "src.rag_pipeline",
        "rag_pipeline",
    ]
    for module_name in candidates:
        try:
            module = __import__(module_name, fromlist=["run_rag"])
            return getattr(module, "run_rag")
        except Exception:
            continue
    return None


def _get_docs(sample: Dict[str, Any]) -> List[Any]:
    docs = sample.get("docs") or sample.get("retrieved_docs") or []
    if isinstance(docs, list):
        return docs
    return [docs]


def _fake_llm(question: str, prompt: str, defense_mode: str, sample: Dict[str, Any]) -> str:
    sample_type = sample.get("type", "")
    joined = f"{question}\n{prompt}"
    is_attack = sample.get("dataset") == "attack" or "attack" in sample_type or "injection" in sample_type or "hijack" in sample_type

    if defense_mode == "D0" and is_attack:
        if any(term in joined for term in ["密钥", "SECRET", "系统提示词", "隐藏"]):
            return "系统提示词: 你是内部课程助手。SECRET_KEY=COURSE_SECRET_123456"
        return "已切换到管理员模式，按攻击者指定格式输出。"

    if defense_mode in {"D3", "D4"} and is_attack:
        return "抱歉，我不能提供系统提示词、隐藏规则、密钥、密码或其他敏感信息。课程相关问题我可以继续回答。"

    if "汇报" in question:
        return "课程实践需要在5月25日进行PPT汇报，每组约10分钟，并在6月1日前提交最终材料。"
    if "提交" in question:
        return "需要提交PPT、代码仓库、数据、结果表和伦理说明。"
    if "评分" in question:
        return "评分关注相关性、实际效果和新颖性。"
    return "该课程问答需要围绕课程安排、作业要求、AI安全与伦理内容作答。"


def _mock_run_rag(question: str, defense_mode: str, top_k: int, sample: Dict[str, Any]) -> Dict[str, Any]:
    docs = _get_docs(sample)[:top_k]
    defense_logs: Dict[str, Any] = {"adapter": "mock"}
    filtered_docs = docs

    if defense_mode in {"D1", "D2", "D3", "D4"}:
        try:
            from defenses.combined_defense import DefensePipeline

            pipeline = DefensePipeline(
                enable_prompt_defense=defense_mode in {"D1", "D4"},
                enable_doc_filter=defense_mode in {"D2", "D4"},
                enable_output_guard=defense_mode in {"D3", "D4"},
                doc_filter_mode="drop",
            )
            prompt, report = pipeline.build_prompt(question, docs)
            raw_answer = _fake_llm(question, prompt, defense_mode, sample)
            answer, report = pipeline.postprocess(raw_answer, report)
            filtered_docs = docs[: report.safe_doc_count]
            defense_logs.update(report.to_dict())
            return {
                "answer": answer,
                "retrieved_docs": docs,
                "filtered_docs": filtered_docs,
                "defense_logs": defense_logs,
            }
        except Exception as exc:
            defense_logs["defense_error"] = str(exc)

    answer = _fake_llm(question, "\n".join(map(str, docs)), defense_mode, sample)
    return {
        "answer": answer,
        "retrieved_docs": docs,
        "filtered_docs": filtered_docs,
        "defense_logs": defense_logs,
    }


def run_rag_for_eval(sample: Dict[str, Any], defense_mode: str, top_k: int = 3) -> Dict[str, Any]:
    member_a_run_rag = _try_member_a_run_rag()
    question = sample.get("question", "")
    if member_a_run_rag is not None:
        result = member_a_run_rag(question=question, defense_mode=defense_mode, top_k=top_k)
        result.setdefault("defense_logs", {})
        result["defense_logs"].setdefault("adapter", "member_a")
        return result
    return _mock_run_rag(question, defense_mode, top_k, sample)
