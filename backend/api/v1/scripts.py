from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from sqlalchemy.orm import Session
import logging

from backend.core.database import get_db
from backend.services.auth import AuthService
from backend.services.script_gen import ScriptGenerationService
from backend.models.user import User
from backend.models.script import Script, ScriptStatus, ScriptType
from backend.schemas.script import (
    ScriptCreateRequest,
    ScriptResponse,
    ScriptListResponse,
    ScriptUpdateRequest,
    ScriptRevisionCreateRequest,
    ScriptRevisionResponse,
    ScriptGenerateRequest,
    ScriptSearchRequest,
)
from backend.core.exceptions import BusinessError, ExternalServiceError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def generate_script(
    request: ScriptGenerateRequest,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    生成剧本
    
    根据提示词和配置生成AI剧本
    """
    try:
        script_service = ScriptGenerationService(db)
        
        script = script_service.generate_script(
            project_id=request.project_id,
            user_id=current_user.id,
            prompt=request.prompt,
            script_type=request.script_type or ScriptType.SHORT_DRAMA,
            episode_number=request.episode_number or 1,
            total_episodes=request.total_episodes or 1,
            target_duration=request.target_duration or 60,
            characters=request.characters,
            settings=request.settings,
            tone=request.tone or "dramatic",
            style=request.style or "cinematic",
            language=request.language or "zh",
        )
        
        return ScriptResponse.from_orm(script)
        
    except BusinessError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=e.message,
        )
    except Exception as e:
        logger.error(f"Failed to generate script: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate script",
        )


@router.post("/", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def create_script(
    request: ScriptCreateRequest,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    创建剧本
    
    手动创建剧本（不调用AI生成）
    """
    try:
        script_service = ScriptGenerationService(db)
        
        # 创建剧本记录
        script = Script(
            title=request.title,
            description=request.description,
            type=request.script_type or ScriptType.SHORT_DRAMA,
            status=ScriptStatus.DRAFT,
            project_id=request.project_id,
            author_id=current_user.id,
            episode_number=request.episode_number or 1,
            total_episodes=request.total_episodes or 1,
            target_duration=request.target_duration or 60,
            characters=request.characters or [],
            settings=request.settings or [],
            tone=request.tone or "dramatic",
            style=request.style or "cinematic",
            language=request.language or "zh",
            content=request.content,
            structured_content=request.structured_content,
        )
        
        db.add(script)
        db.commit()
        db.refresh(script)
        
        logger.info(f"Script created: script_id={script.id}, user_id={current_user.id}")
        
        return ScriptResponse.from_orm(script)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create script: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create script",
        )


@router.get("/", response_model=ScriptListResponse)
async def list_scripts(
    project_id: Optional[int] = Query(None, description="项目ID过滤"),
    status: Optional[ScriptStatus] = Query(None, description="状态过滤"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    列出剧本
    
    获取当前用户的剧本列表，支持分页和过滤
    """
    try:
        script_service = ScriptGenerationService(db)
        
        scripts, total = script_service.list_scripts(
            user_id=current_user.id,
            project_id=project_id,
            skip=skip,
            limit=limit,
            status=status,
        )
        
        return ScriptListResponse(
            scripts=[ScriptResponse.from_orm(script) for script in scripts],
            total=total,
            skip=skip,
            limit=limit,
        )
        
    except Exception as e:
        logger.error(f"Failed to list scripts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list scripts",
        )


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取剧本详情
    
    获取指定剧本的详细信息
    """
    try:
        script_service = ScriptGenerationService(db)
        
        script = script_service.get_script(script_id, current_user.id)
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Script not found",
            )
        
        return ScriptResponse.from_orm(script)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get script: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get script",
        )


@router.put("/{script_id}", response_model=ScriptResponse)
async def update_script(
    script_id: int,
    request: ScriptUpdateRequest,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    更新剧本
    
    更新剧本的标题、内容等信息
    """
    try:
        script_service = ScriptGenerationService(db)
        
        script = script_service.update_script(
            script_id=script_id,
            user_id=current_user.id,
            title=request.title,
            content=request.content,
            structured_content=request.structured_content,
        )
        
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Script not found or access denied",
            )
        
        return ScriptResponse.from_orm(script)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update script: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update script",
        )


@router.post("/{script_id}/revisions", response_model=ScriptRevisionResponse, status_code=status.HTTP_201_CREATED)
async def create_revision(
    script_id: int,
    request: ScriptRevisionCreateRequest,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    创建剧本修订
    
    创建剧本的修订版本，记录变更历史
    """
    try:
        script_service = ScriptGenerationService(db)
        
        revision = script_service.create_revision(
            script_id=script_id,
            user_id=current_user.id,
            content=request.content,
            structured_content=request.structured_content,
            changes=request.changes,
            feedback=request.feedback,
        )
        
        if not revision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Script not found or access denied",
            )
        
        return ScriptRevisionResponse.from_orm(revision)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create revision: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create revision",
        )


