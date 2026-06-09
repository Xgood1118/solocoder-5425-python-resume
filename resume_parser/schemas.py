from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SkillItem(BaseModel):
    name: str
    confidence: float = 0.0


class SkillCategory(BaseModel):
    programming_languages: List[SkillItem] = Field(default_factory=list)
    frameworks: List[SkillItem] = Field(default_factory=list)
    databases: List[SkillItem] = Field(default_factory=list)
    tools: List[SkillItem] = Field(default_factory=list)
    languages: List[SkillItem] = Field(default_factory=list)
    certifications: List[SkillItem] = Field(default_factory=list)


class Education(BaseModel):
    school: Optional[str] = None
    school_standard: Optional[str] = None
    school_tags: List[str] = Field(default_factory=list)
    major: Optional[str] = None
    major_standard: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    degree: Optional[str] = None
    confidence: float = 0.0


class WorkExperience(BaseModel):
    company: Optional[str] = None
    company_standard: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    is_current: bool = False


class ProjectExperience(BaseModel):
    project_name: Optional[str] = None
    company: Optional[str] = None
    company_standard: Optional[str] = None
    role: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    responsibilities: Optional[str] = None


class NameInfo(BaseModel):
    chinese_name: Optional[str] = None
    english_name: Optional[str] = None
    confidence: float = 0.0


class ContactInfo(BaseModel):
    phone: Optional[str] = None
    phone_confidence: float = 0.0
    email: Optional[str] = None
    email_confidence: float = 0.0


class EnhancedInfo(BaseModel):
    age_range: Optional[str] = None
    total_years_of_experience: Optional[float] = None
    school_level: Optional[str] = None
    is_top_school: bool = False
    qs_rank: Optional[int] = None


class ResumeParseResult(BaseModel):
    file_hash: str
    name: Optional[NameInfo] = None
    contact: Optional[ContactInfo] = None
    education: List[Education] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    project_experience: List[ProjectExperience] = Field(default_factory=list)
    skills: Optional[SkillCategory] = None
    enhanced: Optional[EnhancedInfo] = None
    warnings: List[str] = Field(default_factory=list)
    parse_method: Optional[str] = None
    raw_text_length: int = 0


class BatchResumeItem(BaseModel):
    filename: str
    file_hash: Optional[str] = None
    status: str = "pending"
    progress: int = 0
    result: Optional[ResumeParseResult] = None
    error: Optional[str] = None


class BatchParseResponse(BaseModel):
    batch_id: str
    total: int
    completed: int = 0
    items: List[BatchResumeItem] = Field(default_factory=list)


class ParseStats(BaseModel):
    total_requests: int = 0
    successful_requests: int = 0
    success_rate: float = 0.0
    avg_parse_time_by_type: Dict[str, float] = Field(default_factory=dict)
    total_parse_time_by_type: Dict[str, float] = Field(default_factory=dict)
    parse_count_by_type: Dict[str, int] = Field(default_factory=dict)
    field_accuracy: Dict[str, float] = Field(default_factory=dict)


class HealthCheckResponse(BaseModel):
    status: str = "ok"
    cache_size: int = 0
    cache_max_size: int = 0
