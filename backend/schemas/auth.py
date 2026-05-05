from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from backend.models.user import UserRole, UserPlan


class UserBase(BaseModel):
    """用户基础模式"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_]+$")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator("password")
    def validate_password_strength(cls, v):
        """验证密码强度"""
        import re
        
        errors = []
        
        # 检查长度
        if len(v) < 8:
            errors.append("Password must be at least 8 characters long")
        
        # 检查大写字母
        if not re.search(r"[A-Z]", v):
            errors.append("Password must contain at least one uppercase letter")
        
        # 检查小写字母
        if not re.search(r"[a-z]", v):
            errors.append("Password must contain at least one lowercase letter")
        
        # 检查数字
        if not re.search(r"\d", v):
            errors.append("Password must contain at least one number")
        
        # 检查特殊字符
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            errors.append("Password must contain at least one special character")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return v


class UserUpdate(BaseModel):
    """用户更新模式"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_]+$")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    role: UserRole
    plan: UserPlan
    is_active: bool
    is_verified: bool
    monthly_credits: int
    used_credits: int
    remaining_credits: int
    max_concurrent_jobs: int
    max_video_length: int
    preferred_model: Optional[str]
    default_video_resolution: Optional[str]
    default_video_duration: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """用户详情响应模式（包含敏感信息，仅管理员或用户自己可见）"""
    openai_api_key: Optional[str] = None
    runway_api_key: Optional[str] = None
    pika_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    stability_api_key: Optional[str] = None
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求模式"""
    identifier: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """令牌响应模式"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模式"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求模式"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator("new_password")
    def validate_new_password_strength(cls, v):
        """验证新密码强度"""
        import re
        
        errors = []
        
        # 检查长度
        if len(v) < 8:
            errors.append("Password must be at least 8 characters long")
        
        # 检查大写字母
        if not re.search(r"[A-Z]", v):
            errors.append("Password must contain at least one uppercase letter")
        
        # 检查小写字母
        if not re.search(r"[a-z]", v):
            errors.append("Password must contain at least one lowercase letter")
        
        # 检查数字
        if not re.search(r"\d", v):
            errors.append("Password must contain at least one number")
        
        # 检查特殊字符
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            errors.append("Password must contain at least one special character")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return v


class UpdateProfileRequest(BaseModel):
    """更新资料请求模式"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_]+$")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)


class ResetPasswordRequest(BaseModel):
    """重置密码请求模式"""
    email: EmailStr


class ResetPasswordConfirmRequest(BaseModel):
    """确认重置密码请求模式"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator("new_password")
    def validate_password_strength(cls, v):
        """验证密码强度"""
        import re
        
        errors = []
        
        # 检查长度
        if len(v) < 8:
            errors.append("Password must be at least 8 characters long")
        
        # 检查大写字母
        if not re.search(r"[A-Z]", v):
            errors.append("Password must contain at least one uppercase letter")
        
        # 检查小写字母
        if not re.search(r"[a-z]", v):
            errors.append("Password must contain at least one lowercase letter")
        
        # 检查数字
        if not re.search(r"\d", v):
            errors.append("Password must contain at least one number")
        
        # 检查特殊字符
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            errors.append("Password must contain at least one special character")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return v


class VerifyEmailRequest(BaseModel):
    """验证邮箱请求模式"""
    token: str


class UpdateApiKeysRequest(BaseModel):
    """更新API密钥请求模式"""
    openai_api_key: Optional[str] = None
    runway_api_key: Optional[str] = None
    pika_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    stability_api_key: Optional[str] = None


class UserSessionResponse(BaseModel):
    """用户会话响应模式"""
    id: int
    user_agent: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """用户统计响应模式"""
    total_projects: int
    total_scripts: int
    total_storyboards: int
    total_videos: int
    total_generation_time: float  # 秒
    total_cost: float
    credits_used_this_month: int
    credits_remaining: int


class UserListResponse(BaseModel):
    """用户列表响应模式"""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


class RoleUpdateRequest(BaseModel):
    """角色更新请求模式"""
    role: UserRole


class PlanUpdateRequest(BaseModel):
    """套餐更新请求模式"""
    plan: UserPlan


class CreditsUpdateRequest(BaseModel):
    """积分更新请求模式"""
    monthly_credits: int = Field(..., ge=0)
    used_credits: int = Field(..., ge=0)


class UserSearchRequest(BaseModel):
    """用户搜索请求模式"""
    query: Optional[str] = None
    role: Optional[UserRole] = None
    plan: Optional[UserPlan] = None
    is_active: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    skip: int = 0
    limit: int = 100


class ApiKeyResponse(BaseModel):
    """API密钥响应模式"""
    service: str
    has_key: bool
    last_updated: Optional[datetime]


class ApiKeysResponse(BaseModel):
    """API密钥列表响应模式"""
    keys: List[ApiKeyResponse]
