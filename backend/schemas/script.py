from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from backend.models.script import ScriptStatus, ScriptType


class ScriptBase(BaseModel):
    """剧本基础模式"""
    title: str = Field(..., min_length=1, max_length=200, description="剧本标题")
    description: Optional[str] = Field(None, description="剧本描述")
    script_type: ScriptType = Field(default=ScriptType.SHORT_DRAMA, description="剧本类型")
    episode_number: int = Field(default=1, ge=1, description="集数")
    total_episodes: int = Field(default=1, ge=1, description="总集数")
    target_duration: int = Field(default=60, ge=1, le=600, description="目标时长（秒）")
    characters: Optional[List[Dict[str, Any]]] = Field(None, description="角色列表")
    settings: Optional[List[Dict[str, Any]]] = Field(None, description="场景设置")
    tone: Optional[str] = Field(None, description="语气风格")
    style: Optional[str] = Field(None, description="视觉风格")
    language: str = Field(default="zh", description="语言")


class ScriptCreateRequest(ScriptBase):
    """剧本创建请求"""
    project_id: int = Field(..., ge=1, description="项目ID")
    content: Optional[str] = Field(None, description="剧本内容")
    structured_content: Optional[Dict[str, Any]] = Field(None, description="结构化内容")


class ScriptGenerateRequest(BaseModel):
    """剧本生成请求"""
    project_id: int = Field(..., ge=1, description="项目ID")
    prompt: str = Field(..., min_length=10, max_length=2000, description="生成提示词")
    script_type: Optional[ScriptType] = Field(None, description="剧本类型")
    episode_number: Optional[int] = Field(None, ge=1, description="集数")
    total_episodes: Optional[int] = Field(None, ge=1, description="总集数")
    target_duration: Optional[int] = Field(None, ge=1, le=600, description="目标时长（秒）")
    characters: Optional[List[Dict[str, Any]]] = Field(None, description="角色列表")
    settings: Optional[List[Dict[str, Any]]] = Field(None, description="场景设置")
    tone: Optional[str] = Field(None, description="语气风格")
    style: Optional[str] = Field(None, description="视觉风格")
    language: Optional[str] = Field(None, description="语言")


class ScriptUpdateRequest(BaseModel):
    """剧本更新请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="剧本标题")
    content: Optional[str] = Field(None, description="剧本内容")
    structured_content: Optional[Dict[str, Any]] = Field(None, description="结构化内容")
    
    @validator("title")
    def validate_title(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Title cannot be empty")
        return v


class ScriptResponse(ScriptBase):
    """剧本响应模式"""
    id: int
    project_id: Optional[int]
    status: ScriptStatus
    content: Optional[str]
    structured_content: Optional[Dict[str, Any]]
    prompt: Optional[str]
    llm_model: Optional[str]
    llm_config: Optional[Dict[str, Any]]
    estimated_duration: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    generated_at: Optional[datetime]
    approved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ScriptListResponse(BaseModel):
    """剧本列表响应"""
    scripts: List[ScriptResponse]
    total: int
    skip: int
    limit: int


class ScriptRevisionCreateRequest(BaseModel):
    """剧本修订创建请求"""
    content: str = Field(..., description="修订内容")
    structured_content: Dict[str, Any] = Field(..., description="结构化内容")
    changes: str = Field(..., min_length=1, max_length=1000, description="变更说明")
    feedback: Optional[str] = Field(None, description="反馈意见")


class ScriptRevisionResponse(BaseModel):
    """剧本修订响应"""
    id: int
    script_id: int
    revision_number: int
    content: str
    structured_content: Dict[str, Any]
    changes: str
    feedback: Optional[str]
    revised_by_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScriptSearchRequest(BaseModel):
    """剧本搜索请求"""
    query: Optional[str] = Field(None, description="搜索关键词")
    script_type: Optional[ScriptType] = Field(None, description="剧本类型过滤")
    status: Optional[ScriptStatus] = Field(None, description="状态过滤")
    project_id: Optional[int] = Field(None, description="项目ID过滤")
    created_after: Optional[datetime] = Field(None, description="创建时间之后")
    created_before: Optional[datetime] = Field(None, description="创建时间之前")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序顺序")
    skip: int = Field(0, ge=0, description="跳过数量")
    limit: int = Field(100, ge=1, le=1000, description="限制数量")
    
    @validator("sort_by")
    def validate_sort_by(cls, v):
        valid_fields = ["title", "created_at", "updated_at"]
        if v not in valid_fields:
            raise ValueError(f"sort_by must be one of {valid_fields}")
        return v
    
    @validator("sort_order")
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v


class ScriptStatsResponse(BaseModel):
    """剧本统计响应"""
    script_id: int
    word_count: int
    scene_count: int
    revision_count: int
    estimated_duration: Optional[float]
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]


class ScriptExportFormat(str, Enum):
    """剧本导出格式"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    JSON = "json"
    HTML = "html"


