import io
import logging
from typing import Tuple
from .base import BaseParser

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    def supports(self, filename: str) -> bool:
        return filename.lower().endswith('.pdf')

    def parse(self, file_content: bytes, filename: str) -> Tuple[str, dict]:
        metadata = {
            "parse_method": "pdf",
            "confidence": 1.0,
            "page_count": 0,
            "is_scanned": False,
        }
        try:
            import pdfplumber
        except ImportError:
            logger.warning("pdfplumber not installed, falling back to OCR for PDF")
            metadata["parse_method"] = "ocr_fallback"
            metadata["confidence"] = 0.5
            return "", metadata

        try:
            text_parts = []
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                metadata["page_count"] = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text_parts.append(page_text)
                    tables = page.extract_tables() or []
                    for table in tables:
                        for row in table:
                            row_text = " | ".join([str(cell) if cell else "" for cell in row])
                            text_parts.append(row_text)

            full_text = "\n".join(text_parts).strip()

            if len(full_text) < 50:
                logger.warning(f"PDF text extraction returned very little text ({len(full_text)} chars), likely scanned PDF")
                metadata["is_scanned"] = True
                metadata["confidence"] = 0.3
                metadata["parse_method"] = "pdf_scanned"
            else:
                metadata["confidence"] = 0.9

            return full_text, metadata

        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            metadata["parse_method"] = "pdf_error"
            metadata["confidence"] = 0.0
            metadata["error"] = str(e)
            return "", metadata
