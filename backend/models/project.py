from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from backend.core.database import Base


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"


class ProjectType(str, enum.Enum):
    SHORT_DRAMA = "short_drama"  # 短剧
    ADVERTISEMENT = "advertisement"  # 广告
    SOCIAL_MEDIA = "social_media"  # 社交媒体
    EDUCATIONAL = "educational"  # 教育
    ENTERTAINMENT = "entertainment"  # 娱乐
    OTHER = "other"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(SQLEnum(ProjectType), default=ProjectType.SHORT_DRAMA)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    
    # 项目配置
    total_episodes = Column(Integer, default=1)  # 总集数
    current_episode = Column(Integer, default=1)  # 当前集数
    target_duration = Column(Integer, default=60)  # 目标时长（秒）
    target_resolution = Column(String(20), default="720p")
    aspect_ratio = Column(String(20), default="16:9")  # 宽高比
    
    # 风格设置
    style_prompt = Column(Text)  # 风格提示词
    reference_images = Column(Text)  # JSON格式的参考图片URL
    color_palette = Column(String(100))  # 色彩方案
    
    # 并发设置
    concurrent_generation = Column(Boolean, default=False)
    max_concurrent_episodes = Column(Integer, default=1)
    
    # 所有者
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    owner = relationship("User", back_populates="projects")
    scripts = relationship("Script", back_populates="project", cascade="all, delete-orphan")
    storyboards = relationship("Storyboard", back_populates="project", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
    
    @property
    def progress(self) -> float:
        """计算项目进度（0-100）"""
        if self.status == ProjectStatus.COMPLETED:
            return 100.0
        elif self.status == ProjectStatus.DRAFT:
            return 0.0
        elif self.total_episodes > 0:
            return (self.current_episode / self.total_episodes) * 100
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        return self.status == ProjectStatus.COMPLETED
    
    @property
    def can_generate(self) -> bool:
        return self.status in [ProjectStatus.DRAFT, ProjectStatus.IN_PROGRESS]


class ProjectCollaborator(Base):
    __tablename__ = "project_collaborators"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="editor")  # editor, viewer, admin
    permissions = Column(Text)  # JSON格式的权限配置
    
    # 时间戳
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    joined_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    project = relationship("Project")
    user = relationship("User")
    
    def __repr__(self):
        return f"<ProjectCollaborator(project_id={self.project_id}, user_id={self.user_id})>"
