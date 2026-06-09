import re
import logging
from typing import Tuple, List, Dict
from collections import Counter
from ..schemas import SkillCategory, SkillItem

logger = logging.getLogger(__name__)

PROGRAMMING_LANGUAGES = [
    'Python', 'Java', 'C++', 'C#', 'C', 'JavaScript', 'TypeScript', 'Go', 'Golang',
    'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Objective-C', 'Scala', 'R', 'MATLAB',
    'Shell', 'Bash', 'SQL', 'HTML', 'CSS', 'Sass', 'Less', 'Dart', 'Lua', 'Perl',
]

FRAMEWORKS = [
    'React', 'Vue.js', 'Vue', 'Angular', 'Next.js', 'Nuxt.js', 'Svelte', 'Node.js',
    'Express', 'Koa', 'Django', 'Flask', 'FastAPI', 'Tornado', 'Sanic',
    'Spring Boot', 'Spring', 'Spring MVC', 'MyBatis', 'Hibernate', 'JPA',
    'Django REST framework', 'DRF', 'Flutter', 'React Native', 'Uni-app',
    'Taro', 'Electron', 'jQuery', 'Bootstrap', 'Tailwind CSS', 'Ant Design',
    'Element UI', 'Vant',
]

DATABASES = [
    'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server',
    'Elasticsearch', 'Cassandra', 'SQLite', 'MariaDB', 'HBase', 'Neo4j',
    'InfluxDB', 'ClickHouse', 'DynamoDB',
]

TOOLS = [
    'Docker', 'Kubernetes', 'K8s', 'Jenkins', 'Git', 'GitLab', 'GitHub',
    'CI/CD', 'Nginx', 'Apache', 'Linux', 'Unix', 'Ubuntu', 'CentOS',
    'AWS', 'Azure', '阿里云', '腾讯云', '华为云', 'Google Cloud', 'GCP',
    'Jira', 'Confluence', 'Figma', 'Sketch', 'Postman', 'Swagger',
    'Webpack', 'Vite', 'Babel', 'Gulp', 'Grunt',
    'Jupyter', 'VS Code', 'PyCharm', 'IntelliJ', 'IDEA', 'Eclipse',
]

LANGUAGE_SKILLS = [
    '英语', '英语四级', '英语六级', 'CET-4', 'CET-6', 'CET4', 'CET6',
    '雅思', 'IELTS', '托福', 'TOEFL', 'GRE', 'GMAT',
    '日语', '日语一级', '日语二级', 'JLPT N1', 'JLPT N2',
    '韩语', '法语', '德语', '西班牙语', '俄语',
    '母语', '流利', '精通', '熟练', '读写能力', '听说能力',
]

CERTIFICATIONS = [
    'PMP', '软考', '系统架构设计师', '信息系统项目管理师',
    'AWS认证', 'AWS Certified', '阿里云认证', '腾讯云认证',
    '华为认证', 'HCIE', 'HCIP', 'HCIA',
    'OCP', 'OCJP', 'SCJP',
    'CPA', '注册会计师', '司法考试', '法律职业资格',
    '教师资格证', '建造师', '造价工程师',
    'CFA', 'FRM', 'ACCA',
]

SKILL_SECTION_KEYWORDS = [
    '技能', '专业技能', '技能特长', '个人技能', '技术栈',
    'skill', 'skills', 'technical skills', 'core competencies',
]


def extract_skills(text: str) -> Tuple[SkillCategory, List[str]]:
    """
    抽取技能
    返回: (技能分类对象, warnings列表)
    """
    warnings = []

    if not text:
        return SkillCategory(), warnings

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    skill_section_text = _extract_skill_section(lines)
    if not skill_section_text:
        skill_section_text = text

    word_freq = _count_word_frequency(text)

    skill_category = SkillCategory()

    skill_category.programming_languages = _match_skills(
        skill_section_text, PROGRAMMING_LANGUAGES, word_freq
    )
    skill_category.frameworks = _match_skills(
        skill_section_text, FRAMEWORKS, word_freq
    )
    skill_category.databases = _match_skills(
        skill_section_text, DATABASES, word_freq
    )
    skill_category.tools = _match_skills(
        skill_section_text, TOOLS, word_freq
    )
    skill_category.languages = _match_skills(
        skill_section_text, LANGUAGE_SKILLS, word_freq
    )
    skill_category.certifications = _match_skills(
        skill_section_text, CERTIFICATIONS, word_freq
    )

    total_skills = (
        len(skill_category.programming_languages) +
        len(skill_category.frameworks) +
        len(skill_category.databases) +
        len(skill_category.tools)
    )
    if total_skills == 0:
        warnings.append("未抽取到有效技能")

    return skill_category, warnings


def _extract_skill_section(lines: List[str]) -> str:
    section_lines = []
    in_section = False
    section_start_idx = -1

    for i, line in enumerate(lines):
        lower_line = line.lower().strip()
        is_section_header = any(kw.lower() in lower_line for kw in SKILL_SECTION_KEYWORDS) and len(line) < 20

        if is_section_header and not in_section:
            in_section = True
            section_start_idx = i
            continue

        if in_section and is_section_header and i > section_start_idx + 1:
            break

        if in_section:
            section_lines.append(line)

    return '\n'.join(section_lines)


def _count_word_frequency(text: str) -> Dict[str, int]:
    words = re.findall(r'[A-Za-z][A-Za-z0-9+\-#.]*|[\u4e00-\u9fa5]+', text)
    freq = Counter()
    for word in words:
        if len(word) >= 2:
            freq[word.lower()] += 1
    return freq


def _match_skills(text: str, skill_list: List[str], word_freq: Dict[str, int]) -> List[SkillItem]:
    skills = []
    lower_text = text.lower()
    seen = set()

    for skill in skill_list:
        skill_lower = skill.lower()
        if skill_lower in seen:
            continue

        if skill_lower in lower_text:
            confidence = _calculate_confidence(skill, word_freq, text)
            skills.append(SkillItem(name=skill, confidence=confidence))
            seen.add(skill_lower)

    skills.sort(key=lambda s: s.confidence, reverse=True)
    return skills


def _calculate_confidence(skill: str, word_freq: Dict[str, int], text: str) -> float:
    skill_lower = skill.lower()

    count = 0
    for word, freq in word_freq.items():
        if skill_lower in word or word in skill_lower:
            count += freq

    if count >= 5:
        base_conf = 0.95
    elif count >= 3:
        base_conf = 0.85
    elif count >= 2:
        base_conf = 0.75
    else:
        base_conf = 0.6

    lines = text.split('\n')
    in_skill_section = False
    for line in lines:
        if any(kw in line for kw in ['技能', '技术', 'skill']):
            in_skill_section = True
            continue
        if in_skill_section and skill_lower in line.lower():
            base_conf = min(base_conf + 0.1, 1.0)
            break

    return round(base_conf, 2)
