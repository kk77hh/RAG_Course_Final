# 中文 RAG 安全评测项目（成员韩鹏交付模块）

本项目为《人工智能安全与伦理》课程实践的成员 A 交付模块，负责：

- 中文课程问答 RAG baseline（D0）
- BM25 检索模块
- Prompt 拼接
- 统一 run_rag 接口
- 日志记录
- GitHub 仓库结构初始化

## 项目结构

```bash
memberA_rag_project/
├── src/
├── defenses/
├── data/
├── results/
├── requirements.txt
└── README.md
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行 Demo

```bash
python demo_run.py
```

## 接口说明

统一接口：

```python
run_rag(
    question: str,
    defense_mode: str = "D0",
    top_k: int = 3
)
```

返回格式：

```python
{
    "answer": str,
    "retrieved_docs": list,
    "filtered_docs": list,
    "defense_logs": dict
}
```

## 伦理声明

本项目所有攻击目标、系统提示词和密钥均为模拟内容，仅用于课程安全评测研究。
禁止将项目用于真实攻击场景。