import time
import sys
from pathlib import Path
from src.data_loader import load_kb
from src.retriever import BM25Retriever
from src.prompt_builder import build_prompt
from src.llm_client import LLMClient
from src.utils import append_log, now_str

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
C_PACKAGE = REPO_ROOT / "c_member_defense_package"
if C_PACKAGE.exists() and str(C_PACKAGE) not in sys.path:
    sys.path.insert(0, str(C_PACKAGE))

DOCS = load_kb(
    str(PROJECT_ROOT / "data" / "kb_normal.jsonl"),
    str(PROJECT_ROOT / "data" / "kb_malicious.jsonl")
)

RETRIEVER = BM25Retriever(DOCS)

LLM = LLMClient(mock_mode=True)

def run_rag(
    question: str,
    defense_mode: str = "D0",
    top_k: int = 3
):
    start = time.time()

    retrieved_docs = RETRIEVER.search(question, top_k=top_k)
    filtered_docs = retrieved_docs
    defense_logs = {
        "defense_mode": defense_mode,
        "timestamp": now_str()
    }

    if defense_mode in {"D2", "D4"}:
        try:
            from defenses.doc_filter import filter_docs

            filtered_docs, details = filter_docs(retrieved_docs, mode="drop", return_details=True)
            defense_logs["doc_filter"] = details
        except Exception as exc:
            defense_logs["doc_filter_error"] = str(exc)

    prompt = build_prompt(
        question=question,
        retrieved_docs=filtered_docs,
        defense_mode="D1" if defense_mode in {"D1", "D4"} else "D0"
    )

    answer = LLM.generate(prompt)

    if defense_mode in {"D3", "D4"}:
        try:
            from defenses.output_guard import guard_output

            answer, output_result = guard_output(answer, return_result=True)
            defense_logs["output_guard"] = {
                "blocked": output_result.blocked,
                "score": output_result.score,
                "matched_rules": output_result.matched_rules,
                "reason": output_result.reason,
            }
        except Exception as exc:
            defense_logs["output_guard_error"] = str(exc)

    result = {
        "answer": answer,
        "retrieved_docs": retrieved_docs,
        "filtered_docs": filtered_docs,
        "defense_logs": defense_logs
    }

    elapsed = round(time.time() - start, 4)

    log_record = {
        "question": question,
        "answer": answer,
        "retrieved_docs": retrieved_docs,
        "defense_mode": defense_mode,
        "elapsed_sec": elapsed
    }

    append_log(str(PROJECT_ROOT / "results" / "logs" / "run_log.jsonl"), log_record)

    return result
