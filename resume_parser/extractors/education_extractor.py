import re
import logging
from typing import List, Tuple, Optional
from ..schemas import Education
from ..normalize.school import normalize_school
from ..normalize.major import normalize_major

logger = logging.getLogger(__name__)

DATE_PATTERN = re.compile(
    r'(20\d{2}|19\d{2})\s*[-./年至到]\s*(20\d{2}|19\d{2}|至今|现在|present|now)'
)
YEAR_ONLY_PATTERN = re.compile(r'(20\d{2}|19\d{2})')

DEGREE_KEYWORDS = {
    '博士': '博士', 'phd': '博士', 'ph.d': '博士', 'doctor': '博士', 'doctorate': '博士',
    '硕士': '硕士', 'master': '硕士', '研究生': '硕士', 'ma': '硕士', 'ms': '硕士', 'mba': '硕士',
    '本科': '本科', '学士': '本科', 'bachelor': '本科', 'ba': '本科', 'bs': '本科', 'bsc': '本科',
    '大专': '大专', '专科': '大专', 'college': '大专', 'associate': '大专',
    '高中': '高中', '中专': '中专', '职高': '职高',
}

EDUCATION_SECTION_KEYWORDS = [
    '教育背景', '教育经历', '教育程度', '教育', '学历', '教育与培训',
    'academic background', 'education', 'educational background',
]


def extract_education(text: str) -> Tuple[List[Education], List[str]]:
    """
    抽取教育经历
    返回: (教育经历列表, warnings列表)
    """
    warnings = []
    educations: List[Education] = []

    if not text:
        return educations, warnings

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    section_ranges = _find_sections(lines)

    edu_lines = []
    for start, end in section_ranges.get('education', []):
        edu_lines.extend(lines[start:end])

    if not edu_lines:
        edu_lines = _find_education_by_patterns(lines)

    if not edu_lines:
        return educations, warnings

    educations = _parse_education_entries(edu_lines, warnings)

    educations.sort(key=lambda e: _get_end_year(e.end_date) or 0, reverse=True)

    return educations, warnings


def _find_sections(lines: List[str]) -> dict:
    sections = {}
    section_starts = []

    for i, line in enumerate(lines):
        lower_line = line.lower().strip()
        for kw in EDUCATION_SECTION_KEYWORDS:
            if kw.lower() in lower_line and len(line) < 20:
                section_starts.append(('education', i))
                break

    if section_starts:
        section_starts.sort(key=lambda x: x[1])
        for idx, (sec_type, start) in enumerate(section_starts):
            next_start = section_starts[idx + 1][1] if idx + 1 < len(section_starts) else len(lines)
            sections.setdefault(sec_type, []).append((start + 1, next_start))

    return sections


def _find_education_by_patterns(lines: List[str]) -> List[str]:
    edu_lines = []
    for line in lines:
        if _is_education_line(line):
            edu_lines.append(line)
    return edu_lines


def _is_education_line(line: str) -> bool:
    lower = line.lower()
    has_school = any(kw in line for kw in ['大学', '学院', '学校', 'university', 'college', 'institute', 'academy'])
    has_date = bool(DATE_PATTERN.search(line) or YEAR_ONLY_PATTERN.search(line))
    has_degree = any(kw.lower() in lower for kw in DEGREE_KEYWORDS.keys())
    return has_school and (has_date or has_degree)


def _parse_education_entries(lines: List[str], warnings: List[str]) -> List[Education]:
    educations: List[Education] = []
    current_entry_lines: List[str] = []

    def _flush_entry():
        if current_entry_lines:
            entry_text = ' '.join(current_entry_lines)
            edu = _parse_single_education(entry_text, warnings)
            if edu:
                educations.append(edu)
            current_entry_lines.clear()

    for line in lines:
        is_new_entry = bool(DATE_PATTERN.search(line)) or _starts_with_school(line)
        if is_new_entry and current_entry_lines:
            _flush_entry()
        current_entry_lines.append(line)

    _flush_entry()

    return educations


def _starts_with_school(line: str) -> bool:
    return any(kw in line for kw in ['大学', '学院', '学校']) and len(line) > 5


def _parse_single_education(text: str, warnings: List[str]) -> Optional[Education]:
    edu = Education()

    date_match = DATE_PATTERN.search(text)
    if date_match:
        edu.start_date = date_match.group(1)
        end = date_match.group(2)
        if end in ['至今', '现在', 'present', 'now']:
            edu.end_date = '至今'
        else:
            edu.end_date = end
    else:
        years = YEAR_ONLY_PATTERN.findall(text)
        if len(years) >= 2:
            edu.start_date = years[0]
            edu.end_date = years[1]
        elif len(years) == 1:
            edu.end_date = years[0]

    degree = _extract_degree(text)
    edu.degree = degree

    school_name = _extract_school_name(text)
    if school_name:
        standard_school, tags, aliases, conf = normalize_school(school_name)
        edu.school = school_name
        edu.school_standard = standard_school
        edu.school_tags = tags
        edu.confidence = conf

    major = _extract_major(text)
    if major:
        standard_major, maj_conf, maj_warns = normalize_major(major)
        edu.major = major
        edu.major_standard = standard_major
        edu.confidence = max(edu.confidence, maj_conf)
        warnings.extend(maj_warns)

    if edu.school or edu.major or edu.degree:
        return edu
    return None


def _extract_degree(text: str) -> Optional[str]:
    lower = text.lower()
    for keyword, degree in DEGREE_KEYWORDS.items():
        if keyword.lower() in lower:
            return degree
    return None


def _extract_school_name(text: str) -> Optional[str]:
    patterns = [
        r'([\u4e00-\u9fa5]{2,15}(?:大学|学院|学校))',
        r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:\sUniversity|\sCollege|\sInstitute))',
        r'((?:University|College|Institute)\sof\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def _extract_major(text: str) -> Optional[str]:
    major_patterns = [
        r'(?:专业|主修|方向)\s*[:：]?\s*([\u4e00-\u9fa5A-Za-z0-9\s·\-]+?)(?:\s|$|,|，)',
        r'([\u4e00-\u9fa5]{2,10}(?:工程|技术|科学|学|专业))',
    ]
    for pattern in major_patterns:
        match = re.search(pattern, text)
        if match:
            major = match.group(1).strip()
            if len(major) >= 2:
                return major
    return None


def _get_end_year(end_date: Optional[str]) -> int:
    if not end_date or end_date in ['至今', '现在']:
        import datetime
        return datetime.datetime.now().year
    try:
        year_match = re.search(r'(20\d{2}|19\d{2})', end_date)
        if year_match:
            return int(year_match.group(1))
    except Exception:
        pass
    return 0
