"""Batch evaluation entry point for D0-D4."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from io_utils import read_jsonl, write_jsonl
from judge_attack import judge_attack
from judge_normal import judge_normal
from rag_adapter import run_rag_for_eval


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODES = ["D0", "D1", "D2", "D3", "D4"]


def _load_samples(data_dir: Path, repeat: int = 1) -> List[Dict[str, Any]]:
    normal = read_jsonl(data_dir / "questions_normal.jsonl")
    attack = read_jsonl(data_dir / "questions_attack.jsonl")

    if not normal and not attack:
        normal = read_jsonl(ROOT / "data" / "sample_questions_normal.jsonl")
        attack = read_jsonl(ROOT / "data" / "sample_questions_attack.jsonl")

    for row in normal:
        row["dataset"] = "normal"
    for row in attack:
        row["dataset"] = "attack"

    samples = normal + attack
    if repeat <= 1:
        return samples

    expanded: List[Dict[str, Any]] = []
    for round_idx in range(repeat):
        for row in samples:
            cloned = dict(row)
            cloned["original_id"] = row.get("id", "")
            cloned["id"] = f"{row.get('id', '')}__r{round_idx + 1:02d}"
            cloned["repeat_round"] = round_idx + 1
            expanded.append(cloned)
    return expanded


def evaluate_mode(samples: List[Dict[str, Any]], defense_mode: str, top_k: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for sample in samples:
        result = run_rag_for_eval(sample, defense_mode=defense_mode, top_k=top_k)
        answer = result.get("answer", "")
        attack_success = False
        leakage = False
        normal_correct = False
        over_refusal = False
        notes = ""

        if sample["dataset"] == "attack":
            attack_success, leakage, notes = judge_attack(sample, answer)
        else:
            normal_correct, over_refusal, notes = judge_normal(sample, answer)

        rows.append(
            {
                "id": sample.get("id", ""),
                "type": sample.get("type", ""),
                "dataset": sample["dataset"],
                "defense_mode": defense_mode,
                "question": sample.get("question", ""),
                "answer": answer,
                "attack_success": attack_success,
                "leakage": leakage,
                "normal_correct": normal_correct,
                "over_refusal": over_refusal,
                "retrieved_doc_count": len(result.get("retrieved_docs", [])),
                "filtered_doc_count": len(result.get("filtered_docs", [])),
                "defense_logs": result.get("defense_logs", {}),
                "notes": notes,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--modes", nargs="+", default=DEFAULT_MODES)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--repeat", type=int, default=1, help="Repeat the loaded dataset N times for scale testing.")
    args = parser.parse_args()

    samples = _load_samples(args.data_dir, repeat=args.repeat)
    if not samples:
        raise SystemExit("No samples found. Add questions_normal.jsonl and questions_attack.jsonl.")

    for mode in args.modes:
        rows = evaluate_mode(samples, mode, args.top_k)
        write_jsonl(args.results_dir / f"raw_{mode}.jsonl", rows)
        print(f"wrote {len(rows)} rows -> {args.results_dir / f'raw_{mode}.jsonl'}")


if __name__ == "__main__":
    main()
