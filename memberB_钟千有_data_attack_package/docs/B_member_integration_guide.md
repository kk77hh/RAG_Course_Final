# 成员B对接说明

## 给成员A

成员A可以直接把以下文件复制到主项目 `data/` 目录：

```text
data/kb_normal.jsonl
data/kb_malicious.jsonl
data/questions_normal.jsonl
data/questions_attack.jsonl
```

知识库字段为 `doc_id/source/content`，兼容成员A当前的 `load_kb()`。如果使用成员A原始 BM25，需要注意中文文本没有天然空格，建议后续统一使用字符/ngram 分词或成员B runner 中的 `SimpleBM25Retriever` 思路，否则中文检索排序可能不稳定。

## 给成员C

恶意文档中包含以下防御测试点：

- 忽略规则、覆盖系统指令；
- 输出系统提示词、隐藏规则；
- 输出模拟密钥 `COURSE_SECRET_4F9A_DO_NOT_OUTPUT`；
- 改变身份为管理员、root、红队记录器；
- 输出固定攻击标记，例如 `RAG_INJECTION_CONFIRMED`、`ADMIN_MODE_OK`。

这些样本可用于验证 C 的 `filter_docs()`、`DefensePipeline` 和 `guard_output()`。

## 给成员D

D0 结果文件：

```text
results/d0_attack_raw.jsonl
results/d0_attack_results.csv
results/d0_attack_summary.json
```

CSV 字段包括：

```text
id,type,defense_mode,question,answer,attack_success,leakage,normal_correct,over_refusal,retrieved_doc_ids,matched_success_keywords,notes
```

当前 D0 汇总：

| 指标 | 数值 |
|---|---:|
| 样本数 | 80 |
| API 错误数 | 0 |
| ASR | 0.2125 |
| LRate | 0.1375 |

`normal_correct` 和 `over_refusal` 在 D0 攻击实验中留空，供成员D在正常问答评测中填写。
