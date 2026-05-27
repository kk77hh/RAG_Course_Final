try:
    from rank_bm25 import BM25Okapi
except ImportError:  # Keep the baseline runnable in minimal course envs.
    BM25Okapi = None


def _tokenize(text):
    text = text or ""
    rough_tokens = text.lower().split()
    if len(rough_tokens) > 1:
        return rough_tokens
    # Chinese course questions often have no spaces. Character bigrams provide a
    # small but dependency-free fallback that works well enough for this demo.
    compact = "".join(text.lower().split())
    return [compact[i : i + 2] for i in range(max(0, len(compact) - 1))] or [compact]

class BM25Retriever:
    def __init__(self, documents):
        self.documents = documents
        self.corpus = [doc["content"] for doc in documents]
        self.tokenized_corpus = [_tokenize(text) for text in self.corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus) if BM25Okapi else None

    def search(self, query, top_k=3):
        tokenized_query = _tokenize(query)
        if self.bm25:
            scores = self.bm25.get_scores(tokenized_query)
        else:
            query_terms = set(tokenized_query)
            scores = [
                len(query_terms.intersection(set(doc_terms))) / max(1, len(query_terms))
                for doc_terms in self.tokenized_corpus
            ]

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "doc_id": doc["doc_id"],
                "doc_type": doc.get("doc_type", "unknown"),
                "source": doc.get("source", "unknown"),
                "content": doc["content"],
                "score": float(score)
            }
            for doc, score in ranked[:top_k]
        ]
