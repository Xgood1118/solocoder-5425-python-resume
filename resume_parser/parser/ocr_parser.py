import io
import logging
from typing import Tuple
from .base import BaseParser
from ..config import get_settings

logger = logging.getLogger(__name__)


class OCRParser(BaseParser):
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp'}

    def supports(self, filename: str) -> bool:
        ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
        return f'.{ext}' in self.IMAGE_EXTENSIONS

    def parse(self, file_content: bytes, filename: str) -> Tuple[str, dict]:
        settings = get_settings()
        metadata = {
            "parse_method": "ocr",
            "confidence": 0.0,
            "threshold": settings.ocr_confidence_threshold,
        }

        try:
            from PIL import Image
            import pytesseract
        except ImportError as e:
            logger.error(f"OCR dependencies not installed: {e}")
            metadata["parse_method"] = "ocr_error"
            metadata["error"] = "OCR dependencies not installed"
            return "", metadata

        try:
            image = Image.open(io.BytesIO(file_content))

            try:
                ocr_data = pytesseract.image_to_data(image, lang='chi_sim+eng', output_type=pytesseract.Output.DICT)
                confidences = [int(conf) for conf in ocr_data.get('conf', []) if conf != '-1']
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0

                text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                metadata["confidence"] = avg_confidence / 100.0

                if avg_confidence < settings.ocr_confidence_threshold:
                    logger.warning(f"OCR confidence {avg_confidence:.1f}% below threshold {settings.ocr_confidence_threshold}%")
                    metadata["low_confidence"] = True
                    text = ""

            except pytesseract.TesseractError:
                logger.warning("Tesseract error with chi_sim+eng, trying eng only")
                text = pytesseract.image_to_string(image, lang='eng')
                metadata["confidence"] = 0.5
                metadata["fallback_lang"] = "eng"

            return text.strip(), metadata

        except Exception as e:
            logger.error(f"OCR parsing failed: {e}")
            metadata["parse_method"] = "ocr_error"
            metadata["error"] = str(e)
            return "", metadata
