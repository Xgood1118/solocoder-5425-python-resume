import re
import logging
import datetime
from typing import List, Optional, Tuple
from ..schemas import ResumeParseResult, EnhancedInfo, Education
from ..data.schools import get_school_library

logger = logging.getLogger(__name__)


def enhance_result(result: ResumeParseResult) -> ResumeParseResult:
    """增强简历解析结果，添加派生信息"""
    if result.enhanced is None:
        result.enhanced = EnhancedInfo()

    _enhance_school_level(result)
    _enhance_work_experience_years(result)
    _enhance_age_range(result)
    _enhance_top_school(result)
    _enhance_qs_rank(result)

    return result


def _enhance_school_level(result: ResumeParseResult):
    """计算学校层级（最高学历对应的学校层级）"""
    if not result.education:
        return

    highest_edu = None
    degree_rank = {
        '博士': 4,
        '硕士': 3,
        '本科': 2,
        '大专': 1,
    }
    highest_rank = 0

    for edu in result.education:
        rank = degree_rank.get(edu.degree or '', 0)
        if rank > highest_rank:
            highest_rank = rank
            highest_edu = edu

    if highest_edu and highest_edu.school_tags:
        tags = highest_edu.school_tags
        if '985' in tags:
            result.enhanced.school_level = '985'
        elif '211' in tags:
            result.enhanced.school_level = '211'
        elif '双一流' in tags:
            result.enhanced.school_level = '双一流'
        elif 'QS100' in tags:
            result.enhanced.school_level = 'QS100'
        else:
            result.enhanced.school_level = '普通'
    elif highest_edu:
        result.enhanced.school_level = '普通'


def _enhance_work_experience_years(result: ResumeParseResult):
    """计算总工作年限"""
    if not result.work_experience:
        return

    total_years = 0.0
    current_year = datetime.datetime.now().year

    for work in result.work_experience:
        start_year = _extract_year(work.start_date)
        end_year = _extract_year(work.end_date)

        if work.is_current or work.end_date in ['至今', '现在', 'present', 'now']:
            end_year = current_year

        if start_year and end_year and end_year >= start_year:
            total_years += (end_year - start_year)

    if total_years > 0:
        result.enhanced.total_years_of_experience = round(total_years, 1)


def _enhance_age_range(result: ResumeParseResult):
    """根据工作年限和毕业时间推算年龄段"""
    if result.enhanced.total_years_of_experience:
        years = result.enhanced.total_years_of_experience
        grad_age = 22
        min_age = int(grad_age + years)
        max_age = int(min_age + 5)
        result.enhanced.age_range = f"{min_age}-{max_age}"
        return

    if result.education:
        for edu in result.education:
            end_year = _extract_year(edu.end_date)
            if end_year:
                grad_age = 22 if edu.degree in ['本科', '大专'] else 25 if edu.degree == '硕士' else 28 if edu.degree == '博士' else 22
                current_year = datetime.datetime.now().year
                age = current_year - end_year + grad_age
                min_age = max(20, age - 2)
                max_age = age + 3
                result.enhanced.age_range = f"{min_age}-{max_age}"
                break


def _enhance_top_school(result: ResumeParseResult):
    """判断是否为顶尖学校"""
    if not result.education:
        return

    top_tags = {'985', 'QS100'}
    for edu in result.education:
        if any(tag in top_tags for tag in edu.school_tags):
            result.enhanced.is_top_school = True
            break


def _enhance_qs_rank(result: ResumeParseResult):
    """获取 QS 排名（如果有）"""
    if not result.education:
        return

    school_dict, _, _ = get_school_library()

    best_rank = None
    for edu in result.education:
        school_name = edu.school_standard or edu.school
        if school_name and school_name in school_dict:
            info = school_dict[school_name]
            qs_rank = info.get("qs_rank")
            if qs_rank and (best_rank is None or qs_rank < best_rank):
                best_rank = qs_rank

    if best_rank:
        result.enhanced.qs_rank = best_rank


def _extract_year(date_str: Optional[str]) -> Optional[int]:
    if not date_str:
        return None
    match = re.search(r'(20\d{2}|19\d{2})', date_str)
    if match:
        return int(match.group(1))
    return None
