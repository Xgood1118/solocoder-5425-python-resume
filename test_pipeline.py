import sys
sys.path.insert(0, r'c:\Users\白东鑫\work01\SoloCoder\5425-python-resume')

from resume_parser.pipeline import parse_resume_file

sample_resume = """
张三 (Zhang San)
手机: +86 138-1234-5678
邮箱: zhangsan@example.com

教育背景
2018.09 - 2022.06  清华大学  计算机科学与技术  本科
2015.09 - 2018.06  北京市第四中学  高中

工作经历
2022.07 - 至今  字节跳动  后端开发工程师
- 负责核心业务系统的设计与开发
- 使用 Python、Go 等编程语言
- 技术栈：FastAPI、Redis、MySQL、Docker

2020.07 - 2020.09  百度  研发实习生
- 参与搜索引擎优化项目

项目经历
电商推荐系统
项目时间：2021.03 - 2022.06
角色：核心开发
技术栈：Python、TensorFlow、Redis、MySQL
描述：基于深度学习的电商商品推荐系统
责任：负责召回算法设计与实现

专业技能
编程语言：Python, Java, Go, JavaScript
框架：Django, FastAPI, React, Vue.js
数据库：MySQL, PostgreSQL, Redis, MongoDB
工具：Docker, Kubernetes, Git, Jenkins
语言能力：英语六级
证书：AWS认证解决方案架构师
"""

print("Testing resume parsing pipeline...")
print("=" * 60)

result = parse_resume_file(sample_resume.encode('utf-8'), 'test_resume.txt')

print(f"File hash: {result.file_hash[:16]}...")
print(f"Parse method: {result.parse_method}")
print(f"Raw text length: {result.raw_text_length}")
print()

print("Name:")
if result.name:
    print(f"  Chinese: {result.name.chinese_name}")
    print(f"  English: {result.name.english_name}")
    print(f"  Confidence: {result.name.confidence}")
print()

print("Contact:")
if result.contact:
    print(f"  Phone: {result.contact.phone} (conf={result.contact.phone_confidence})")
    print(f"  Email: {result.contact.email} (conf={result.contact.email_confidence})")
print()

print(f"Education: {len(result.education)} entries")
for edu in result.education:
    print(f"  - {edu.school} | {edu.major} | {edu.degree}")
    print(f"    Standard: {edu.school_standard}")
    print(f"    Tags: {edu.school_tags}")
    print(f"    Period: {edu.start_date} - {edu.end_date}")
print()

print(f"Work experience: {len(result.work_experience)} entries")
for work in result.work_experience:
    print(f"  - {work.company} | {work.position}")
    print(f"    Standard: {work.company_standard}")
    print(f"    Period: {work.start_date} - {work.end_date}")
print()

print(f"Project experience: {len(result.project_experience)} entries")
for proj in result.project_experience:
    print(f"  - {proj.project_name} | {proj.role}")
    print(f"    Tech: {proj.tech_stack}")
print()

print("Skills:")
if result.skills:
    print(f"  Programming: {[s.name for s in result.skills.programming_languages[:5]]}")
    print(f"  Frameworks: {[s.name for s in result.skills.frameworks[:5]]}")
    print(f"  Databases: {[s.name for s in result.skills.databases[:5]]}")
    print(f"  Tools: {[s.name for s in result.skills.tools[:5]]}")
    print(f"  Languages: {[s.name for s in result.skills.languages[:5]]}")
    print(f"  Certifications: {[s.name for s in result.skills.certifications[:5]]}")
print()

print("Enhanced info:")
if result.enhanced:
    print(f"  School level: {result.enhanced.school_level}")
    print(f"  Is top school: {result.enhanced.is_top_school}")
    print(f"  QS rank: {result.enhanced.qs_rank}")
    print(f"  Age range: {result.enhanced.age_range}")
    print(f"  Total years of experience: {result.enhanced.total_years_of_experience}")
print()

print(f"Warnings ({len(result.warnings)}):")
for w in result.warnings:
    print(f"  - {w}")

print()
print("=" * 60)
print("Pipeline test completed!")
