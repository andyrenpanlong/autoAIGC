from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AppException(Exception):
    """应用基础异常类"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AppException):
    """认证错误"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(AppException):
    """授权错误"""
    
    def __init__(self, message: str = "Authorization failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class NotFoundError(AppException):
    """资源未找到错误"""
    
    def __init__(self, resource: str = "Resource", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details,
        )


class ValidationError(AppException):
    """验证错误"""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class BusinessError(AppException):
    """业务逻辑错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_ERROR",
            details=details,
        )


class RateLimitError(AppException):
    """速率限制错误"""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_ERROR",
            details=details,
        )


class ExternalServiceError(AppException):
    """外部服务错误"""
    
    def __init__(self, service: str, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{service}: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )


class ModelGenerationError(AppException):
    """模型生成错误"""
    
    def __init__(self, model: str, message: str = "Model generation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{model}: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="MODEL_GENERATION_ERROR",
            details=details,
        )


class InsufficientCreditsError(AppException):
    """积分不足错误"""
    
    def __init__(self, message: str = "Insufficient credits", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            error_code="INSUFFICIENT_CREDITS",
            details=details,
        )


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    创建标准错误响应
    
    Args:
        status_code: HTTP状态码
        error_code: 错误代码
        message: 错误消息
        details: 错误详情
        request_id: 请求ID
        
    Returns:
        Dict: 错误响应字典
    """
    error_response = {
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
        },
        "success": False,
    }
    
    if request_id:
        error_response["request_id"] = request_id
    
    return error_response


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    应用异常处理器
    
    Args:
        request: 请求对象
        exc: 异常实例
        
    Returns:
        JSONResponse: 错误响应
    """
    logger.error(
        f"AppException: {exc.error_code} - {exc.message}",
        extra={
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )
    
    error_response = create_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        request_id=request.state.get("request_id") if hasattr(request.state, "request_id") else None,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    请求验证异常处理器
    
    Args:
        request: 请求对象
        exc: 验证异常
        
    Returns:
        JSONResponse: 错误响应
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(
        f"Validation error: {errors}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )
    
    error_response = create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"errors": errors},
        request_id=request.state.get("request_id") if hasattr(request.state, "request_id") else None,
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response,
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Pydantic验证异常处理器
    
    Args:
        request: 请求对象
        exc: Pydantic验证异常
        
    Returns:
        JSONResponse: 错误响应
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(
        f"Pydantic validation error: {errors}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )
    
    error_response = create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        message="Data validation failed",
        details={"errors": errors},
        request_id=request.state.get("request_id") if hasattr(request.state, "request_id") else None,
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用异常处理器
    
    Args:
        request: 请求对象
        exc: 异常实例
        
    Returns:
        JSONResponse: 错误响应
    """
    logger.exception(
        f"Unhandled exception: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
        },
    )
    
    error_response = create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        details={
            "exception": str(exc),
            "type": type(exc).__name__,
        } if settings.debug else {},
        request_id=request.state.get("request_id") if hasattr(request.state, "request_id") else None,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    设置异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    # 注册应用异常处理器
    app.add_exception_handler(AppException, app_exception_handler)
    
    # 注册验证异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    
    # 注册通用异常处理器（最后注册，作为兜底）
    app.add_exception_handler(Exception, generic_exception_handler)
