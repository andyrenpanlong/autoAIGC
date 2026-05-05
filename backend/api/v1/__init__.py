from fastapi import APIRouter
from backend.api.v1 import auth, projects, scripts, storyboards, videos, models

# 创建API v1路由器
router = APIRouter(prefix="/v1", tags=["v1"])

# 包含子路由
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(projects.router, prefix="/projects", tags=["Projects"])
router.include_router(scripts.router, prefix="/scripts", tags=["Scripts"])
router.include_router(storyboards.router, prefix="/storyboards", tags=["Storyboards"])
router.include_router(videos.router, prefix="/videos", tags=["Videos"])
router.include_router(models.router, prefix="/models", tags=["Models"])


@router.get("/")
async def api_v1_root():
    """
    API v1 根端点
    
    返回API版本信息
    """
    return {
        "api": "v1",
        "version": "1.0.0",
        "description": "AI视频生成平台API v1",
        "endpoints": {
            "auth": "/api/v1/auth",
            "projects": "/api/v1/projects",
            "scripts": "/api/v1/scripts",
            "storyboards": "/api/v1/storyboards",
            "videos": "/api/v1/videos",
            "models": "/api/v1/models",
        },
    }
