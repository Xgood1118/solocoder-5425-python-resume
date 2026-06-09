#!/usr/bin/env python
"""
简历解析服务启动脚本
端口从环境变量 PORT 读取，默认 8080
"""
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from resume_parser.config import get_settings
from resume_parser.logging_config import setup_logging


def main():
    settings = get_settings()

    setup_logging("INFO")

    port = settings.port

    print(f"=" * 60)
    print(f"  简历解析服务 Resume Parser Service")
    print(f"=" * 60)
    print(f"  监听端口: {port}")
    print(f"  缓存容量: {settings.cache_max_size}")
    print(f"  OCR 置信度阈值: {settings.ocr_confidence_threshold}%")
    print(f"  批量最大文件数: {settings.max_batch_size}")
    print(f"  API 文档: http://localhost:{port}/docs")
    print(f"  健康检查: http://localhost:{port}/health")
    print(f"=" * 60)

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Resume Parser Service starting on port {port}")

    uvicorn.run(
        "resume_parser.app:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False,
        access_log=True,
    )


if __name__ == "__main__":
    main()
