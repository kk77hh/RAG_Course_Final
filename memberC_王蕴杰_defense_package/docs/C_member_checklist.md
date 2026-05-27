# C成员任务验收清单

## 必须完成

- [x] D1 Prompt加固模板：`defenses/prompt_defense.py`
- [x] D2 文档检测与过滤：`defenses/doc_filter.py`
- [x] D3 输出敏感信息拦截：`defenses/output_guard.py`
- [x] D4 组合防御流程：`defenses/combined_defense.py`
- [x] 风险关键词/正则规则库：`defenses/rules.py`
- [x] 给A成员的接入指南：`docs/integration_guide_for_A.md`
- [x] 给PPT用的讲稿：`docs/C_member_ppt_notes.md`
- [x] 给实验报告用的文字：`docs/C_member_report_section.md`
- [x] demo脚本：`scripts/demo_c_defense.py`
- [x] 测试样例：`tests/test_defense_modules.py`
- [x] 攻防测试样本：`data/defense_test_cases.jsonl`

## 需要和A成员确认

- [ ] A成员的检索结果是 `list[str]` 还是 `list[dict]`？
- [ ] A成员调用大模型的函数名是什么？例如 `llm.generate(prompt)`。
- [ ] 最终系统是否要保留 `defense_report.to_dict()` 供D成员统计？

## 需要和D成员确认

- [ ] D成员是否需要记录每次过滤掉了几篇文档？
- [ ] D成员是否需要记录输出是否被D3拦截？
- [ ] D成员是否把D0-D4分开跑实验？

## 汇报时你要讲的核心句子

我负责防御模块。我的设计是在RAG流程的三个关键位置加入防护：首先在检索文档进入模型前做D2过滤，防止恶意文档注入；其次用D1安全Prompt告诉模型文档只是资料不是指令；最后用D3输出检查拦截系统提示词、密钥、token等敏感信息。最终D4组合防御可以降低攻击成功率和敏感信息泄露率，但可能会带来少量过度拒答，需要通过实验指标评估。
