from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from backend.config import settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # 连接前检查连接是否有效
    echo=settings.debug,  # 调试模式下输出SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的依赖函数
    
    Yields:
        Session: SQLAlchemy数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    初始化数据库，创建所有表
    
    注意：在生产环境中应该使用Alembic迁移
    """
    try:
        # 导入所有模型以确保它们被注册
        from backend.models import user, project, script, storyboard, video
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def drop_db() -> None:
    """
    删除所有表（仅用于开发和测试）
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


def check_db_connection() -> bool:
    """
    检查数据库连接是否正常
    
    Returns:
        bool: 连接是否成功
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# 数据库工具函数
def get_table_count(table_name: str) -> int:
    """
    获取指定表的记录数量
    
    Args:
        table_name: 表名
        
    Returns:
        int: 记录数量
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            return result.scalar()
    except Exception as e:
        logger.error(f"Failed to get count for table {table_name}: {e}")
        return 0


def execute_raw_sql(sql: str, params: dict = None) -> list:
    """
    执行原始SQL查询
    
    Args:
        sql: SQL语句
        params: 参数
        
    Returns:
        list: 查询结果
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(sql, params or {})
            return [dict(row) for row in result]
    except Exception as e:
        logger.error(f"Failed to execute SQL: {e}")
        raise


# 数据库会话上下文管理器
class DatabaseSession:
    """数据库会话上下文管理器"""
    
    def __init__(self):
        self.db = None
    
    def __enter__(self) -> Session:
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            if exc_type is not None:
                self.db.rollback()
            else:
                self.db.commit()
            self.db.close()
