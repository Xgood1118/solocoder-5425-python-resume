import re
import logging
from typing import Optional, Tuple, List
from fuzzywuzzy import fuzz
from ..data.companies import get_company_library

logger = logging.getLogger(__name__)

COMPANY_SUFFIX_PATTERN = re.compile(
    r'(有限公司|股份有限公司|集团有限公司|集团|公司|科技|技术|有限责任公司|责任有限公司|控股|实业|贸易|咨询|服务)$'
)


def _clean_company_name(name: str) -> str:
    """清理公司名称，去除常见后缀、括号内容等"""
    if not name:
        return ""

    cleaned = name.strip()

    cleaned = re.sub(r'[\(（][^\)）]*[\)）]', '', cleaned)

    cleaned = cleaned.strip()

    return cleaned


def normalize_company(raw_name: str) -> Tuple[Optional[str], float, List[str]]:
    """
    归一化公司名称
    返回: (标准公司名, 置信度, warnings列表)
    """
    warnings = []
    if not raw_name:
        return None, 0.0, warnings

    company_lib = get_company_library()

    if raw_name in company_lib:
        return company_lib[raw_name], 0.95, warnings

    raw_lower = raw_name.lower()
    if raw_lower in company_lib:
        return company_lib[raw_lower], 0.9, warnings

    cleaned = _clean_company_name(raw_name)
    if cleaned in company_lib:
        return company_lib[cleaned], 0.85, warnings

    cleaned_lower = cleaned.lower()
    if cleaned_lower in company_lib:
        return company_lib[cleaned_lower], 0.8, warnings

    best_match = None
    best_score = 0
    for alias, standard in company_lib.items():
        score = fuzz.partial_ratio(raw_name, alias)
        if score > best_score:
            best_score = score
            best_match = standard

    if best_score >= 85 and best_match:
        return best_match, best_score / 100.0, warnings
    elif best_score >= 70 and best_match:
        warnings.append(f"公司名 '{raw_name}' 模糊匹配到 '{best_match}'，置信度 {best_score}%")
        return best_match, best_score / 100.0, warnings
    else:
        warnings.append(f"未匹配到标准公司名: {raw_name}")
        return raw_name, 0.3, warnings
