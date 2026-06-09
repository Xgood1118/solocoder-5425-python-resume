import re
import logging
from typing import List, Tuple, Optional
from ..schemas import ProjectExperience
from ..normalize.company import normalize_company

logger = logging.getLogger(__name__)

DATE_PATTERN = re.compile(
    r'(20\d{2}|19\d{2})\s*[-./年至到]\s*(20\d{2}|19\d{2}|至今|现在|present|now)'
)

PROJECT_SECTION_KEYWORDS = [
    '项目经历', '项目经验', '项目', '项目背景', '项目介绍',
    'project experience', 'projects', 'project', 'project history',
]

TECH_KEYWORDS = [
    'Python', 'Java', 'C++', 'C#', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin',
    'React', 'Vue', 'Angular', 'Next.js', 'Nuxt.js', 'Svelte', 'Node.js', 'Express', 'Django', 'Flask', 'FastAPI',
    'Spring', 'Spring Boot', 'MyBatis', 'Hibernate',
    'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server', 'Elasticsearch', 'Cassandra',
    'Docker', 'Kubernetes', 'K8s', 'Jenkins', 'Git', 'GitLab', 'GitHub', 'CI/CD',
    'Linux', 'Unix', 'Windows', 'Ubuntu', 'CentOS',
    'AWS', 'Azure', '阿里云', '腾讯云', '华为云', 'Google Cloud', 'GCP',
    'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy',
]


def extract_project_experience(text: str) -> Tuple[List[ProjectExperience], List[str]]:
    """
    抽取项目经历
    返回: (项目经历列表, warnings列表)
    """
    warnings = []
    projects: List[ProjectExperience] = []

    if not text:
        return projects, warnings

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    section_lines = _extract_section_lines(lines, PROJECT_SECTION_KEYWORDS)

    if not section_lines:
        return projects, warnings

    entries = _split_entries(section_lines)
    for entry_text in entries:
        project = _parse_single_project(entry_text, warnings)
        if project:
            projects.append(project)

    projects.sort(key=lambda p: _get_start_year(p.start_date) or 0, reverse=True)

    return projects, warnings


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


def _split_entries(lines: List[str]) -> List[str]:
    entries = []
    current_entry: List[str] = []

    def _flush():
        if current_entry:
            entries.append('\n'.join(current_entry))
            current_entry.clear()

    for line in lines:
        is_new_entry = (DATE_PATTERN.search(line) is not None) and (
            any(kw in line for kw in ['项目', 'project', '系统', '平台', 'app', '网站'])
        )
        if is_new_entry and current_entry:
            _flush()
        current_entry.append(line)

    _flush()
    return entries


def _parse_single_project(text: str, warnings: List[str]) -> Optional[ProjectExperience]:
    project = ProjectExperience()

    date_match = DATE_PATTERN.search(text)
    if date_match:
        project.start_date = date_match.group(1)
        end = date_match.group(2)
        if end in ['至今', '现在', 'present', 'now']:
            project.end_date = '至今'
        else:
            project.end_date = end

    project_name = _extract_project_name(text)
    if project_name:
        project.project_name = project_name

    company = _extract_company(text)
    if company:
        standard_company, conf, comp_warns = normalize_company(company)
        project.company = company
        project.company_standard = standard_company
        warnings.extend(comp_warns)

    role = _extract_role(text)
    if role:
        project.role = role

    tech_stack = _extract_tech_stack(text)
    if tech_stack:
        project.tech_stack = tech_stack

    description = _extract_description(text)
    if description:
        project.description = description

    responsibilities = _extract_responsibilities(text)
    if responsibilities:
        project.responsibilities = responsibilities

    if project.project_name or project.role or project.start_date:
        return project
    return None


def _extract_project_name(text: str) -> Optional[str]:
    patterns = [
        r'项目名(?:称)?\s*[:：]?\s*([^\n，,。]+?)(?:\s|$|，|,|。)',
        r'^([^\n，,。]{2,30}项目)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            name = match.group(1).strip()
            if len(name) >= 2:
                return name
    return None


def _extract_company(text: str) -> Optional[str]:
    patterns = [
        r'(?:公司|所属公司)\s*[:：]?\s*([\u4e00-\u9fa5A-Za-z\s]+(?:公司|集团|科技))',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            company = match.group(1).strip()
            if len(company) >= 2:
                return company
    return None


def _extract_role(text: str) -> Optional[str]:
    patterns = [
        r'(?:角色|职责|担任)\s*[:：]?\s*([\u4e00-\u9fa5A-Za-z\s]+?)(?:\s|$|，|,|。)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            role = match.group(1).strip()
            if len(role) >= 2:
                return role
    return None


def _extract_tech_stack(text: str) -> List[str]:
    techs = []
    lower_text = text.lower()
    for tech in TECH_KEYWORDS:
        if tech.lower() in lower_text and tech not in techs:
            techs.append(tech)
    return techs


def _extract_description(text: str) -> Optional[str]:
    patterns = [
        r'(?:项目描述|简介|介绍|项目简介)\s*[:：]?\s*(.+?)(?:\n\n|$|职责|责任)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            desc = match.group(1).strip()
            if len(desc) >= 5:
                return desc
    return None


def _extract_responsibilities(text: str) -> Optional[str]:
    patterns = [
        r'(?:职责|责任|负责|主要工作|工作内容)\s*[:：]?\s*(.+?)(?:\n\n|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            resp = match.group(1).strip()
            if len(resp) >= 5:
                return resp
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
