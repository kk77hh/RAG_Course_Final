# 成员B交付包：数据集与D0攻击实验

本目录为成员钟千有交付内容，负责中文 RAG 安全评测项目中的数据集构建、攻击样本设计、D0 无防御攻击实验和典型案例整理。

## 目录结构

```text
memberB_data_attack_package/
├── data/
│   ├── kb_normal.jsonl
│   ├── kb_malicious.jsonl
│   ├── questions_normal.jsonl
│   ├── questions_attack.jsonl
│   └── dataset_manifest.json
├── scripts/
│   ├── build_member_b_data.py
│   ├── run_d0_attack_eval.py
│   ├── rejudge_d0_results.py
│   └── export_member_b_docs.py
├── results/
│   ├── d0_attack_raw.jsonl
│   ├── d0_attack_results.csv
│   └── d0_attack_summary.json
└── docs/
    ├── B_member_dataset_description.md
    ├── B_member_attack_cases.md
    ├── B_member_ppt_notes.md
    ├── B_member_integration_guide.md
    └── B_member_checklist.md
```

## 数据规模

- 正常知识库：40 条
- 恶意文档：20 条
- 正常问题：80 条
- 攻击问题：80 条

## D0 实验结果

- 模型：google/gemini-3.1-flash-lite-preview
- 样本数：80
- API 错误数：0
- 攻击成功率 ASR：0.2125
- 敏感信息泄露率 LRate：0.1375

## 运行方法

重新生成数据：

```bash
python3 scripts/build_member_b_data.py
```

重新跑 D0 攻击实验。脚本会从作业根目录的 `env.local` 或环境变量读取 OpenRouter 配置：

```bash
python3 scripts/run_d0_attack_eval.py
```

如果只想重算自动判定，不重新调用 API：

```bash
python3 scripts/rejudge_d0_results.py
```

重新导出文档：

```bash
python3 scripts/export_member_b_docs.py
```

## 安全说明

`env.local` 不属于成员B交付物，不应提交到 GitHub。所有攻击目标和密钥均为课程模拟内容，例如 `COURSE_SECRET_4F9A_DO_NOT_OUTPUT`，不对应任何真实系统。
