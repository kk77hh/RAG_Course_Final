from src.utils import read_jsonl

def load_kb(normal_path, malicious_path=None):
    docs = []

    normal_docs = read_jsonl(normal_path)
    for item in normal_docs:
        item["doc_type"] = "normal"
        docs.append(item)

    if malicious_path:
        malicious_docs = read_jsonl(malicious_path)
        for item in malicious_docs:
            item["doc_type"] = "malicious"
            docs.append(item)

    return docs