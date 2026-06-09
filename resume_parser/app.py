import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List

from .config import get_settings
from .schemas import (
    ResumeParseResult,
    BatchParseResponse,
    ParseStats,
    HealthCheckResponse,
)
from .pipeline import parse_resume_file
from .cache import get_cache
from .stats import get_stats_collector
from .batch import get_batch_processor
from .data.schools import get_school_library
from .data.companies import get_company_library
from .data.majors import get_major_library

logger = logging.getLogger(__name__)

app = FastAPI(
    title="简历解析服务",
    description="支持 PDF/Word/图片 三种格式的简历结构化解析服务",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """启动时预加载数据"""
    settings = get_settings()
    logger.info(f"Starting resume parser service on port {settings.port}")

    logger.info("Pre-loading school library...")
    school_dict, alias_map, school_names = get_school_library()
    logger.info(f"School library loaded: {len(school_names)} schools, {len(alias_map)} aliases")

    logger.info("Pre-loading company library...")
    company_lib = get_company_library()
    logger.info(f"Company library loaded: {len(company_lib)} entries")

    logger.info("Pre-loading major library...")
    major_lib = get_major_library()
    logger.info(f"Major library loaded: {len(major_lib)} entries")

    cache = get_cache()
    logger.info(f"Cache initialized (max_size: {cache.max_size})")

    logger.info(f"Service started successfully, listening on port {settings.port}")


@app.get("/health", response_model=HealthCheckResponse, tags=["系统"])
async def health_check():
    """健康检查接口"""
    cache = get_cache()
    return HealthCheckResponse(
        status="ok",
        cache_size=cache.size(),
        cache_max_size=cache.max_size,
    )


@app.post("/api/v1/parse", response_model=ResumeParseResult, tags=["解析"])
async def parse_resume(file: UploadFile = File(...)):
    """
    单文件简历解析接口

    - **file**: 简历文件，支持 PDF、Word (.docx)、图片格式
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise HTTPException(status_code=400, detail="文件读取失败")

    if not content:
        raise HTTPException(status_code=400, detail="文件内容为空")

    try:
        result = parse_resume_file(content, file.filename)
        return result
    except Exception as e:
        logger.error(f"Parse failed for {file.filename}: {e}", exc_info=True)
        return JSONResponse(
            status_code=200,
            content=ResumeParseResult(
                file_hash="",
                warnings=[f"解析失败: {str(e)}"],
            ).model_dump()
        )


@app.post("/api/v1/batch/parse", response_model=BatchParseResponse, tags=["批量解析"])
async def batch_parse(files: List[UploadFile] = File(...)):
    """
    批量简历解析接口（同步处理，返回进度）

    - **files**: 多个简历文件，最多 50 份
    """
    settings = get_settings()

    if len(files) > settings.max_batch_size:
        raise HTTPException(
            status_code=400,
            detail=f"批量解析文件数不能超过 {settings.max_batch_size} 份"
        )

    if not files:
        raise HTTPException(status_code=400, detail="请至少上传一个文件")

    file_data = []
    for file in files:
        content = await file.read()
        file_data.append((file.filename or "unknown", content))

    try:
        batch_processor = get_batch_processor()
        batch_id = batch_processor.create_batch(file_data)

        status_result = batch_processor.get_batch_status(batch_id)
        if status_result is None:
            raise HTTPException(status_code=500, detail="批量任务创建失败")

        return status_result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch parse failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="批量解析服务异常")


@app.get("/api/v1/batch/{batch_id}", response_model=BatchParseResponse, tags=["批量解析"])
async def get_batch_status(batch_id: str):
    """
    查询批量解析进度

    - **batch_id**: 批量任务 ID
    """
    batch_processor = get_batch_processor()
    result = batch_processor.get_batch_status(batch_id)

    if result is None:
        raise HTTPException(status_code=404, detail="批量任务不存在或已过期")

    return result


@app.get("/api/v1/stats", response_model=ParseStats, tags=["统计"])
async def get_statistics():
    """获取解析统计数据"""
    stats_collector = get_stats_collector()
    return stats_collector.get_stats()


@app.post("/api/v1/cache/clear", tags=["系统"])
async def clear_cache():
    """清空缓存"""
    cache = get_cache()
    size_before = cache.size()
    cache.clear()
    return {"message": f"缓存已清空，清除了 {size_before} 条记录"}


@app.get("/api/v1/cache/size", tags=["系统"])
async def get_cache_size():
    """获取缓存大小"""
    cache = get_cache()
    return {"size": cache.size(), "max_size": cache.max_size}
