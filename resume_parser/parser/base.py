from abc import ABC, abstractmethod
from typing import Tuple, Optional


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_content: bytes, filename: str) -> Tuple[str, dict]:
        """
        解析文件，返回 (原始文本, 元数据)
        元数据包含 parse_method, confidence 等信息
        """
        pass

    @abstractmethod
    def supports(self, filename: str) -> bool:
        """判断是否支持该文件类型"""
        pass
