# D成员交付包：自动化评测、图表与汇报统稿

## 1. 分工定位

D成员负责把项目算清楚、讲清楚：批量跑 D0-D4，计算 ASR、LRate、Utility、ORR、Score，生成结果表和图表，并整理 PPT 结构、讲稿与 Q&A。

当前仓库只有 C 成员防御包，缺少 A 的正式 `run_rag` 和 B 的完整数据。因此本目录提供两层能力：

- 有真实 `src.rag_pipeline.run_rag` 时，自动调用真实 RAG。
- 没有真实接口时，使用 mock runner 跑通评测流程，先产出占位结果和图表。

## 2. 目录说明

```text
D_member/
├── eval/
│   ├── run_eval.py
│   ├── judge_attack.py
│   ├── judge_normal.py
│   ├── aggregate_metrics.py
│   ├── plot_results.py
│   ├── rag_adapter.py
│   └── io_utils.py
├── data/
│   ├── sample_questions_normal.jsonl
│   └── sample_questions_attack.jsonl
├── results/
├── charts/
├── docs/
└── slides/
```

## 3. 运行命令

从 `D_member` 目录运行：

```bash
python eval/run_eval.py
python eval/aggregate_metrics.py
python eval/plot_results.py
```

如果 B 成员交付了正式数据，把文件放到 `D_member/data/`：

```text
questions_normal.jsonl
questions_attack.jsonl
```

如果 A 成员交付了正式 RAG，只要仓库根目录可导入 `src.rag_pipeline.run_rag`，评测脚本会自动切换到真实接口。

## 4. 输出

- `results/raw_D0.jsonl` 到 `results/raw_D4.jsonl`：逐样本原始结果。
- `results/metrics_summary.csv`：五个防御模式的指标汇总。
- `charts/asr.png`、`charts/lrate.png`、`charts/utility_orr.png`、`charts/score.png`：汇报图表。若没有 matplotlib，会生成文本图表。

## 5. 指标定义

| 指标 | 公式 | 越好方向 |
|---|---|---|
| ASR | 攻击成功样本数 / 攻击样本总数 | 越低越好 |
| LRate | 敏感信息泄露次数 / 测试总次数 | 越低越好 |
| Utility | 正常问题回答正确数 / 正常问题总数 | 越高越好 |
| ORR | 正常问题被错误拒答数 / 正常问题总数 | 越低越好 |
| Score | Utility * (1 - ASR) * (1 - ORR) | 越高越好 |

## 6. 待 A/B/C 补齐的接口和数据

- A：`run_rag(question: str, defense_mode: str, top_k: int = 3) -> dict`。
- B：不少于 80 条正常问题和 80 条攻击问题，字段包含 `id/type/question/expected_behavior/success_rule`，正常题补充 `expected_answer_keywords`。
- C：防御日志中尽量保留过滤原因、输出拦截原因，便于案例页解释。

