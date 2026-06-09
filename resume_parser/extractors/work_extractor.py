import re
import logging
from typing import List, Tuple, Optional
from ..schemas import WorkExperience
from ..normalize.company import normalize_company

logger = logging.getLogger(__name__)

DATE_PATTERN = re.compile(
    r'(20\d{2}|19\d{2})\s*[-./年至到]\s*(20\d{2}|19\d{2}|至今|现在|present|now)'
)

WORK_SECTION_KEYWORDS = [
    '工作经历', '工作经验', '工作', '职业经历', '工作背景', '从业经历',
    'work experience', 'experience', 'employment', 'work history', 'professional experience',
]


def extract_work_experience(text: str) -> Tuple[List[WorkExperience], List[str]]:
    """
    抽取工作经历
    返回: (工作经历列表, warnings列表)
    """
    warnings = []
    work_list: List[WorkExperience] = []

    if not text:
        return work_list, warnings

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    section_lines = _extract_section_lines(lines, WORK_SECTION_KEYWORDS)

    if not section_lines:
        section_lines = _find_work_by_patterns(lines)

    if not section_lines:
        return work_list, warnings

    entries = _split_entries(section_lines)
    for entry_text in entries:
        work = _parse_single_work(entry_text, warnings)
        if work:
            work_list.append(work)

    work_list.sort(key=lambda w: _get_start_year(w.start_date) or 0, reverse=True)

    return work_list, warnings


def _extract_section_lines(lines: List[str], keywords: List[str]) -> List[str]:
    section_lines = []
    in_section = False
    section_start_idx = -1

    for i, line in enumerate(lines):
        lower_line = line.lower().strip()
        is_section_header = any(kw.lower() in lower_line for kw in keywords) and len(line) < 20

        if is_section_header and not in_section:
            in_section = True
            section_start_idx = i
            continue

        if in_section and is_section_header and i > section_start_idx + 1:
            break

        if in_section:
            section_lines.append(line)

    return section_lines


def _find_work_by_patterns(lines: List[str]) -> List[str]:
    work_lines = []
    for line in lines:
        if _is_work_line(line):
            work_lines.append(line)
    return work_lines


def _is_work_line(line: str) -> bool:
    has_company = any(kw in line for kw in ['公司', '集团', '科技', '有限', '股份', 'co.', 'inc.', 'ltd.', 'company'])
    has_date = bool(DATE_PATTERN.search(line))
    has_position = any(kw in line for kw in ['工程师', '经理', '主管', '总监', '专员', '助理', 'engineer', 'manager', 'developer'])
    return has_company and (has_date or has_position)


def _split_entries(lines: List[str]) -> List[str]:
    entries = []
    current_entry: List[str] = []

    def _flush():
        if current_entry:
            entries.append('\n'.join(current_entry))
            current_entry.clear()

    for line in lines:
        is_new_entry = bool(DATE_PATTERN.search(line)) and any(kw in line for kw in ['公司', '集团', '科技', '有限'])
        if is_new_entry and current_entry:
            _flush()
        current_entry.append(line)

    _flush()
    return entries


def _parse_single_work(text: str, warnings: List[str]) -> Optional[WorkExperience]:
    work = WorkExperience()

    date_match = DATE_PATTERN.search(text)
    if date_match:
        work.start_date = date_match.group(1)
        end = date_match.group(2)
        if end in ['至今', '现在', 'present', 'now']:
            work.end_date = '至今'
            work.is_current = True
        else:
            work.end_date = end

    company = _extract_company(text)
    if company:
        standard_company, conf, comp_warns = normalize_company(company)
        work.company = company
        work.company_standard = standard_company
        warnings.extend(comp_warns)

    position = _extract_position(text)
    if position:
        work.position = position

    department = _extract_department(text)
    if department:
        work.department = department

    description = _extract_description(text)
    if description:
        work.description = description

    if work.company or work.position or work.start_date:
        return work
    return None


def _extract_company(text: str) -> Optional[str]:
    patterns = [
        r'([\u4e00-\u9fa5A-Za-z\s]+(?:公司|集团|科技|技术|有限公司|股份有限公司))',
        r'(?:就职于|任职于|工作于|在)\s*([\u4e00-\u9fa5A-Za-z\s]+?)(?:\s|$|，|,|。)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            company = match.group(1).strip()
            if len(company) >= 2:
                return company
    return None


def _extract_position(text: str) -> Optional[str]:
    patterns = [
        r'(?:职位|岗位|职务|担任)\s*[:：]?\s*([\u4e00-\u9fa5A-Za-z\s]+?)(?:\s|$|，|,|。)',
        r'([\u4e00-\u9fa5]{2,10}(?:工程师|经理|主管|总监|专员|助理|开发|设计|产品))',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            pos = match.group(1).strip()
            if len(pos) >= 2:
                return pos
    return None


def _extract_department(text: str) -> Optional[str]:
    patterns = [
        r'(?:部门|所属部门|所在部门)\s*[:：]?\s*([\u4e00-\u9fa5A-Za-z\s]+?)(?:\s|$|，|,|。)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            dept = match.group(1).strip()
            if len(dept) >= 2:
                return dept
    return None


def _extract_description(text: str) -> Optional[str]:
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if len(lines) > 1:
        desc_lines = []
        for line in lines[1:]:
            if not DATE_PATTERN.search(line) and not any(kw in line for kw in ['公司', '集团', '职位']):
                desc_lines.append(line)
        if desc_lines:
            return '\n'.join(desc_lines)
    return None


def _get_start_year(start_date: Optional[str]) -> int:
    if not start_date:
        return 0
    try:
        year_match = re.search(r'(20\d{2}|19\d{2})', start_date)
        if year_match:
            return int(year_match.group(1))
    except Exception:
        pass
    return 0