class ScriptExportRequest(BaseModel):
    """剧本导出请求"""
    format: ScriptExportFormat = Field(default=ScriptExportFormat.PDF, description="导出格式")
    include_metadata: bool = Field(default=True, description="是否包含元数据")
    include_revisions: bool = Field(default=False, description="是否包含修订历史")
    watermark: Optional[str] = Field(None, description="水印文本")


class ScriptBatchGenerateRequest(BaseModel):
    """剧本批量生成请求"""
    project_id: int = Field(..., ge=1, description="项目ID")
    prompts: List[str] = Field(..., min_items=1, max_items=10, description="生成提示词列表")
    script_type: ScriptType = Field(default=ScriptType.SHORT_DRAMA, description="剧本类型")
    total_episodes: int = Field(default=1, ge=1, description="总集数")
    target_duration: int = Field(default=60, ge=1, le=600, description="目标时长（秒）")
    concurrent: bool = Field(default=False, description="是否并发生成")
    
    @validator("prompts")
    def validate_prompts(cls, v):
        for prompt in v:
            if len(prompt) < 10 or len(prompt) > 2000:
                raise ValueError("Each prompt must be between 10 and 2000 characters")
        return v


class ScriptBatchGenerateResponse(BaseModel):
    """剧本批量生成响应"""
    job_id: str
    total_scripts: int
    completed_scripts: int
    failed_scripts: int
    status: str
    created_at: datetime


class ScriptAnalysisRequest(BaseModel):
    """剧本分析请求"""
    analyze_sentiment: bool = Field(default=True, description="分析情感")
    analyze_structure: bool = Field(default=True, description="分析结构")
    analyze_characters: bool = Field(default=True, description="分析角色")
    analyze_dialogue: bool = Field(default=True, description="分析对话")


class ScriptAnalysisResponse(BaseModel):
    """剧本分析响应"""
    script_id: int
    sentiment: Optional[Dict[str, Any]]
    structure: Optional[Dict[str, Any]]
    characters: Optional[List[Dict[str, Any]]]
    dialogue: Optional[Dict[str, Any]]
    readability_score: Optional[float]
    complexity_score: Optional[float]
    analyzed_at: datetime


class ScriptTemplate(BaseModel):
    """剧本模板"""
    id: int
    name: str
    description: Optional[str]
    template_type: ScriptType
    content_template: str
    variables: List[Dict[str, Any]]
    is_public: bool
    created_by_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ScriptTemplateCreateRequest(BaseModel):
    """剧本模板创建请求"""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    template_type: ScriptType = Field(..., description="模板类型")
    content_template: str = Field(..., description="内容模板")
    variables: List[Dict[str, Any]] = Field(default=[], description="模板变量")
    is_public: bool = Field(default=False, description="是否公开")


class ScriptTemplateApplyRequest(BaseModel):
    """应用剧本模板请求"""
    template_id: int = Field(..., description="模板ID")
    variables: Dict[str, Any] = Field(..., description="模板变量值")
    project_id: int = Field(..., description="项目ID")
