import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

CHINESE_NAME_PATTERN = re.compile(r'^[\u4e00-\u9fa5]{2,4}(?:·[\u4e00-\u9fa5]+)?$')
ENGLISH_NAME_PATTERN = re.compile(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b')
NAME_WITH_ENGLISH_PATTERN = re.compile(
    r'([\u4e00-\u9fa5]{2,4})\s*[\(（]\s*([A-Za-z\s]+)\s*[\)）]'
)


def extract_name(text: str, ocr_confidence: float = 1.0) -> Tuple[Optional[str], Optional[str], float]:
    """
    抽取姓名
    返回: (中文名, 英文名, 置信度)
    """
    if not text:
        return None, None, 0.0

    chinese_name = None
    english_name = None
    confidence = 0.0

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    if not lines:
        return None, None, 0.0

    for i, line in enumerate(lines[:10]):
        match = NAME_WITH_ENGLISH_PATTERN.search(line)
        if match:
            chinese_name = match.group(1)
            english_name = match.group(2).strip()
            confidence = 0.9 if i < 3 else 0.7
            break

    if not chinese_name:
        for i, line in enumerate(lines[:10]):
            clean_line = re.sub(r'[\s\-_]+', '', line)
            if CHINESE_NAME_PATTERN.match(clean_line) and len(clean_line) >= 2 and len(clean_line) <= 4:
                if not _is_common_word(clean_line):
                    chinese_name = clean_line
                    confidence = 0.85 if i < 3 else 0.6
                    break

    if not english_name:
        for i, line in enumerate(lines[:10]):
            matches = ENGLISH_NAME_PATTERN.findall(line)
            if matches and chinese_name:
                for m in matches:
                    if m.lower() not in ['resume', 'curriculum', 'vitae', 'cv']:
                        english_name = m
                        confidence = min(confidence + 0.05, 0.95)
                        break
                if english_name:
                    break

    if chinese_name and ocr_confidence < 0.6:
        confidence = min(confidence, ocr_confidence)
        if confidence < 0.4:
            logger.debug(f"OCR confidence too low ({ocr_confidence}), discarding name")
            return None, None, 0.0

    return chinese_name, english_name, confidence


def _is_common_word(text: str) -> bool:
    common_words = {
        '简历', '个人', '基本', '信息', '教育', '背景', '工作', '经历',
        '项目', '经验', '技能', '特长', '求职', '意向', '联系', '方式',
        '姓名', '性别', '年龄', '籍贯', '住址', '手机', '邮箱', '电话',
        '专业', '学校', '学历', '毕业', '时间', '公司', '职位', '部门',
    }
    return text in common_words
