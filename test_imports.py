import sys
sys.path.insert(0, r'c:\Users\白东鑫\work01\SoloCoder\5425-python-resume')

print("=" * 60)
print("Testing resume parser modules...")
print("=" * 60)

from resume_parser.config import get_settings
settings = get_settings()
print(f"[OK] Config: port={settings.port}, cache_max_size={settings.cache_max_size}")

from resume_parser.schemas import ResumeParseResult, NameInfo, ContactInfo
print("[OK] Schemas loaded")

from resume_parser.data.schools import get_school_library
school_dict, alias_map, school_names = get_school_library()
print(f"[OK] School library: {len(school_names)} schools, {len(alias_map)} aliases")

from resume_parser.data.companies import get_company_library
company_lib = get_company_library()
print(f"[OK] Company library: {len(company_lib)} entries")

from resume_parser.data.majors import get_major_library
major_lib = get_major_library()
print(f"[OK] Major library: {len(major_lib)} entries")

from resume_parser.cache import LRUCache, compute_file_hash
cache = LRUCache(max_size=10)
cache.set('test', {'value': 1})
val = cache.get('test')
h = compute_file_hash(b'hello world')
print(f"[OK] Cache: get={val}, hash={h[:16]}...")

from resume_parser.normalize.phone import normalize_phone
phone, conf, warns = normalize_phone('+86 138-1234-5678')
print(f"[OK] Phone normalize: {phone} (conf={conf})")

from resume_parser.normalize.email import normalize_email
email, conf = normalize_email('Test@Example.com')
print(f"[OK] Email normalize: {email} (conf={conf})")

from resume_parser.normalize.school import normalize_school
school, tags, aliases, conf = normalize_school('清华')
print(f"[OK] School normalize: {school}, tags={tags}, conf={conf}")

from resume_parser.normalize.company import normalize_company
company, conf, comp_warns = normalize_company('百度')
print(f"[OK] Company normalize: {company} (conf={conf})")

from resume_parser.normalize.major import normalize_major
major, conf, major_warns = normalize_major('计算机科学与技术')
print(f"[OK] Major normalize: {major} (conf={conf})")

from resume_parser.extractors.name_extractor import extract_name
name_text = "张三 (Zhang San)\n手机: 13812345678\n邮箱: test@example.com"
cn_name, en_name, conf = extract_name(name_text)
print(f"[OK] Name extract: cn={cn_name}, en={en_name}, conf={conf}")

from resume_parser.extractors.contact_extractor import extract_contact
phone, phone_conf, email, email_conf, warns = extract_contact(name_text)
print(f"[OK] Contact extract: phone={phone}, email={email}")

from resume_parser.stats import StatsCollector
stats = StatsCollector()
print("[OK] Stats collector created")

from resume_parser.search.engine import InMemorySearch
search = InMemorySearch()
print("[OK] Search engine created")

print("=" * 60)
print("All core modules loaded successfully!")
print("=" * 60)
