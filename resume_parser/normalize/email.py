import re
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(
    r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
)


def normalize_email(raw_email: str) -> Tuple[Optional[str], float]:
    """归一化邮箱，返回 (标准化邮箱, 置信度)"""
    if not raw_email:
        return None, 0.0

    email = raw_email.strip().lower()

    if EMAIL_REGEX.fullmatch(email):
        return email, 0.99

    match = EMAIL_REGEX.search(email)
    if match:
        return match.group(0).lower(), 0.85

    return None, 0.0


def find_emails(text: str) -> List[Tuple[str, float, str]]:
    """从文本中找出所有邮箱，返回 [(邮箱, 置信度, 原始匹配字符串)]"""
    if not text:
        return []

    matches = EMAIL_REGEX.findall(text)
    results = []
    seen = set()
    for match in matches:
        email, conf = normalize_email(match)
        if email and email not in seen:
            seen.add(email)
            results.append((email, conf, match))

    return results
