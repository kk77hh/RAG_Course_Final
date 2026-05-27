"""Generate simple charts from metrics_summary.csv."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_metrics(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _plot_with_matplotlib(rows: list[dict[str, str]], charts_dir: Path) -> bool:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return False

    charts_dir.mkdir(parents=True, exist_ok=True)
    modes = [r["defense_mode"] for r in rows]
    chart_specs = [
        ("ASR", "Attack Success Rate", "asr.png"),
        ("LRate", "Leakage Rate", "lrate.png"),
        ("Score", "Composite Score", "score.png"),
    ]
    for key, title, filename in chart_specs:
        values = [float(r[key]) for r in rows]
        plt.figure(figsize=(7, 4))
        plt.bar(modes, values, color=["#62656a", "#3874cb", "#2f9d74", "#c47f2c", "#b94664"])
        plt.ylim(0, 1)
        plt.title(title)
        plt.xlabel("Defense Mode")
        plt.ylabel(key)
        plt.tight_layout()
        plt.savefig(charts_dir / filename, dpi=180)
        plt.close()

    utility = [float(r["Utility"]) for r in rows]
    orr = [float(r["ORR"]) for r in rows]
    x = range(len(modes))
    plt.figure(figsize=(7, 4))
    plt.plot(x, utility, marker="o", label="Utility")
    plt.plot(x, orr, marker="s", label="ORR")
    plt.xticks(list(x), modes)
    plt.ylim(0, 1)
    plt.title("Utility vs Over-refusal")
    plt.legend()
    plt.tight_layout()
    plt.savefig(charts_dir / "utility_orr.png", dpi=180)
    plt.close()
    return True


def _write_text_charts(rows: list[dict[str, str]], charts_dir: Path) -> None:
    charts_dir.mkdir(parents=True, exist_ok=True)
    for key in ["ASR", "LRate", "Utility", "ORR", "Score"]:
        lines = [f"{key} text chart"]
        for row in rows:
            value = float(row[key])
            lines.append(f"{row['defense_mode']}: {'#' * int(value * 40)} {value:.2f}")
        (charts_dir / f"{key.lower()}_chart.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, default=ROOT / "results" / "metrics_summary.csv")
    parser.add_argument("--charts-dir", type=Path, default=ROOT / "charts")
    args = parser.parse_args()

    rows = _load_metrics(args.metrics)
    if _plot_with_matplotlib(rows, args.charts_dir):
        print(f"wrote png charts -> {args.charts_dir}")
    else:
        _write_text_charts(rows, args.charts_dir)
        print(f"matplotlib unavailable; wrote text charts -> {args.charts_dir}")


if __name__ == "__main__":
    main()
