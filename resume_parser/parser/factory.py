import logging
from typing import Tuple, Optional
from .base import BaseParser
from .pdf_parser import PDFParser
from .word_parser import WordParser
from .ocr_parser import OCRParser

logger = logging.getLogger(__name__)


class ParserFactory:
    def __init__(self):
        self.parsers = [
            PDFParser(),
            WordParser(),
            OCRParser(),
        ]

    def get_parser(self, filename: str) -> Optional[BaseParser]:
        for parser in self.parsers:
            if parser.supports(filename):
                return parser
        return None

    def parse_file(self, file_content: bytes, filename: str) -> Tuple[str, dict]:
        parser = self.get_parser(filename)
        if parser is None:
            logger.warning(f"Unsupported file type: {filename}")
            return "", {
                "parse_method": "unsupported",
                "confidence": 0.0,
                "error": f"Unsupported file type: {filename}",
            }

        text, metadata = parser.parse(file_content, filename)

        if not text and metadata.get("is_scanned"):
            logger.info(f"Scanned PDF detected, falling back to OCR: {filename}")
            ocr_parser = OCRParser()
            ocr_text, ocr_meta = ocr_parser.parse(file_content, filename + ".png")
            if ocr_text:
                metadata["parse_method"] = "ocr_from_scanned_pdf"
                metadata["ocr_confidence"] = ocr_meta.get("confidence", 0)
                metadata["confidence"] = ocr_meta.get("confidence", 0) * 0.8
                text = ocr_text
            else:
                logger.warning(f"OCR fallback also failed for scanned PDF: {filename}")
                metadata["parse_method"] = "scanned_pdf_ocr_failed"
                metadata["error"] = "Scanned PDF could not be parsed by OCR"

        return text, metadata


factory = ParserFactory()
