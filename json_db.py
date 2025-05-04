import json
import os
import threading
from datetime import datetime
import numpy as np

class JSONDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({"documents": []}, f)

    def create(self, record: dict) -> str:
        with self.lock:
            with open(self.db_path, 'r+') as f:
                data = json.load(f)
                record_id = str(len(data["documents"]) + 1)
                record.update({
                    "id": record_id,
                    "created_at": datetime.now().isoformat(),
                    "citations": record.get("citations", {"cohere": [], "scholar": []})
                })
                data["documents"].append(record)
                f.seek(0)
                json.dump(data, f, indent=2)
        return record_id

    def find_similar(self, embedding: list, threshold: float = 0.7) -> list:
        with self.lock:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                results = []
                for doc in data["documents"]:
                    if 'embedding' in doc:
                        similarity = self._cosine_similarity(embedding, doc['embedding'])
                        if similarity > threshold:
                            results.append({
                                "id": doc["id"],
                                "similarity": similarity,
                                "content": doc.get("content", "")[:200]
                            })
                return sorted(results, key=lambda x: x["similarity"], reverse=True)

    def _cosine_similarity(self, vec1: list, vec2: list) -> float:
        dot = np.dot(vec1, vec2)
        norm = (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return dot / norm if norm != 0 else 0.0