import logging
from typing import Tuple, Optional, List
from ..normalize.phone import find_phones
from ..normalize.email import find_emails

logger = logging.getLogger(__name__)


def extract_contact(text: str) -> Tuple[Optional[str], float, Optional[str], float, List[str]]:
    """
    抽取联系方式（手机、邮箱）
    返回: (手机号, 手机置信度, 邮箱, 邮箱置信度, warnings列表)
    """
    warnings = []
    phone = None
    phone_conf = 0.0
    email = None
    email_conf = 0.0

    if not text:
        return None, 0.0, None, 0.0, warnings

    phones = find_phones(text)
    if phones:
        phones.sort(key=lambda x: x[1], reverse=True)
        phone = phones[0][0]
        phone_conf = phones[0][1]
        if len(phones) > 1:
            warnings.append(f"找到多个手机号，返回置信度最高的: {phone}")

    emails = find_emails(text)
    if emails:
        emails.sort(key=lambda x: x[1], reverse=True)
        email = emails[0][0]
        email_conf = emails[0][1]

    return phone, phone_conf, email, email_conf, warnings
