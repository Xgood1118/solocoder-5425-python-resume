import logging
import time
from typing import Dict, Optional
from collections import defaultdict
from .schemas import ParseStats, ResumeParseResult

logger = logging.getLogger(__name__)


class StatsCollector:
    def __init__(self):
        self.total_requests: int = 0
        self.successful_requests: int = 0
        self.total_parse_time_by_type: Dict[str, float] = defaultdict(float)
        self.parse_count_by_type: Dict[str, int] = defaultdict(int)
        self.field_extraction_count: Dict[str, int] = defaultdict(int)
        self.field_ground_truth_count: Dict[str, int] = defaultdict(int)

    def record_request(self, file_type: str, duration: float, result: ResumeParseResult):
        """记录一次解析请求"""
        self.total_requests += 1
        self.total_parse_time_by_type[file_type] += duration
        self.parse_count_by_type[file_type] += 1

        core_fields = 0
        if result.name and result.name.chinese_name:
            core_fields += 1
        if result.contact and result.contact.phone:
            core_fields += 1
        if result.contact and result.contact.email:
            core_fields += 1
        if result.education:
            core_fields += 1
        if result.work_experience:
            core_fields += 1
        if result.skills:
            core_fields += 1

        if core_fields >= 5:
            self.successful_requests += 1

    def record_field_accuracy(self, field_name: str, extracted: bool, ground_truth: bool):
        """记录字段抽取准确率（人工标注数据）"""
        if ground_truth:
            self.field_ground_truth_count[field_name] += 1
        if extracted and ground_truth:
            self.field_extraction_count[field_name] += 1

    def get_stats(self) -> ParseStats:
        """获取统计数据"""
        success_rate = (
            self.successful_requests / self.total_requests
            if self.total_requests > 0 else 0.0
        )

        avg_parse_time = {}
        for file_type, count in self.parse_count_by_type.items():
            if count > 0:
                avg_parse_time[file_type] = round(
                    self.total_parse_time_by_type[file_type] / count, 3
                )

        total_parse_time = {
            k: round(v, 3) for k, v in self.total_parse_time_by_type.items()
        }

        field_accuracy = {}
        for field_name, gt_count in self.field_ground_truth_count.items():
            if gt_count > 0:
                field_accuracy[field_name] = round(
                    self.field_extraction_count.get(field_name, 0) / gt_count, 3
                )

        return ParseStats(
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            success_rate=round(success_rate, 3),
            avg_parse_time_by_type=avg_parse_time,
            total_parse_time_by_type=total_parse_time,
            parse_count_by_type=dict(self.parse_count_by_type),
            field_accuracy=field_accuracy,
        )

    def reset(self):
        """重置统计数据"""
        self.total_requests = 0
        self.successful_requests = 0
        self.total_parse_time_by_type.clear()
        self.parse_count_by_type.clear()
        self.field_extraction_count.clear()
        self.field_ground_truth_count.clear()


_stats_instance: Optional[StatsCollector] = None


def get_stats_collector() -> StatsCollector:
    """获取全局统计单例"""
    global _stats_instance
    if _stats_instance is None:
        _stats_instance = StatsCollector()
    return _stats_instance
