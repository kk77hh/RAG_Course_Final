"""Recompute D0 attack judgments from saved raw model answers.

Use this when the success/leakage heuristics are adjusted but the API outputs
do not need to be regenerated.
"""

from __future__ import annotations

import json
from pathlib import Path

from run_d0_attack_eval import DATA_DIR, RESULTS_DIR, judge_attack, read_jsonl, summarize, write_csv, write_jsonl


def main() -> None:
    raw_path = RESULTS_DIR / "d0_attack_raw.jsonl"
    if not raw_path.exists():
        raise FileNotFoundError(raw_path)

    questions = {row["id"]: row for row in read_jsonl(DATA_DIR / "questions_attack.jsonl")}
    rows = read_jsonl(raw_path)
    for row in rows:
        question = questions[row["id"]]
        judgment = judge_attack(question, row["answer"])
        row["attack_success"] = judgment["attack_success"]
        row["leakage"] = judgment["leakage"]
        row["matched_success_keywords"] = "|".join(judgment["matched_success_keywords"])
        row["matched_leakage_patterns"] = judgment["matched_leakage_patterns"]
        row["judge_reasons"] = judgment["judge_reasons"]
        row["notes"] = "; ".join(judgment["judge_reasons"])

    model = "unknown"
    summary_path = RESULTS_DIR / "d0_attack_summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        model = summary.get("model", model)
    summary = summarize(rows, model, complete_dataset=len(rows) == len(questions))
    write_jsonl(raw_path, rows)
    write_csv(RESULTS_DIR / "d0_attack_results.csv", rows)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
