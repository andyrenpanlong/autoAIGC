from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging
import secrets

from backend.config import settings

logger = logging.getLogger(__name__)

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 密码是否匹配
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    获取密码哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希密码
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 令牌数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 令牌数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT刷新令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        Optional[Dict]: 解码后的令牌数据，如果无效则返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码JWT令牌（不验证过期）
    
    Args:
        token: JWT令牌
        
    Returns:
        Optional[Dict]: 解码后的令牌数据
    """
    try:
        # 设置verify_exp=False来跳过过期验证
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        return payload
    except JWTError as e:
        logger.error(f"Token decoding failed: {e}")
        return None


def generate_api_key() -> str:
    """
    生成API密钥
    
    Returns:
        str: 生成的API密钥
    """
    return secrets.token_urlsafe(32)


def generate_random_password(length: int = 12) -> str:
    """
    生成随机密码
    
    Args:
        length: 密码长度
        
    Returns:
        str: 随机密码
    """
    import string
    import random
    
    # 定义字符集
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    
    # 确保密码包含至少一个大写字母、一个小写字母、一个数字和一个特殊字符
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*"),
    ]
    
    # 添加剩余字符
    password += [random.choice(characters) for _ in range(length - 4)]
    
    # 随机打乱
    random.shuffle(password)
    
    return "".join(password)


def hash_api_key(api_key: str) -> str:
    """
    哈希API密钥
    
    Args:
        api_key: API密钥
        
    Returns:
        str: 哈希后的API密钥
    """
    return pwd_context.hash(api_key)


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """
    验证API密钥
    
    Args:
        plain_api_key: 明文API密钥
        hashed_api_key: 哈希API密钥
        
    Returns:
        bool: API密钥是否匹配
    """
    return verify_password(plain_api_key, hashed_api_key)


def create_password_reset_token(email: str) -> str:
    """
    创建密码重置令牌
    
    Args:
        email: 用户邮箱
        
    Returns:
        str: 密码重置令牌
    """
    # 重置令牌有效期为1小时
    expire = datetime.utcnow() + timedelta(hours=1)
    
    to_encode = {
        "sub": email,
        "exp": expire,
        "type": "password_reset",
    }
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    验证密码重置令牌
    
    Args:
        token: 密码重置令牌
        
    Returns:
        Optional[str]: 用户邮箱，如果令牌无效则返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "password_reset":
            return None
        
        return payload.get("sub")
    except JWTError:
        return None


def create_email_verification_token(email: str) -> str:
    """
    创建邮箱验证令牌
    
    Args:
        email: 用户邮箱
        
    Returns:
        str: 邮箱验证令牌
    """
    # 验证令牌有效期为24小时
    expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode = {
        "sub": email,
        "exp": expire,
        "type": "email_verification",
    }
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_email_verification_token(token: str) -> Optional[str]:
    """
    验证邮箱验证令牌
    
    Args:
        token: 邮箱验证令牌
        
    Returns:
        Optional[str]: 用户邮箱，如果令牌无效则返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "email_verification":
            return None
        
        return payload.get("sub")
    except JWTError:
        return None


def sanitize_input(input_string: str) -> str:
    """
    清理用户输入，防止XSS攻击
    
    Args:
        input_string: 用户输入字符串
        
    Returns:
        str: 清理后的字符串
    """
    import html
    
    # 转义HTML特殊字符
    sanitized = html.escape(input_string)
    
    # 移除危险字符
    dangerous_patterns = [
        "<script", "</script>", "javascript:", "onload=", "onerror=",
        "onclick=", "onmouseover=", "eval(", "document.cookie",
    ]
    
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern, "")
    
    return sanitized.strip()


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    验证密码强度
    
    Args:
        password: 密码
        
    Returns:
        Dict: 验证结果
    """
    import re
    
    result = {
        "is_valid": True,
        "errors": [],
        "score": 0,  # 0-100分
    }
    
    # 检查长度
    if len(password) < 8:
        result["is_valid"] = False
        result["errors"].append("Password must be at least 8 characters long")
    else:
        result["score"] += 20
    
    # 检查大写字母
    if not re.search(r"[A-Z]", password):
        result["errors"].append("Password must contain at least one uppercase letter")
    else:
        result["score"] += 20
    
    # 检查小写字母
    if not re.search(r"[a-z]", password):
        result["errors"].append("Password must contain at least one lowercase letter")
    else:
        result["score"] += 20
    
    # 检查数字
    if not re.search(r"\d", password):
        result["errors"].append("Password must contain at least one number")
    else:
        result["score"] += 20
    
    # 检查特殊字符
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        result["errors"].append("Password must contain at least one special character")
    else:
        result["score"] += 20
    
    # 如果有错误，标记为无效
    if result["errors"]:
        result["is_valid"] = False
    
    return result
