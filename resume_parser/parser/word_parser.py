import io
import logging
from typing import Tuple
from .base import BaseParser

logger = logging.getLogger(__name__)


class WordParser(BaseParser):
    def supports(self, filename: str) -> bool:
        return filename.lower().endswith(('.docx', '.doc'))

    def parse(self, file_content: bytes, filename: str) -> Tuple[str, dict]:
        metadata = {
            "parse_method": "word",
            "confidence": 1.0,
            "paragraph_count": 0,
            "table_count": 0,
        }
        try:
            from docx import Document
        except ImportError:
            logger.error("python-docx not installed")
            metadata["parse_method"] = "word_error"
            metadata["confidence"] = 0.0
            metadata["error"] = "python-docx not installed"
            return "", metadata

        try:
            text_parts = []
            doc = Document(io.BytesIO(file_content))

            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text.strip())
            metadata["paragraph_count"] = len(doc.paragraphs)

            for table in doc.tables:
                metadata["table_count"] += 1
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells]
                    row_text = " | ".join(row_cells)
                    if row_text.strip():
                        text_parts.append(row_text)

            full_text = "\n".join(text_parts).strip()
            metadata["confidence"] = 0.95

            return full_text, metadata

        except Exception as e:
            logger.error(f"Word parsing failed: {e}")
            metadata["parse_method"] = "word_error"
            metadata["confidence"] = 0.0
            metadata["error"] = str(e)
            return "", metadata
