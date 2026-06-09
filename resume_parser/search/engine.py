from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class SearchEngine(ABC):
    @abstractmethod
    def add_document(self, doc_id: str, content: dict) -> None:
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        pass


class InMemorySearch(SearchEngine):
    def __init__(self):
        self._docs: Dict[str, dict] = {}

    def add_document(self, doc_id: str, content: dict) -> None:
        self._docs[doc_id] = content

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        query_lower = query.lower()
        results = []
        for doc_id, content in self._docs.items():
            content_str = str(content).lower()
            if query_lower in content_str:
                results.append({"doc_id": doc_id, "score": 1.0})
                if len(results) >= limit:
                    break
        return results

    def delete_document(self, doc_id: str) -> bool:
        if doc_id in self._docs:
            del self._docs[doc_id]
            return True
        return False


_search_instance: Optional[SearchEngine] = None


def get_search_engine() -> SearchEngine:
    global _search_instance
    if _search_instance is None:
        _search_instance = InMemorySearch()
    return _search_instance
