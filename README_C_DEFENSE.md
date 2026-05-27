# C成员交付包：RAG安全防御模块

## 1. 我的分工定位

C成员负责项目中的防御模块，目标是在基础RAG系统上加入安全防护，降低提示注入、间接文档注入、任务劫持和敏感信息泄露风险。

本交付包包含四个防御版本：

| 版本 | 名称 | 作用 |
|---|---|---|
| D1 | Prompt加固 | 告诉模型：检索文档是资料，不是指令 |
| D2 | 检索文档检测与清洗 | 在文档进入模型前过滤恶意内容 |
| D3 | 输出检查 | 在模型输出后拦截敏感信息泄露 |
| D4 | 组合防御 | D1 + D2 + D3 组合使用 |

---

## 2. 文件说明

```text
rag-security-project/
├── defenses/
│   ├── __init__.py
│   ├── rules.py                # 风险规则库
│   ├── prompt_defense.py       # D1 Prompt加固
│   ├── doc_filter.py           # D2 文档检测与清洗
│   ├── output_guard.py         # D3 输出检查
│   └── combined_defense.py     # D4 组合防御流程
├── scripts/
│   └── demo_c_defense.py       # 防御模块演示
├── tests/
│   └── test_defense_modules.py # 简单测试
└── docs/
    ├── C_member_report_section.md
    ├── C_member_ppt_notes.md
    └── integration_guide_for_A.md
```

---

## 3. 给A成员的接入方式

A成员负责RAG主流程，只需要在检索后、调用大模型前、模型输出后分别接入我的函数。

### 方式一：使用组合防御

```python
from defenses.combined_defense import DefensePipeline

pipeline = DefensePipeline(doc_filter_mode="drop")

# 1. RAG系统已经拿到了用户问题和检索文档
question = "课程实践什么时候汇报？"
retrieved_docs = retriever.search(question)

# 2. 生成安全prompt
safe_prompt, defense_report = pipeline.build_prompt(question, retrieved_docs)

# 3. 调用大模型
raw_answer = llm.generate(safe_prompt)

# 4. 输出检查
final_answer, defense_report = pipeline.postprocess(raw_answer, defense_report)

print(final_answer)
print(defense_report.to_dict())
```

### 方式二：单独调用D2和D3

```python
from defenses.doc_filter import filter_docs
from defenses.prompt_defense import build_safe_prompt
from defenses.output_guard import guard_output

safe_docs = filter_docs(retrieved_docs, mode="drop")
prompt = build_safe_prompt(question, safe_docs)
raw_answer = llm.generate(prompt)
final_answer = guard_output(raw_answer)
```

---

## 4. 我的最小交付成果

我完成了以下内容：

1. D1：安全Prompt模板；
2. D2：恶意检索文档检测与过滤；
3. D2：恶意句子清洗模式；
4. D3：敏感输出检测与拦截；
5. D4：组合防御流水线；
6. 可输出防御报告，方便D成员统计实验结果；
7. demo脚本和简单测试；
8. PPT防御部分讲稿。

---

## 5. 运行演示

在项目根目录运行：

```bash
python scripts/demo_c_defense.py
```

如果安装了pytest，可以运行：

```bash
python -m pytest tests/test_defense_modules.py
```

---

## 6. Git提交建议

C成员只改这些路径：

```text
defenses/
scripts/demo_c_defense.py
tests/test_defense_modules.py
docs/C_member_*.md
```

提交命令：

```bash
git checkout -b feature/defense

git add defenses/ scripts/demo_c_defense.py tests/test_defense_modules.py docs/
git commit -m "add D1-D4 RAG defense modules"
git push origin feature/defense
```

然后在GitHub上开Pull Request：

```text
feature/defense -> dev
```
