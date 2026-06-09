import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

PHONE_REGEX = re.compile(r'(?:\+?86)?[\s-]?1[3-9]\d[\s-]?\d{4}[\s-]?\d{4}')
PHONE_ONLY_DIGITS_REGEX = re.compile(r'\d{11,}')


def normalize_phone(raw_phone: str) -> Tuple[Optional[str], float, list]:
    """
    归一化手机号
    返回: (标准化手机号, 置信度, warnings列表)
    """
    warnings = []
    if not raw_phone:
        return None, 0.0, warnings

    digits_only = re.sub(r'[^\d]', '', raw_phone)

    if len(digits_only) < 11:
        return None, 0.0, warnings

    has_country_code = False
    if digits_only.startswith('86') and len(digits_only) >= 13:
        digits_only = digits_only[2:]
        has_country_code = True

    if len(digits_only) > 11:
        logger.debug(f"Phone number too long ({len(digits_only)} digits after country code), skipping: {raw_phone}")
        return None, 0.0, warnings

    if len(digits_only) == 11 and digits_only.startswith('1') and digits_only[1] in '3456789':
        confidence = 0.95
        if has_country_code or raw_phone.startswith('+86'):
            confidence = 0.98
        return digits_only, confidence, warnings
    elif len(digits_only) == 11:
        warnings.append(f"手机号格式存疑: {raw_phone}")
        return digits_only, 0.6, warnings

    return None, 0.0, warnings


def find_phones(text: str) -> list:
    """从文本中找出所有可能的手机号"""
    if not text:
        return []

    matches = PHONE_REGEX.findall(text)
    phones = []
    for match in matches:
        phone, conf, warns = normalize_phone(match)
        if phone:
            phones.append((phone, conf, match, warns))

    all_digit_matches = PHONE_ONLY_DIGITS_REGEX.findall(text)
    for match in all_digit_matches:
        if len(match) == 11 and match.startswith('1') and match[1] in '3456789':
            phone, conf, warns = normalize_phone(match)
            if phone and phone not in [p[0] for p in phones]:
                phones.append((phone, conf, match, warns))

    return phones
