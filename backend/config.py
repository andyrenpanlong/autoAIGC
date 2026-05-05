from pydantic_settings import BaseSettings
from typing import Optional, List
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class ModelProvider(str, Enum):
    LOCAL = "local"
    OPENAI = "openai"
    RUNWAY = "runway"
    PIKA = "pika"
    GOOGLE = "google"
    STABILITY = "stability"


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "AI Video Generation Platform"
    app_version: str = "0.1.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # 数据库配置
    database_url: str = "postgresql://postgres:password@localhost:5432/ai_video_db"
    database_pool_size: int = 20
    database_max_overflow: int = 40
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    redis_pool_size: int = 10
    
    # JWT配置
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # 文件存储配置
    upload_dir: str = "./uploads"
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    allowed_file_types: List[str] = ["image/jpeg", "image/png", "image/gif", "video/mp4", "video/quicktime"]
    
    # MinIO/S3配置
    storage_type: str = "local"  # local, minio, s3
    minio_endpoint: Optional[str] = None
    minio_access_key: Optional[str] = None
    minio_secret_key: Optional[str] = None
    minio_bucket: str = "ai-videos"
    s3_region: Optional[str] = None
    s3_bucket: Optional[str] = None
    
    # 模型配置
    default_model_provider: ModelProvider = ModelProvider.LOCAL
    enable_local_models: bool = True
    local_models_dir: str = "./models"
    
    # LTX模型配置
    ltx_model_path: Optional[str] = None
    ltx_model_version: str = "2.3"
    ltx_cache_dir: str = "./cache/ltx"
    
    # Stable Diffusion配置
    sd_model_path: Optional[str] = None
    sd_model_version: str = "xl-1.0"
    sd_cache_dir: str = "./cache/sd"
    
    # OpenAI配置
    openai_api_key: Optional[str] = None
    openai_organization: Optional[str] = None
    openai_sora_model: str = "sora-1.0"
    
    # Runway配置
    runway_api_key: Optional[str] = None
    runway_model: str = "gen-2"
    
    # Pika配置
    pika_api_key: Optional[str] = None
    
    # Google配置
    google_api_key: Optional[str] = None
    google_veo_model: str = "veo-1.0"
    
    # Stability AI配置
    stability_api_key: Optional[str] = None
    stability_model: str = "stable-diffusion-xl-1024-v1-0"
    
    # LLM配置（用于剧本生成）
    llm_provider: str = "openai"  # openai, anthropic, local
    openai_llm_model: str = "gpt-4-turbo"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-opus-20240229"
    local_llm_url: Optional[str] = "http://localhost:11434"
    local_llm_model: str = "llama3.1:8b"
    
    # 任务队列配置
    max_concurrent_tasks: int = 4
    task_timeout_seconds: int = 3600  # 1小时
    video_generation_timeout: int = 1800  # 30分钟
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = "./logs/app.log"
    
    # 监控配置
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()
