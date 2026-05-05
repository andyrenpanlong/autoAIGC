from typing import Optional, Tuple
from datetime import datetime
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.core.database import get_db
from backend.core.security import (
    verify_password,
    get_password_hash,
    verify_token,
    create_access_token,
)
from backend.models.user import User, UserRole
from backend.core.exceptions import AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

# OAuth2配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class AuthService:
    """认证服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        """
        获取当前用户
        
        Args:
            token: JWT令牌
            db: 数据库会话
            
        Returns:
            User: 当前用户对象
            
        Raises:
            HTTPException: 如果认证失败
        """
        try:
            # 验证令牌
            payload = verify_token(token)
            if not payload:
                raise AuthenticationError("Invalid authentication token")
            
            # 获取用户ID
            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationError("Invalid token payload")
            
            # 查找用户
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                raise AuthenticationError("User not found")
            
            if not user.is_active:
                raise AuthenticationError("User is inactive")
            
            return user
            
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message,
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Failed to get current user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
    
    @staticmethod
    def get_current_active_user(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """
        获取当前活跃用户
        
        Args:
            current_user: 当前用户
            
        Returns:
            User: 活跃用户对象
            
        Raises:
            HTTPException: 如果用户不活跃
        """
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
        return current_user
    
    @staticmethod
    def require_role(required_role: UserRole):
        """
        要求特定角色的装饰器
        
        Args:
            required_role: 需要的角色
            
        Returns:
            装饰器函数
        """
        def role_checker(current_user: User = Depends(get_current_user)) -> User:
            if current_user.role != required_role and current_user.role != UserRole.ADMIN:
                raise AuthorizationError(
                    f"Requires {required_role.value} role",
                    details={"required_role": required_role.value, "user_role": current_user.role.value}
                )
            return current_user
        return role_checker
    
    @staticmethod
    def require_any_role(required_roles: list[UserRole]):
        """
        要求任意指定角色的装饰器
        
        Args:
            required_roles: 需要的角色列表
            
        Returns:
            装饰器函数
        """
        def role_checker(current_user: User = Depends(get_current_user)) -> User:
            if current_user.role == UserRole.ADMIN:
                return current_user
            
            if current_user.role not in required_roles:
                raise AuthorizationError(
                    f"Requires one of roles: {[r.value for r in required_roles]}",
                    details={"required_roles": [r.value for r in required_roles], "user_role": current_user.role.value}
                )
            return current_user
        return role_checker
    
    def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> User:
        """
        注册新用户
        
        Args:
            email: 邮箱
            username: 用户名
            password: 密码
            full_name: 全名
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            HTTPException: 如果注册失败
        """
        try:
            # 检查邮箱是否已存在
            existing_user = self.db.query(User).filter(
                (User.email == email) | (User.username == username)
            ).first()
            
            if existing_user:
                if existing_user.email == email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered",
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken",
                    )
            
            # 创建用户
            hashed_password = get_password_hash(password)
            user = User(
                email=email,
                username=username,
                full_name=full_name or username,
                hashed_password=hashed_password,
                is_active=True,
                role=UserRole.USER,
                created_at=datetime.utcnow(),
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User registered: {email}")
            return user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error during registration: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed due to database constraint",
            )
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Registration failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed",
            )
    
    def authenticate_user(
        self,
        identifier: str,
        password: str,
    ) -> Optional[User]:
        """
        认证用户
        
        Args:
            identifier: 用户名或邮箱
            password: 密码
            
        Returns:
            Optional[User]: 认证成功的用户，如果失败则返回None
        """
        try:
            # 尝试通过邮箱或用户名查找用户
            user = self.db.query(User).filter(
                (User.email == identifier) | (User.username == identifier)
            ).first()
            
            if not user:
                logger.warning(f"Authentication failed: user not found for identifier {identifier}")
                return None
            
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Authentication failed: incorrect password for user {user.email}")
                return None
            
            if not user.is_active:
                logger.warning(f"Authentication failed: user {user.email} is inactive")
                return None
            
            logger.info(f"User authenticated: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def update_user_profile(
        self,
        user_id: int,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
    ) -> User:
        """
        更新用户资料
        
        Args:
            user_id: 用户ID
            full_name: 全名
            email: 邮箱
            username: 用户名
            
        Returns:
            User: 更新后的用户对象
            
        Raises:
            HTTPException: 如果更新失败
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            
            # 检查邮箱是否已被其他用户使用
            if email and email != user.email:
                existing_user = self.db.query(User).filter(
                    User.email == email,
                    User.id != user_id,
                ).first()
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already in use",
                    )
                user.email = email
            
            # 检查用户名是否已被其他用户使用
            if username and username != user.username:
                existing_user = self.db.query(User).filter(
                    User.username == username,
                    User.id != user_id,
                ).first()
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken",
                    )
                user.username = username
            
            if full_name:
                user.full_name = full_name
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User profile updated: {user.email}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Profile update failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Profile update failed",
            )
    
    def change_password(
        self,
        user_id: int,
        new_password: str,
    ) -> None:
        """
        修改用户密码
        
        Args:
            user_id: 用户ID
            new_password: 新密码
            
        Raises:
            HTTPException: 如果修改失败
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            
            hashed_password = get_password_hash(new_password)
            user.hashed_password = hashed_password
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Password changed for user: {user.email}")
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Password change failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed",
            )
    
    def update_user_role(
        self,
        user_id: int,
        new_role: UserRole,
        current_user: User,
    ) -> User:
        """
        更新用户角色（仅管理员可用）
        
        Args:
            user_id: 用户ID
            new_role: 新角色
            current_user: 当前操作用户
            
        Returns:
            User: 更新后的用户对象
            
        Raises:
            HTTPException: 如果更新失败或权限不足
        """
        try:
            # 检查当前用户是否为管理员
            if current_user.role != UserRole.ADMIN:
                raise AuthorizationError("Admin role required")
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            
            # 不能修改自己的角色
            if user.id == current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot change your own role",
                )
            
            user.role = new_role
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User role updated: {user.email} -> {new_role.value}")
            return user
            
        except AuthorizationError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=e.message,
            )
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Role update failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Role update failed",
            )
    
    def deactivate_user(
        self,
        user_id: int,
        current_user: User,
    ) -> User:
        """
        停用用户（仅管理员可用）
        
        Args:
            user_id: 用户ID
            current_user: 当前操作用户
            
        Returns:
            User: 停用后的用户对象
            
        Raises:
            HTTPException: 如果操作失败或权限不足
        """
        try:
            # 检查当前用户是否为管理员
            if current_user.role != UserRole.ADMIN:
                raise AuthorizationError("Admin role required")
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            
            # 不能停用自己
            if user.id == current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate yourself",
                )
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User deactivated: {user.email}")
            return user
            
        except AuthorizationError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=e.message,
            )
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"User deactivation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User deactivation failed",
            )
    
    def activate_user(
        self,
        user_id: int,
        current_user: User,
    ) -> User:
        """
        激活用户（仅管理员可用）
        
        Args:
            user_id: 用户ID
            current_user: 当前操作用户
            
        Returns:
            User: 激活后的用户对象
            
        Raises:
            HTTPException: 如果操作失败或权限不足
        """
        try:
            # 检查当前用户是否为管理员
            if current_user.role != UserRole.ADMIN:
                raise AuthorizationError("Admin role required")
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            
            user.is_active = True
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User activated: {user.email}")
            return user
            
        except AuthorizationError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=e.message,
            )
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"User activation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User activation failed",
            )
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象，如果不存在则返回None
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 用户邮箱
            
        Returns:
            Optional[User]: 用户对象，如果不存在则返回None
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[User]: 用户对象，如果不存在则返回None
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> Tuple[list[User], int]:
        """
        列出用户
        
        Args:
            skip: 跳过数量
            limit: 限制数量
            active_only: 是否只返回活跃用户
            
        Returns:
            Tuple[list[User], int]: 用户列表和总数
        """
        query = self.db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total
