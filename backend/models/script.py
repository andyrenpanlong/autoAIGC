from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from backend.core.database import Base


class ScriptStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    REVISING = "revising"
    APPROVED = "approved"


class ScriptType(str, enum.Enum):
    SHORT_DRAMA = "short_drama"
    AD_SCRIPT = "ad_script"
    SOCIAL_MEDIA = "social_media"
    EDUCATIONAL = "educational"
    PRODUCT_DEMO = "product_demo"
    TESTIMONIAL = "testimonial"


class Script(Base):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(SQLEnum(ScriptType), default=ScriptType.SHORT_DRAMA)
    status = Column(SQLEnum(ScriptStatus), default=ScriptStatus.DRAFT)
    
    # 剧本内容
    content = Column(Text)  # 完整剧本文本
    structured_content = Column(JSON)  # 结构化剧本数据
    episode_number = Column(Integer, default=1)  # 集数
    total_episodes = Column(Integer, default=1)  # 总集数
    
    # 时长配置
    target_duration = Column(Integer, default=60)  # 目标时长（秒）
    estimated_duration = Column(Float)  # 预估时长
    
    # 角色信息
    characters = Column(JSON)  # JSON格式的角色列表
    settings = Column(JSON)  # JSON格式的场景设置
    
    # 风格与语气
    tone = Column(String(50))  # 语气：formal, casual, humorous, dramatic
    style = Column(String(50))  # 风格：cinematic, documentary, animation
    language = Column(String(10), default="zh")  # 语言
    
    # 生成配置
    prompt = Column(Text)  # 原始提示词
    llm_model = Column(String(50))  # 使用的LLM模型
    llm_config = Column(JSON)  # LLM配置参数
    
    # 关联项目
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    generated_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    project = relationship("Project", back_populates="scripts")
    author = relationship("User", back_populates="scripts")
    storyboards = relationship("Storyboard", back_populates="script", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="script", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Script(id={self.id}, title={self.title}, type={self.type})>"
    
    @property
    def is_completed(self) -> bool:
        return self.status == ScriptStatus.COMPLETED or self.status == ScriptStatus.APPROVED
    
    @property
    def can_generate_storyboard(self) -> bool:
        return self.is_completed and self.content is not None


class ScriptRevision(Base):
    __tablename__ = "script_revisions"
    
    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=False)
    revision_number = Column(Integer, default=1)
    
    # 修订内容
    content = Column(Text)
    structured_content = Column(JSON)
    changes = Column(Text)  # 变更说明
    feedback = Column(Text)  # 反馈意见
    
    # 修订者
    revised_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    script = relationship("Script")
    revised_by = relationship("User")
    
    def __repr__(self):
        return f"<ScriptRevision(script_id={self.script_id}, revision={self.revision_number})>"
