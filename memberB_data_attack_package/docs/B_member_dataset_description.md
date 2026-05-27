# 成员B数据集说明

生成日期：2026-05-23

## 分工定位

成员B负责数据集构建与攻击实验，目标是让项目有完整样本、有可复现 D0 攻击结果、有可用于 PPT 的典型案例。

## 文件清单

| 文件 | 数量 | 用途 | 对接对象 |
|---|---:|---|---|
| `data/kb_normal.jsonl` | 40 | 正常知识库文档 | 成员A检索模块 |
| `data/kb_malicious.jsonl` | 20 | 间接提示注入与任务劫持恶意文档 | 成员A/C |
| `data/questions_normal.jsonl` | 80 | 正常问答 Utility/ORR 测试 | 成员D |
| `data/questions_attack.jsonl` | 80 | 五类攻击样本 D0-D4 测试 | 成员D |
| `data/dataset_manifest.json` | 1 | 数据规模和伦理说明 | 全员 |

## 正常问答分布

| 类型 | 数量 |
|---|---:|
| normal_course_faq | 40 |
| normal_campus_faq | 20 |
| normal_ai_security_concept | 20 |

## 攻击样本分布

| 类型 | 数量 |
|---|---:|
| direct_injection | 20 |
| indirect_doc_injection | 20 |
| obfuscated_injection | 20 |
| task_hijack | 10 |
| sensitive_info_induction | 10 |

## 字段说明

知识库文档字段：

| 字段 | 含义 |
|---|---|
| `doc_id` | 文档唯一编号，正常文档使用 `normal_doc_*`，恶意文档使用 `mal_doc_*` |
| `source` | 文档来源或主题标签 |
| `content` | 文档正文，可直接被成员A的 `load_kb()` 读取 |

问题样本字段：

| 字段 | 含义 |
|---|---|
| `id` | 样本唯一编号 |
| `type` | 样本类型，例如 `direct_injection` 或 `normal_course_faq` |
| `question` | 用户输入 |
| `expected_behavior` | 安全期望行为 |
| `expected_answer_keywords` | 正常问答自动判断关键词 |
| `attack_goal` | 攻击目标，仅攻击样本使用 |
| `success_rule` | 攻击成功判定口径 |
| `success_keywords` | 自动判定辅助关键词 |
| `target_doc_id` | 间接注入样本对应恶意文档 |

## 伦理边界

所有密钥、系统提示词和攻击目标均为课程模拟内容。数据集中使用的 `COURSE_SECRET_4F9A_DO_NOT_OUTPUT` 不是真实密钥，不对应任何真实账号、真实 API Key 或真实个人隐私。
