# 给A成员的防御模块接入指南

A成员负责RAG主流程，我负责防御模块。为了避免代码冲突，A只需要在三个位置调用我的接口。

## 1. 接入位置

原始RAG流程：

```text
用户问题 -> 检索Top-k文档 -> 拼接Prompt -> 调用大模型 -> 返回答案
```

加入防御后：

```text
用户问题
 -> 检索Top-k文档
 -> D2：过滤/清洗检索文档
 -> D1：构造安全Prompt
 -> 调用大模型
 -> D3：输出检查
 -> 返回安全答案
```

---

## 2. 推荐接口

```python
from defenses.combined_defense import DefensePipeline

pipeline = DefensePipeline(
    doc_filter_mode="drop",       # drop: 丢弃可疑文档；clean: 删除可疑句子
    enable_prompt_defense=True,
    enable_doc_filter=True,
    enable_output_guard=True,
)

safe_prompt, defense_report = pipeline.build_prompt(question, retrieved_docs)
raw_answer = llm.generate(safe_prompt)
final_answer, defense_report = pipeline.postprocess(raw_answer, defense_report)
```

---

## 3. D0-D4实验版本怎么开关

可以通过开关控制不同防御版本：

```python
# D0：无防御。建议A用自己的原始prompt，不调用DefensePipeline。

# D1：只开Prompt加固
pipeline = DefensePipeline(
    enable_prompt_defense=True,
    enable_doc_filter=False,
    enable_output_guard=False,
)

# D2：只开文档过滤
pipeline = DefensePipeline(
    enable_prompt_defense=False,
    enable_doc_filter=True,
    enable_output_guard=False,
)

# D3：只开输出检查
pipeline = DefensePipeline(
    enable_prompt_defense=False,
    enable_doc_filter=False,
    enable_output_guard=True,
)

# D4：组合防御
pipeline = DefensePipeline(
    enable_prompt_defense=True,
    enable_doc_filter=True,
    enable_output_guard=True,
)
```

---

## 4. 给D成员的评测字段

`defense_report.to_dict()` 会返回：

```python
{
    "question_suspicious": bool,
    "question_reason": str,
    "raw_doc_count": int,
    "safe_doc_count": int,
    "doc_details": list,
    "output_blocked": bool,
    "output_reason": str,
    "final_action": str,
}
```

D成员可以用这些字段统计：

- 文档过滤数量；
- 可疑问题数量；
- 输出拦截数量；
- D4是否过度拒答；
- 典型攻击成功/防御成功案例。
