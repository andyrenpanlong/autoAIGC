from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import logging

from backend.core.database import get_db
from backend.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
)
from backend.models.user import User, UserSession
from backend.schemas.auth import (
    UserCreate,
    UserResponse,
    TokenResponse,
    LoginRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    UpdateProfileRequest,
)
from backend.services.auth import AuthService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth2配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    用户注册
    
    创建新用户账户
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
        )
        
        logger.info(f"User registered: {user.email}")
        return UserResponse.from_orm(user)
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    用户登录
    
    使用用户名/邮箱和密码登录，返回访问令牌和刷新令牌
    """
    try:
        auth_service = AuthService(db)
        
        # 尝试使用用户名或邮箱登录
        user = auth_service.authenticate_user(
            identifier=form_data.username,  # 可能是用户名或邮箱
            password=form_data.password,
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建访问令牌
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        # 创建刷新令牌
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        # 创建用户会话
        session = UserSession(
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db.add(session)
        db.commit()
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800,  # 30分钟
            user=UserResponse.from_orm(user),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    刷新访问令牌
    
    使用刷新令牌获取新的访问令牌
    """
    try:
        # 验证刷新令牌
        payload = verify_token(refresh_data.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        user_id = int(payload.get("sub"))
        
        # 查找用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        
        # 查找有效的会话
        session = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.refresh_token == refresh_data.refresh_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow(),
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
            )
        
        # 创建新的访问令牌
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        # 更新会话令牌
        session.session_token = access_token
        session.last_activity_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,  # 返回相同的刷新令牌
            token_type="bearer",
            expires_in=1800,
            user=UserResponse.from_orm(user),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    用户登出
    
    使当前用户的会话失效
    """
    try:
        # 使当前用户的所有会话失效
        db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True,
        ).update({"is_active": False})
        db.commit()
        
        logger.info(f"User logged out: {current_user.email}")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(AuthService.get_current_user),
):
    """
    获取当前用户信息
    
    返回当前登录用户的详细信息
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新用户资料
    
    更新当前用户的个人信息
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.update_user_profile(
            user_id=current_user.id,
            full_name=profile_data.full_name,
            email=profile_data.email,
            username=profile_data.username,
        )
        
        logger.info(f"Profile updated for user: {user.email}")
        
        return UserResponse.from_orm(user)
        
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    修改密码
    
    修改当前用户的密码
    """
    try:
        auth_service = AuthService(db)
        
        # 验证当前密码
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
        
        # 更新密码
        auth_service.change_password(
            user_id=current_user.id,
            new_password=password_data.new_password,
        )
        
        # 使所有现有会话失效（安全考虑）
        db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True,
        ).update({"is_active": False})
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/reset-password-request")
async def request_password_reset(
    email: str,
    db: Session = Depends(get_db),
):
    """
    请求重置密码
    
    发送密码重置邮件（需要实现邮件服务）
    """
    try:
        # 查找用户
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # 出于安全考虑，即使用户不存在也返回成功
            logger.info(f"Password reset requested for non-existent email: {email}")
            return {"message": "If the email exists, a reset link has been sent"}
        
        # 这里应该生成重置令牌并发送邮件
        # 由于邮件服务未实现，暂时记录日志
        logger.info(f"Password reset requested for user: {user.email}")
        
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取用户会话列表
    
    返回当前用户的所有活跃会话
    """
    try:
        sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow(),
        ).order_by(UserSession.created_at.desc()).all()
        
        session_list = []
        for session in sessions:
            session_list.append({
                "id": session.id,
                "user_agent": session.user_agent,
                "ip_address": session.ip_address,
                "created_at": session.created_at.isoformat(),
                "last_activity_at": session.last_activity_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
            })
        
        return {"sessions": session_list}
        
    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    撤销会话
    
    使指定的用户会话失效
    """
    try:
        session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == current_user.id,
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        
        session.is_active = False
        db.commit()
        
        logger.info(f"Session revoked: {session_id} for user: {current_user.email}")
        
        return {"message": "Session revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
