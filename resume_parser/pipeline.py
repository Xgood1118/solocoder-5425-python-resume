import logging
import time
from typing import Tuple, List
from .parser.factory import factory as parser_factory
from .extractors.name_extractor import extract_name
from .extractors.contact_extractor import extract_contact
from .extractors.education_extractor import extract_education
from .extractors.work_extractor import extract_work_experience
from .extractors.project_extractor import extract_project_experience
from .extractors.skill_extractor import extract_skills
from .enhance.enhancer import enhance_result
from .cache import compute_file_hash, get_cache
from .stats import get_stats_collector
from .schemas import (
    ResumeParseResult,
    NameInfo,
    ContactInfo,
    SkillCategory,
)

logger = logging.getLogger(__name__)


def parse_resume_file(file_content: bytes, filename: str) -> ResumeParseResult:
    """
    完整的简历解析流程：
    1. 计算 SHA-256 哈希
    2. 查缓存，命中则直接返回
    3. 按文件类型解析（PDF/Word/OCR）
    4. 字段抽取（并行/顺序）
    5. 归一化
    6. 增强
    7. 写缓存
    8. 返回结果
    """
    start_time = time.time()

    file_hash = compute_file_hash(file_content)
    cache = get_cache()

    cached = cache.get(file_hash)
    if cached:
        logger.info(f"Cache hit for file: {filename} (hash: {file_hash[:16]}...)")
        return cached

    warnings: List[str] = []
    result = ResumeParseResult(file_hash=file_hash)

    try:
        raw_text, parse_meta = parser_factory.parse_file(file_content, filename)
        result.raw_text_length = len(raw_text)
        result.parse_method = parse_meta.get("parse_method", "unknown")

        if not raw_text:
            if parse_meta.get("is_scanned") or parse_meta.get("parse_method") == "scanned_pdf_ocr_failed":
                warnings.append("扫描版 PDF 或图片简历识别失败，文本内容为空")
                logger.warning(f"Scanned document OCR failed: {filename}")
            else:
                warnings.append("未能从文件中提取到文本内容")

        ocr_confidence = parse_meta.get("confidence", 1.0)

        try:
            chinese_name, english_name, name_conf = extract_name(raw_text, ocr_confidence)
            if chinese_name or english_name:
                result.name = NameInfo(
                    chinese_name=chinese_name,
                    english_name=english_name,
                    confidence=name_conf,
                )
        except Exception as e:
            logger.error(f"Name extraction failed: {e}")
            warnings.append(f"姓名抽取失败: {str(e)}")

        try:
            phone, phone_conf, email, email_conf, contact_warns = extract_contact(raw_text)
            if phone or email:
                result.contact = ContactInfo(
                    phone=phone,
                    phone_confidence=phone_conf,
                    email=email,
                    email_confidence=email_conf,
                )
            warnings.extend(contact_warns)
        except Exception as e:
            logger.error(f"Contact extraction failed: {e}")
            warnings.append(f"联系方式抽取失败: {str(e)}")

        try:
            education_list, edu_warns = extract_education(raw_text)
            result.education = education_list
            warnings.extend(edu_warns)
        except Exception as e:
            logger.error(f"Education extraction failed: {e}")
            warnings.append(f"教育经历抽取失败: {str(e)}")

        try:
            work_list, work_warns = extract_work_experience(raw_text)
            result.work_experience = work_list
            warnings.extend(work_warns)
        except Exception as e:
            logger.error(f"Work experience extraction failed: {e}")
            warnings.append(f"工作经历抽取失败: {str(e)}")

        try:
            project_list, proj_warns = extract_project_experience(raw_text)
            result.project_experience = project_list
            warnings.extend(proj_warns)
        except Exception as e:
            logger.error(f"Project experience extraction failed: {e}")
            warnings.append(f"项目经历抽取失败: {str(e)}")

        try:
            skills, skill_warns = extract_skills(raw_text)
            result.skills = skills
            warnings.extend(skill_warns)
        except Exception as e:
            logger.error(f"Skills extraction failed: {e}")
            warnings.append(f"技能抽取失败: {str(e)}")

        try:
            enhance_result(result)
        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            warnings.append(f"信息增强失败: {str(e)}")

    except Exception as e:
        logger.error(f"Parse pipeline failed: {e}", exc_info=True)
        warnings.append(f"解析流程异常: {str(e)}")

    result.warnings = warnings

    duration = time.time() - start_time
    result_dict = result.model_dump()
    cache.set(file_hash, result_dict)

    stats = get_stats_collector()
    file_type = _get_file_type(filename)
    stats.record_request(file_type, duration, result)

    logger.info(
        f"Resume parsed: {filename} | "
        f"type: {file_type} | "
        f"duration: {duration:.3f}s | "
        f"text_len: {result.raw_text_length} | "
        f"warnings: {len(warnings)}"
    )

    return result


def _get_file_type(filename: str) -> str:
    if filename.lower().endswith('.pdf'):
        return 'pdf'
    elif filename.lower().endswith(('.docx', '.doc')):
        return 'word'
    elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp')):
        return 'image'
    else:
        return 'unknown'
