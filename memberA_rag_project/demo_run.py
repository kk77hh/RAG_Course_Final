from src.rag_pipeline import run_rag

if __name__ == "__main__":
    question = "课程实践最终什么时候提交？"

    result = run_rag(
        question=question,
        defense_mode="D0",
        top_k=3
    )

    print("=== ANSWER ===")
    print(result["answer"])

    print("\n=== RETRIEVED DOCS ===")
    for doc in result["retrieved_docs"]:
        print("-", doc["content"])