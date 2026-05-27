# 最终提交检查清单

## 代码与数据

- [ ] A 成员 `run_rag` 接口可被 `D_member/eval/run_eval.py` 调用。
- [ ] B 成员数据已放入 `D_member/data/questions_normal.jsonl` 和 `D_member/data/questions_attack.jsonl`。
- [ ] C 成员 D1-D4 防御日志包含过滤和拦截原因。
- [ ] D0-D4 都生成了 `results/raw_D*.jsonl`。
- [ ] `results/metrics_summary.csv` 已更新。
- [ ] 至少 3 张图表已生成到 `charts/`。

## PPT

- [ ] 10-12 页以内。
- [ ] 第9页包含指标和实验矩阵。
- [ ] 第10页包含 ASR、LRate、Utility/ORR、Score。
- [ ] 至少包含一个 D0 攻击成功案例和一个 D4 防御成功案例。
- [ ] 结论中说明局限和伦理边界。

## 伦理

- [ ] 只使用模拟密钥和模拟攻击目标。
- [ ] 不包含真实 API Key、Cookie、账号或个人隐私。
- [ ] 不测试真实线上系统。
- [ ] 攻击样本仅用于课程评测，没有写成真实攻击教程。

