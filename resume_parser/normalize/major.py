import re
import logging
from typing import Optional, Tuple, List
from fuzzywuzzy import fuzz
from ..data.majors import get_major_library

logger = logging.getLogger(__name__)


def _clean_major_name(name: str) -> str:
    if not name:
        return ""

    cleaned = name.strip()
    cleaned = re.sub(r'[\(（][^\)）]*[\)）]', '', cleaned)
    cleaned = re.sub(r'(专业|方向|类)$', '', cleaned)
    return cleaned.strip()


def normalize_major(raw_name: str) -> Tuple[Optional[str], float, List[str]]:
    """
    归一化专业名称
    返回: (标准专业名, 置信度, warnings列表)
    """
    warnings = []
    if not raw_name:
        return None, 0.0, warnings

    major_lib = get_major_library()

    cleaned = _clean_major_name(raw_name)

    if cleaned in major_lib:
        return major_lib[cleaned], 0.95, warnings

    best_match = None
    best_score = 0
    for major_name in major_lib.values():
        score = fuzz.partial_ratio(cleaned, major_name)
        if score > best_score:
            best_score = score
            best_match = major_name

    if best_match and best_score >= 75:
        if best_score >= 90:
            confidence = 0.85
        else:
            confidence = best_score / 100.0
            warnings.append(f"专业名 '{raw_name}' 模糊匹配到 '{best_match}'，置信度 {best_score}%")
        return best_match, confidence, warnings
    else:
        warnings.append(f"未匹配到标准专业名: {raw_name}")
        return raw_name, 0.3, warnings
