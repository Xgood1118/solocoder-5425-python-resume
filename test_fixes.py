import sys
sys.path.insert(0, r'c:\Users\白东鑫\work01\SoloCoder\5425-python-resume')

from resume_parser.data.schools import get_school_library
get_school_library.cache_clear()

print("=" * 60)
print("Phone normalization tests:")
print("=" * 60)
from resume_parser.normalize.phone import normalize_phone

test_cases = [
    '+86 138-1234-5678',
    '13812345678',
    '138-1234-5678',
    '010-12345678-123',
    '8613999999999',
    '1234567890123',
]
for tc in test_cases:
    phone, conf, warns = normalize_phone(tc)
    print(f"  {tc!r} -> {phone} (conf={conf}, warnings={warns})")

print()
print("=" * 60)
print("School normalization tests:")
print("=" * 60)
from resume_parser.normalize.school import normalize_school

test_schools = ['清华', '北京大学', 'MIT', '斯坦福', '复旦大学']
for ts in test_schools:
    school, tags, aliases, conf = normalize_school(ts)
    print(f"  {ts!r} -> {school}, tags={tags}, conf={conf}")

print()
print("=" * 60)
print("School library info:")
print("=" * 60)
school_dict, alias_map, school_names = get_school_library()
print(f"Total schools: {len(school_names)}")
print(f"Total aliases: {len(alias_map)}")
print(f"'清华' maps to: {alias_map.get('清华')}")
print(f"'Tsinghua' maps to: {alias_map.get('Tsinghua')}")
print(f"清华大学 tags: {school_dict.get('清华大学', {}).get('tags')}")
print(f"清华大学 qs_rank: {school_dict.get('清华大学', {}).get('qs_rank')}")

print()
print("All tests completed!")
