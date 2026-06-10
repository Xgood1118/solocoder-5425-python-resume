import re

print("【新 DATE_PATTERN 测试】")
print()

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

test_cases = [
    '2022.07 - 至今',
    '2021年至今',
    '2020 - 2022',
    '2019.01-2021.06',
    '2018/05 - 2020/03',
    '2017年 - 2019年',
    '2016到现在',
]

for tc in test_cases:
    m = DATE_PATTERN.search(tc)
    if m:
        print(f"  ✓ {tc}")
        print(f"    匹配: {m.group()} (位置: {m.start()}-{m.end()})")
        print(f"    group(1)={m.group(1)}, group(2)={m.group(2)}")
    else:
        print(f"  ✗ {tc} -> 未匹配")
    print()
