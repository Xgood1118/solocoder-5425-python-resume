import sys
sys.path.insert(0, r'c:\Users\白东鑫\work01\SoloCoder\5425-python-resume')

print("=" * 60)
print("问题诊断：专业抽取与公司名匹配")
print("=" * 60)

print("\n【问题1：专业抽取把学校名当成专业】")
print("-" * 60)

from resume_parser.extractors.education_extractor import _extract_major, _extract_school_name

test_cases = [
    "2018.09 - 2022.06  清华大学  计算机科学与技术  本科",
    "北京大学  软件工程专业  硕士",
    "浙江大学  信息工程  本科",
    "复旦大学经济学学士",
    "上海交通大学 机械工程",
]

for tc in test_cases:
    school = _extract_school_name(tc)
    major = _extract_major(tc)
    print(f"  原文: {tc}")
    print(f"    -> 学校: {school}")
    print(f"    -> 专业: {major}")
    print()

print("\n【问题2：公司名模糊匹配过于宽松】")
print("-" * 60)

from resume_parser.normalize.company import normalize_company

test_companies = [
    "字节跳动",
    "北京字节跳动科技有限公司",
    "百度在线网络技术有限公司",
    "联想",
    "小米科技",
    "腾讯科技（深圳）有限公司",
    "美团点评",
    "滴滴出行",
    "京东集团",
    "网易公司",
    "阿里巴巴集团",
    "华为技术有限公司",
    "蚂蚁科技集团股份有限公司",
]

for tc in test_companies:
    std, conf, warns = normalize_company(tc)
    status = "✓ 匹配正确" if tc.startswith(std) or std.startswith(tc[:2]) else "✗ 可能错配"
    print(f"  {tc} -> {std} (置信度: {conf:.2f}) {status}")
    if warns:
        for w in warns:
            print(f"      警告: {w}")
    print()

print("\n【问题3：公司名抽取正则是否准确】")
print("-" * 60)

from resume_parser.extractors.work_extractor import _extract_company

test_work_texts = [
    "2022.07 - 至今  字节跳动  后端开发工程师",
    "2020.07 - 2022.06  百度在线网络技术有限公司  研发工程师",
    "腾讯科技 产品经理 2019 - 至今",
    "在阿里巴巴集团担任前端开发",
    "美团点评 - 运营专员 - 2021年至今",
    "华为技术有限公司  西安研究所  软件工程师",
]

for tc in test_work_texts:
    company = _extract_company(tc)
    print(f"  原文: {tc}")
    print(f"    -> 抽取的公司: {company}")
    print()

print("诊断完成！")
