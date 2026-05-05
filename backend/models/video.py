from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from backend.core.database import Base


class VideoStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoQuality(str, enum.Enum):
    LOW = "low"  # 360p
    MEDIUM = "medium"  # 720p
    HIGH = "high"  # 1080p
    ULTRA = "ultra"  # 4K


class VideoFormat(str, enum.Enum):
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    WEBM = "webm"
    GIF = "gif"


class VideoModel(str, enum.Enum):
    LTX_2_3 = "ltx-2.3"
    STABLE_VIDEO = "stable-video"
    ANIMATEDIFF = "animatediff"
    OPENAI_SORA = "openai-sora"
    RUNWAY_GEN2 = "runway-gen2"
    PIKA = "pika"
    GOOGLE_VEO = "google-veo"


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.PENDING)
    
    # 关联信息
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=True)
    storyboard_id = Column(Integer, ForeignKey("storyboards.id"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 视频信息
    episode_number = Column(Integer, default=1)
    duration = Column(Float)  # 时长（秒）
    resolution = Column(String(20))  # 分辨率
    quality = Column(SQLEnum(VideoQuality), default=VideoQuality.MEDIUM)
    format = Column(SQLEnum(VideoFormat), default=VideoFormat.MP4)
    aspect_ratio = Column(String(20), default="16:9")
    frame_rate = Column(Integer, default=30)  # 帧率
    
    # 文件信息
    file_url = Column(String(500))  # 视频文件URL
    thumbnail_url = Column(String(500))  # 缩略图URL
    preview_url = Column(String(500))  # 预览URL
    file_size = Column(Integer)  # 文件大小（字节）
    
    # 生成配置
    model = Column(SQLEnum(VideoModel), default=VideoModel.LTX_2_3)
    prompt = Column(Text)  # 生成提示词
    negative_prompt = Column(Text)  # 负面提示词
    generation_config = Column(JSON)  # 生成配置参数
    
    # 输入资源
    input_images = Column(JSON)  # 输入图片URL列表
    input_videos = Column(JSON)  # 输入视频URL列表
    audio_track_url = Column(String(500))  # 音频轨道URL
    
    # 任务信息
    task_id = Column(String(100))  # Celery任务ID
    job_id = Column(String(100))  # 作业ID
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # 性能指标
    generation_time = Column(Float)  # 生成时间（秒）
    gpu_memory_used = Column(Float)  # GPU内存使用（MB）
    cost = Column(Float, default=0.0)  # 生成成本
    
    # 错误信息
    error_message = Column(Text)
    error_stack_trace = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    project = relationship("Project", back_populates="videos")
    script = relationship("Script", back_populates="videos")
    storyboard = relationship("Storyboard", back_populates="videos")
    creator = relationship("User", back_populates="videos")
    
    def __repr__(self):
        return f"<Video(id={self.id}, name={self.name}, status={self.status})>"
    
    @property
    def is_finished(self) -> bool:
        return self.status in [VideoStatus.COMPLETED, VideoStatus.FAILED, VideoStatus.CANCELLED]
    
    @property
    def is_successful(self) -> bool:
        return self.status == VideoStatus.COMPLETED and self.file_url is not None
    
    @property
    def progress(self) -> float:
        """计算生成进度（0-100）"""
        if self.is_finished:
            return 100.0 if self.is_successful else 0.0
        elif self.status == VideoStatus.GENERATING:
            return 50.0
        elif self.status == VideoStatus.PROCESSING:
            return 75.0
        return 0.0


class VideoGenerationJob(Base):
    __tablename__ = "video_generation_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # 作业配置
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    total_videos = Column(Integer, default=1)  # 总视频数
    completed_videos = Column(Integer, default=0)  # 已完成视频数
    failed_videos = Column(Integer, default=0)  # 失败视频数
    
    # 并发设置
    concurrent_limit = Column(Integer, default=1)
    current_concurrent = Column(Integer, default=0)
    
    # 状态
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.PENDING)
    is_batch = Column(Boolean, default=False)  # 是否批量作业
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    project = relationship("Project")
    videos = relationship("Video", backref="generation_job")
    
    def __repr__(self):
        return f"<VideoGenerationJob(id={self.id}, name={self.name}, status={self.status})>"
    
    @property
    def progress(self) -> float:
        if self.total_videos > 0:
            return (self.completed_videos / self.total_videos) * 100
        return 0.0
    
    @property
    def can_add_video(self) -> bool:
        return self.current_concurrent < self.concurrent_limit and not self.is_finished
    
    @property
    def is_finished(self) -> bool:
        return self.status in [VideoStatus.COMPLETED, VideoStatus.FAILED, VideoStatus.CANCELLED]
