import re
import logging
from typing import List, Tuple, Optional
from ..schemas import WorkExperience
from ..normalize.company import normalize_company

logger = logging.getLogger(__name__)

DATE_PATTERN = re.compile(
    r'(20\d{2}|19\d{2})'
    r'(?:'
    r'[.\-年/\s]*(?:\d{1,2})?\s*[-./至到—–~]\s*'
    r'|'
    r'(?:年|\.\d{1,2})?\s*'
    r')'
    r'(20\d{2}|19\d{2}|至今|现在|present|now|到现在|到今)'
    r'(?:[.\-年/\s]*\d{1,2})?'
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
        stripped = line.strip()
        lower_line = stripped.lower()
        is_section_header = any(kw.lower() in lower_line for kw in keywords) and len(stripped) < 30

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
    stripped = line.strip()
    has_date = bool(DATE_PATTERN.search(stripped))
    has_position = any(kw in stripped for kw in [
        '工程师', '经理', '主管', '总监', '专员', '助理',
        'engineer', 'manager', 'developer', '开发', '设计', '产品', '运营',
        '分析师', '顾问', '教授', '老师', '研究员',
    ])
    has_company_hint = any(kw in stripped for kw in [
        '公司', '集团', '科技', '有限', '股份', 'co.', 'inc.', 'ltd.', 'company',
        '字节', '阿里', '腾讯', '百度', '美团', '京东', '华为', '小米', '网易',
        '滴滴', '快手', 'b站', '哔哩哔哩', '拼多多',
    ])
    has_job_keyword = any(kw in stripped for kw in ['任职', '就职', '工作于', '担任', '曾任'])

    if has_date and (has_position or has_company_hint or has_job_keyword):
        return True

    if has_company_hint and has_position:
        return True

    return False


def _split_entries(lines: List[str]) -> List[str]:
    entries = []
    current_entry: List[str] = []

    def _flush():
        if current_entry:
            entries.append('\n'.join(current_entry))
            current_entry.clear()

    for line in lines:
        stripped = line.strip()
        has_date = bool(DATE_PATTERN.search(stripped))
        has_position = any(kw in stripped for kw in [
            '工程师', '经理', '主管', '总监', '专员', '助理',
            'engineer', 'manager', 'developer',
        ])
        has_company = any(kw in stripped for kw in [
            '公司', '集团', '科技', '有限', '股份', '有限公司',
        ])

        is_new_entry = (has_date and (has_position or has_company)) or (has_company and has_position)
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
    first_line = text.split('\n')[0] if '\n' in text else text

    def _clean_company_name(name: str) -> str:
        if not name:
            return ""
        cleaned = name.strip()
        cleaned = re.sub(r'^[\s\-—–·|/／、,，。.（）()\[\]【】《》""\'`~!@#$%^&*_+={}\\\\<>?]+', '', cleaned)
        cleaned = re.sub(r'[\s\-—–·|/／、,，。.（）()\[\]【】《》""\'`~!@#$%^&*_+={}\\\\<>?]+$', '', cleaned)
        cleaned = re.sub(r'[\(（]?\s*(?:深圳|北京|上海|广州|杭州|成都|武汉|西安|南京|重庆|苏州|天津|青岛|大连|厦门|福州|郑州|长沙|济南|哈尔滨|沈阳|长春|石家庄|太原|合肥|南昌|南宁|昆明|贵阳|拉萨|乌鲁木齐|呼和浩特|银川|西宁)\s*(?:分公司|公司)?[\)）]?', '', cleaned)
        cleaned = re.sub(r'[\(（][^\)）]{0,50}[\)）]', '', cleaned)
        cleaned = re.sub(r'[\[【][^\]】]{0,50}[\]】]', '', cleaned)
        cleaned = re.sub(r'[\-—–·|/／、,，。.]+\s*$', '', cleaned)
        cleaned = re.sub(r'^\s*[\-—–·|/／、,，。.]+', '', cleaned)
        cleaned = cleaned.strip()
        return cleaned

    explicit_patterns = [
        r'(?:^|[\s，,。.；;])(?:就职于|任职于|工作于|曾任于|曾就职于|现就职于|加盟|加入)\s*([\u4e00-\u9fa5A-Za-z0-9·\-（）()]+)',
        r'(?:在)\s*([\u4e00-\u9fa5A-Za-z0-9·\-（）()]+?)\s*(?:担任|任|从事|做|工作)',
    ]
    for pattern in explicit_patterns:
        match = re.search(pattern, first_line)
        if match:
            company = match.group(1).strip()
            company = _clean_company_name(company)
            if _is_valid_company_name(company):
                return company

    date_match = DATE_PATTERN.search(first_line)
    if date_match:
        after_date = first_line[date_match.end():].strip()
        after_date = re.sub(r'^[\s\-—–·|/／、,，。.]+', '', after_date)

        before_date = first_line[:date_match.start()].strip()
        before_date = re.sub(r'[\s\-—–·|/／、,，。.]+$', '', before_date)

        position_keywords = [
            '开发工程师', '研发工程师', '软件工程师', '前端工程师', '后端工程师',
            '算法工程师', '数据工程师', '测试工程师', '运维工程师',
            '产品经理', '产品总监', '运营经理', '设计师', '分析师',
            '架构师', '总经理', '副总经理', '工程师', '经理',
            '主管', '总监', '专员', '助理', '运营',
            '顾问', '教授', '老师', '研究员',
            'CEO', 'CTO', 'COO', 'CFO',
        ]

        def _extract_from_part(part: str) -> Optional[str]:
            pos_end = len(part)
            for kw in position_keywords:
                idx = part.find(kw)
                if idx > 0:
                    pos_end = min(pos_end, idx)

            candidate_part = part[:pos_end].strip()
            candidates = re.split(r'\s{2,}|\t|/|／|、|,|，|\||｜| - | – ', candidate_part)

            for candidate in candidates:
                candidate = candidate.strip()
                candidate = _clean_company_name(candidate)
                if _is_valid_company_name(candidate):
                    return candidate
            return None

        if after_date:
            company = _extract_from_part(after_date)
            if company:
                return company

        if before_date:
            company = _extract_from_part(before_date)
            if company:
                return company

    suffix_patterns = [
        r'(^|[\s，,。.；;])([\u4e00-\u9fa5A-Za-z0-9·\-（）()]+(?:有限公司|股份有限公司|集团有限公司|有限责任公司|集团|公司))',
    ]
    for pattern in suffix_patterns:
        for match in re.finditer(pattern, first_line):
            company = match.group(2).strip()
            company = _clean_company_name(company)
            if _is_valid_company_name(company) and len(company) >= 4:
                return company

    return None


def _is_valid_company_name(name: str) -> bool:
    if not name or len(name) < 2:
        return False

    if any(kw in name for kw in ['职位', '岗位', '职务', '部门', '所属', '时间', '日期', '地点', '地址', '薪资', '工资']):
        return False

    if re.match(r'^(20\d{2}|19\d{2})', name):
        return False

    if re.match(r'^[\d\s\-./]+$', name):
        return False

    if len(name) > 50:
        return False

    return True


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
