import re
import logging
from typing import Optional, Tuple, List
from fuzzywuzzy import fuzz
from ..data.schools import get_school_library

logger = logging.getLogger(__name__)


def _clean_school_name(name: str) -> str:
    """清理学校名称"""
    if not name:
        return ""

    cleaned = name.strip()
    cleaned = re.sub(r'[\(（][^\)）]*[\)）]', '', cleaned)
    cleaned = cleaned.strip()
    return cleaned


def normalize_school(raw_name: str) -> Tuple[Optional[str], List[str], List[str], float]:
    """
    归一化学校名称
    返回: (标准学校名, 学校标签列表, 别名列表, 置信度)
    """
    warnings = []
    if not raw_name:
        return None, [], [], 0.0

    school_dict, alias_to_standard, all_school_names = get_school_library()

    cleaned = _clean_school_name(raw_name)

    if cleaned in alias_to_standard:
        standard = alias_to_standard[cleaned]
        info = school_dict.get(standard, {})
        return standard, info.get("tags", []), info.get("aliases", []), 0.95

    cleaned_lower = cleaned.lower()
    if cleaned_lower in alias_to_standard:
        standard = alias_to_standard[cleaned_lower]
        info = school_dict.get(standard, {})
        return standard, info.get("tags", []), info.get("aliases", []), 0.9

    best_match = None
    best_score = 0
    for school_name in all_school_names:
        score = fuzz.partial_ratio(cleaned, school_name)
        if score > best_score:
            best_score = score
            best_match = school_name

    if best_match and best_score >= 80:
        info = school_dict.get(best_match, {})
        if best_score >= 90:
            confidence = 0.85
        else:
            confidence = best_score / 100.0
            warnings.append(f"学校名 '{raw_name}' 模糊匹配到 '{best_match}'，置信度 {best_score}%")
        return best_match, info.get("tags", []), info.get("aliases", []), confidence
    else:
        warnings.append(f"未匹配到标准学校名: {raw_name}")
        return raw_name, [], [], 0.3
