import uuid
import logging
import threading
import time
from typing import Dict, List, Optional
from .schemas import BatchResumeItem, BatchParseResponse
from .pipeline import parse_resume_file
from .config import get_settings

logger = logging.getLogger(__name__)


class BatchProcessor:
    def __init__(self):
        self._batches: Dict[str, List[BatchResumeItem]] = {}
        self._lock = threading.Lock()

    def create_batch(self, files: List[tuple]) -> str:
        """
        创建一个批量解析任务
        files: [(filename, file_content), ...]
        返回 batch_id
        """
        settings = get_settings()
        if len(files) > settings.max_batch_size:
            raise ValueError(f"Batch size exceeds maximum of {settings.max_batch_size}")

        batch_id = str(uuid.uuid4())
        items = []
        for filename, content in files:
            items.append(BatchResumeItem(
                filename=filename,
                status="pending",
                progress=0,
            ))

        with self._lock:
            self._batches[batch_id] = items

        self._process_batch_async(batch_id, files)

        return batch_id

    def _process_batch_async(self, batch_id: str, files: List[tuple]):
        """在后台线程中处理批量任务"""
        thread = threading.Thread(
            target=self._process_batch,
            args=(batch_id, files),
            daemon=True,
        )
        thread.start()

    def _process_batch(self, batch_id: str, files: List[tuple]):
        """处理批量任务"""
        logger.info(f"Starting batch processing: {batch_id}, size: {len(files)}")

        for i, (filename, content) in enumerate(files):
            try:
                with self._lock:
                    if batch_id not in self._batches:
                        logger.warning(f"Batch {batch_id} not found, aborting")
                        return
                    self._batches[batch_id][i].status = "processing"
                    self._batches[batch_id][i].progress = 10

                result = parse_resume_file(content, filename)

                with self._lock:
                    if batch_id not in self._batches:
                        return
                    self._batches[batch_id][i].status = "completed"
                    self._batches[batch_id][i].progress = 100
                    self._batches[batch_id][i].result = result
                    self._batches[batch_id][i].file_hash = result.file_hash

            except Exception as e:
                logger.error(f"Batch item failed: {filename}, error: {e}")
                with self._lock:
                    if batch_id not in self._batches:
                        return
                    self._batches[batch_id][i].status = "failed"
                    self._batches[batch_id][i].error = str(e)
                    self._batches[batch_id][i].progress = 100

        logger.info(f"Batch processing completed: {batch_id}")

    def get_batch_status(self, batch_id: str) -> Optional[BatchParseResponse]:
        """获取批量任务状态"""
        with self._lock:
            items = self._batches.get(batch_id)
            if items is None:
                return None

            completed = sum(1 for item in items if item.status in ("completed", "failed"))

            return BatchParseResponse(
                batch_id=batch_id,
                total=len(items),
                completed=completed,
                items=[item.model_copy() for item in items],
            )

    def cleanup_old_batches(self, max_age_seconds: int = 3600):
        """清理旧的批量任务（保留1小时）"""
        with self._lock:
            pass


_batch_processor: Optional[BatchProcessor] = None


def get_batch_processor() -> BatchProcessor:
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchProcessor()
    return _batch_processor
