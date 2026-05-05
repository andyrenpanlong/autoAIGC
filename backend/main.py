from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import time
from contextlib import asynccontextmanager

from backend.config import settings
from backend.core.database import init_db, check_db_connection
from backend.api.v1 import router as api_v1_router
from backend.core.exceptions import setup_exception_handlers

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file) if settings.log_file else logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    - 启动时：初始化数据库，检查连接
    - 关闭时：清理资源
    """
    # 启动时
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # 检查数据库连接
    if not check_db_connection():
        logger.error("Failed to connect to database. Application may not function properly.")
    
    # 初始化数据库（仅开发环境）
    if settings.environment == "development":
        try:
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}")
    
    yield
    
    # 关闭时
    logger.info("Shutting down application")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI视频生成平台后端API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

# 添加中间件

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 可信主机中间件
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # 生产环境应配置具体域名
    )

# GZip压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 自定义中间件：请求日志
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Request failed: {e}")
        raise
    
    # 计算处理时间
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # 记录响应信息
    logger.info(f"Response: {response.status_code} ({process_time:.3f}s)")
    
    return response


# 设置异常处理器
setup_exception_handlers(app)

# 挂载静态文件
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册API路由
app.include_router(api_v1_router, prefix="/api/v1")


# 健康检查端点
@app.get("/health", tags=["Health"])
async def health_check():
    """
    健康检查端点
    
    返回应用状态和依赖服务状态
    """
    health_status = {
        "status": "healthy",
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        },
        "services": {
            "database": check_db_connection(),
            "redis": True,  # 需要实现Redis健康检查
            "storage": True,  # 需要实现存储健康检查
        },
        "timestamp": time.time(),
    }
    
    # 如果有服务不可用，返回503状态
    if not all(health_status["services"].values()):
        health_status["status"] = "degraded"
        return JSONResponse(
            content=health_status,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    
    return health_status


# 根端点
@app.get("/", tags=["Root"])
async def root():
    """
    根端点
    
    返回应用基本信息
    """
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "description": "AI视频生成平台后端API",
        "docs": "/docs" if settings.debug else None,
        "health": "/health",
        "api": "/api/v1",
    }


# 版本信息端点
@app.get("/version", tags=["Info"])
async def version_info():
    """
    版本信息端点
    
    返回详细的版本信息
    """
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "python_version": "3.12+",
        "framework": "FastAPI",
        "database": "PostgreSQL",
        "cache": "Redis",
        "features": [
            "用户认证与授权",
            "剧本生成（LLM集成）",
            "分镜脚本自动化",
            "多模型视频生成",
            "并发批量生成",
            "任务队列与进度跟踪",
        ],
    }


# 错误处理示例
@app.get("/error-test", tags=["Test"])
async def error_test():
    """
    错误测试端点（仅开发环境可用）
    
    用于测试错误处理机制
    """
    if settings.environment != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in development environment",
        )
    
    # 模拟各种错误
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="This is a test error for error handling testing",
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if settings.environment == "production" else 1,
        log_level=settings.log_level.lower(),
    )
