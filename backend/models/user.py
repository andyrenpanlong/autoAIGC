from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    CREATOR = "creator"
    ADMIN = "admin"


class UserPlan(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(200))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    plan = Column(SQLEnum(UserPlan), default=UserPlan.FREE)
    
    # API密钥配置
    openai_api_key = Column(String(255), nullable=True)
    runway_api_key = Column(String(255), nullable=True)
    pika_api_key = Column(String(255), nullable=True)
    google_api_key = Column(String(255), nullable=True)
    stability_api_key = Column(String(255), nullable=True)
    
    # 使用限制
    monthly_credits = Column(Integer, default=100)  # 每月生成次数
    used_credits = Column(Integer, default=0)
    max_concurrent_jobs = Column(Integer, default=2)
    max_video_length = Column(Integer, default=60)  # 秒
    
    # 偏好设置
    preferred_model = Column(String(50), default="ltx-2.3")
    default_video_resolution = Column(String(20), default="720p")
    default_video_duration = Column(Integer, default=15)  # 秒
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    scripts = relationship("Script", back_populates="author", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="creator", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
    
    @property
    def remaining_credits(self) -> int:
        return max(0, self.monthly_credits - self.used_credits)
    
    @property
    def can_create_job(self) -> bool:
        return self.remaining_credits > 0 and self.is_active


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    session_token = Column(String(512), unique=True, index=True, nullable=False)
    refresh_token = Column(String(512), unique=True, index=True, nullable=False)
    user_agent = Column(Text)
    ip_address = Column(String(45))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"
