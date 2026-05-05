from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from backend.core.database import Base


class StoryboardStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    REVISING = "revising"
    APPROVED = "approved"


class ShotType(str, enum.Enum):
    EXTREME_WIDE = "extreme_wide"  # 极远景
    WIDE = "wide"  # 远景
    FULL = "full"  # 全景
    MEDIUM = "medium"  # 中景
    CLOSE_UP = "close_up"  # 特写
    EXTREME_CLOSE_UP = "extreme_close_up"  # 大特写


class CameraAngle(str, enum.Enum):
    EYE_LEVEL = "eye_level"  # 平视
    HIGH_ANGLE = "high_angle"  # 俯视
    LOW_ANGLE = "low_angle"  # 仰视
    DUTCH_ANGLE = "dutch_angle"  # 倾斜角度
    BIRDS_EYE = "birds_eye"  # 鸟瞰
    WORM_EYE = "worm_eye"  # 虫眼


class CameraMovement(str, enum.Enum):
    STATIC = "static"  # 固定
    PAN = "pan"  # 摇摄
    TILT = "tilt"  # 俯仰
    DOLLY = "dolly"  # 推拉
    TRACK = "track"  # 跟踪
    CRANE = "crane"  # 升降
    ZOOM = "zoom"  # 变焦
    HANDHELD = "handheld"  # 手持


class Storyboard(Base):
    __tablename__ = "storyboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    status = Column(SQLEnum(StoryboardStatus), default=StoryboardStatus.DRAFT)
    
    # 关联信息
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    episode_number = Column(Integer, default=1)
    
    # 分镜内容
    shots = Column(JSON)  # JSON格式的分镜列表
    total_shots = Column(Integer, default=0)
    total_duration = Column(Float)  # 总时长（秒）
    
    # 视觉风格
    visual_style = Column(String(100))  # 视觉风格
    color_palette = Column(JSON)  # 色彩方案
    lighting_style = Column(String(50))  # 灯光风格
    
    # 生成配置
    generation_prompt = Column(Text)  # 生成提示词
    ai_model = Column(String(50))  # 使用的AI模型
    generation_config = Column(JSON)  # 生成配置
    
    # 预览信息
    preview_images = Column(JSON)  # 预览图片URL
    preview_video_url = Column(String(500))  # 预览视频URL
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    generated_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    script = relationship("Script", back_populates="storyboards")
    project = relationship("Project", back_populates="storyboards")
    videos = relationship("Video", back_populates="storyboard")
    
    def __repr__(self):
        return f"<Storyboard(id={self.id}, name={self.name}, shots={self.total_shots})>"
    
    @property
    def is_completed(self) -> bool:
        return self.status == StoryboardStatus.COMPLETED or self.status == StoryboardStatus.APPROVED
    
    @property
    def can_generate_video(self) -> bool:
        return self.is_completed and self.shots is not None and len(self.shots) > 0


class StoryboardShot(Base):
    __tablename__ = "storyboard_shots"
    
    id = Column(Integer, primary_key=True, index=True)
    storyboard_id = Column(Integer, ForeignKey("storyboards.id"), nullable=False)
    shot_number = Column(Integer, nullable=False)
    
    # 镜头信息
    description = Column(Text, nullable=False)  # 镜头描述
    duration = Column(Float, default=3.0)  # 时长（秒）
    shot_type = Column(SQLEnum(ShotType), default=ShotType.MEDIUM)
    camera_angle = Column(SQLEnum(CameraAngle), default=CameraAngle.EYE_LEVEL)
    camera_movement = Column(SQLEnum(CameraMovement), default=CameraMovement.STATIC)
    
    # 视觉元素
    characters = Column(JSON)  # 角色列表
    props = Column(JSON)  # 道具列表
    setting = Column(String(200))  # 场景设置
    time_of_day = Column(String(50))  # 时间：day, night, dawn, dusk
    
    # 音频元素
    dialogue = Column(Text)  # 对白
    sound_effects = Column(JSON)  # 音效
    background_music = Column(String(100))  # 背景音乐
    
    # 生成信息
    visual_prompt = Column(Text)  # 视觉提示词
    reference_image_url = Column(String(500))  # 参考图片URL
    generated_image_url = Column(String(500))  # 生成图片URL
    
    # 排序与分组
    sequence_order = Column(Integer, default=0)
    scene_number = Column(Integer, default=1)
    
    def __repr__(self):
        return f"<StoryboardShot(shot={self.shot_number}, duration={self.duration}s)>"
