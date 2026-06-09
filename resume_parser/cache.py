import hashlib
import logging
from collections import OrderedDict
from typing import Optional, Any
from .config import get_settings

logger = logging.getLogger(__name__)


def compute_file_hash(file_content: bytes) -> str:
    """计算文件内容的 SHA-256 哈希"""
    return hashlib.sha256(file_content).hexdigest()


class LRUCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存，命中则移动到末尾（最近使用）"""
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存，如果超过容量则淘汰最老的"""
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        while len(self._cache) > self.max_size:
            oldest_key = next(iter(self._cache))
            self._cache.popitem(last=False)
            logger.debug(f"Cache evicted: {oldest_key}")

    def __len__(self) -> int:
        return len(self._cache)

    def size(self) -> int:
        return len(self._cache)

    def clear(self) -> None:
        self._cache.clear()

    def has(self, key: str) -> bool:
        return key in self._cache


_cache_instance: Optional[LRUCache] = None


def get_cache() -> LRUCache:
    """获取全局缓存单例"""
    global _cache_instance
    if _cache_instance is None:
        settings = get_settings()
        _cache_instance = LRUCache(max_size=settings.cache_max_size)
    return _cache_instance