@router.get("/{script_id}/revisions", response_model=List[ScriptRevisionResponse])
async def list_revisions(
    script_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    列出剧本修订
    
    获取剧本的所有修订历史
    """
    try:
        # 首先检查剧本是否存在且用户有权限
        script_service = ScriptGenerationService(db)
        script = script_service.get_script(script_id, current_user.id)
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Script not found",
            )
        
        # 获取修订列表
        from backend.models.script import ScriptRevision
        revisions = db.query(ScriptRevision).filter(
            ScriptRevision.script_id == script_id,
        ).order_by(ScriptRevision.revision_number.desc()).all()
        
        return [ScriptRevisionResponse.from_orm(rev) for rev in revisions]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list revisions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list revisions",
        )


@router.post("/{script_id}/approve", response_model=ScriptResponse)
async def approve_script(
    script_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    批准剧本
    
    将剧本标记为已批准状态，可以进入下一阶段
    """
    try:
        script_service = ScriptGenerationService(db)
        
        script = script_service.approve_script(script_id, current_user.id)
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Script not found or access denied",
            )
        
        return ScriptResponse.from_orm(script)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve script: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve script",
        )


@router.delete("/{script_id}")
async def delete_script(
    script_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    删除剧本
    
    永久删除剧本及其所有修订
    """
    try:
        script_service = ScriptGenerationService(db)
        
        success = script_service.delete_script(script_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Script not found or access denied",
            )
        
        return {"message": "Script deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete script: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete script",
        )


@router.post("/search", response_model=ScriptListResponse)
async def search_scripts(
    request: ScriptSearchRequest,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    搜索剧本
    
    根据多种条件搜索剧本
    """
    try:
        from sqlalchemy import or_
        
        # 构建查询
        query = db.query(Script).filter(Script.author_id == current_user.id)
        
        # 关键词搜索
        if request.query:
            search_query = f"%{request.query}%"
            query = query.filter(
                or_(
                    Script.title.ilike(search_query),
                    Script.description.ilike(search_query),
                    Script.content.ilike(search_query),
                )
            )
        
        # 类型过滤
        if request.script_type:
            query = query.filter(Script.type == request.script_type)
        
        # 状态过滤
        if request.status:
            query = query.filter(Script.status == request.status)
        
        # 项目过滤
        if request.project_id:
            query = query.filter(Script.project_id == request.project_id)
        
        # 时间范围过滤
        if request.created_after:
            query = query.filter(Script.created_at >= request.created_after)
        
        if request.created_before:
            query = query.filter(Script.created_at <= request.created_before)
        
        # 获取总数
        total = query.count()
        
        # 应用排序和分页
        order_by = Script.created_at.desc()
        if request.sort_by:
            if request.sort_by == "title":
                order_by = Script.title.asc() if request.sort_order == "asc" else Script.title.desc()
            elif request.sort_by == "updated_at":
                order_by = Script.updated_at.asc() if request.sort_order == "asc" else Script.updated_at.desc()
        
        scripts = query.order_by(order_by).offset(request.skip).limit(request.limit).all()
        
        return ScriptListResponse(
            scripts=[ScriptResponse.from_orm(script) for script in scripts],
            total=total,
            skip=request.skip,
            limit=request.limit,
        )
        
    except Exception as e:
        logger.error(f"Failed to search scripts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search scripts",
        )


@router.get("/{script_id}/stats")
async def get_script_stats(
    script_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取剧本统计
    
    获取剧本的统计信息，如字数、场景数等
    """
    try:
        script_service = ScriptGenerationService(db)
        script = script_service.get_script(script_id, current_user.id)
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Script not found",
            )
        
        # 计算统计信息
        word_count = len(script.content.split()) if script.content else 0
        scene_count = len(script.structured_content.get("scenes", [])) if script.structured_content else 0
        
        # 获取修订数量
        from backend.models.script import ScriptRevision
        revision_count = db.query(ScriptRevision).filter(
            ScriptRevision.script_id == script_id,
        ).count()
        
        return {
            "script_id": script_id,
            "word_count": word_count,
            "scene_count": scene_count,
            "revision_count": revision_count,
            "estimated_duration": script.estimated_duration,
            "status": script.status.value,
            "created_at": script.created_at.isoformat() if script.created_at else None,
            "updated_at": script.updated_at.isoformat() if script.updated_at else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get script stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get script stats",
        )
