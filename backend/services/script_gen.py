from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.models.script import Script, ScriptStatus, ScriptType, ScriptRevision
from backend.models.project import Project
from backend.core.exceptions import BusinessError, ExternalServiceError
from backend.config import settings

logger = logging.getLogger(__name__)


class ScriptGenerationService:
    """剧本生成服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_script(
        self,
        project_id: int,
        user_id: int,
        prompt: str,
        script_type: ScriptType = ScriptType.SHORT_DRAMA,
        episode_number: int = 1,
        total_episodes: int = 1,
        target_duration: int = 60,
        characters: Optional[List[Dict]] = None,
        settings: Optional[List[Dict]] = None,
        tone: str = "dramatic",
        style: str = "cinematic",
        language: str = "zh",
    ) -> Script:
        """
        生成剧本
        
        Args:
            project_id: 项目ID
            user_id: 用户ID
            prompt: 生成提示词
            script_type: 剧本类型
            episode_number: 集数
            total_episodes: 总集数
            target_duration: 目标时长（秒）
            characters: 角色列表
            settings: 场景设置
            tone: 语气
            style: 风格
            language: 语言
            
        Returns:
            Script: 生成的剧本对象
            
        Raises:
            BusinessError: 业务逻辑错误
            ExternalServiceError: 外部服务错误
        """
        try:
            # 验证项目存在且用户有权限
            project = self.db.query(Project).filter(
                Project.id == project_id,
                Project.owner_id == user_id,
            ).first()
            
            if not project:
                raise BusinessError("Project not found or access denied")
            
            # 检查项目状态
            if not project.can_generate:
                raise BusinessError(f"Project is in {project.status} state, cannot generate script")
            
            # 创建剧本记录
            script = Script(
                title=f"{project.name} - Episode {episode_number}",
                description=f"AI-generated script for {project.name}",
                type=script_type,
                status=ScriptStatus.GENERATING,
                project_id=project_id,
                author_id=user_id,
                episode_number=episode_number,
                total_episodes=total_episodes,
                target_duration=target_duration,
                characters=characters or [],
                settings=settings or [],
                tone=tone,
                style=style,
                language=language,
                prompt=prompt,
                llm_model=settings.llm_provider,
                llm_config={
                    "provider": settings.llm_provider,
                    "model": self._get_llm_model(),
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
                created_at=datetime.utcnow(),
            )
            
            self.db.add(script)
            self.db.commit()
            self.db.refresh(script)
            
            logger.info(f"Started script generation: script_id={script.id}, project_id={project_id}")
            
            # 异步生成剧本内容
            # 这里应该触发Celery任务，但为了简化，我们直接调用
            try:
                self._generate_script_content(script)
            except Exception as e:
                logger.error(f"Script generation failed: {e}")
                script.status = ScriptStatus.DRAFT
                script.error_message = str(e)
                self.db.commit()
                raise ExternalServiceError("LLM service", str(e))
            
            return script
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during script generation: {e}")
            raise BusinessError("Database error occurred")
        except (BusinessError, ExternalServiceError):
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during script generation: {e}")
            raise BusinessError("Unexpected error occurred")
    
    def _generate_script_content(self, script: Script) -> None:
        """
        生成剧本内容
        
        Args:
            script: 剧本对象
        """
        # 根据配置选择LLM提供商
        if settings.llm_provider == "openai":
            content, structured_content = self._generate_with_openai(script)
        elif settings.llm_provider == "anthropic":
            content, structured_content = self._generate_with_anthropic(script)
        elif settings.llm_provider == "local":
            content, structured_content = self._generate_with_local_llm(script)
        else:
            # 默认使用模拟数据
            content, structured_content = self._generate_mock_content(script)
        
        # 更新剧本
        script.content = content
        script.structured_content = structured_content
        script.status = ScriptStatus.COMPLETED
        script.generated_at = datetime.utcnow()
        script.estimated_duration = self._estimate_duration(content)
        
        self.db.commit()
        logger.info(f"Script generation completed: script_id={script.id}")
    
    def _generate_with_openai(self, script: Script) -> tuple[str, Dict]:
        """使用OpenAI生成剧本"""
        # 这里应该调用OpenAI API
        # 由于需要API密钥，暂时返回模拟数据
        return self._generate_mock_content(script)
    
    def _generate_with_anthropic(self, script: Script) -> tuple[str, Dict]:
        """使用Anthropic生成剧本"""
        # 这里应该调用Anthropic API
        return self._generate_mock_content(script)
    
    def _generate_with_local_llm(self, script: Script) -> tuple[str, Dict]:
        """使用本地LLM生成剧本"""
        # 这里应该调用本地LLM（如Ollama）
        return self._generate_mock_content(script)
    
    def _generate_mock_content(self, script: Script) -> tuple[str, Dict]:
        """生成模拟剧本内容（用于开发和测试）"""
        title = script.title or "Untitled Script"
        
        content = f"""# {title}

## 剧本信息
- 类型: {script.type.value}
- 集数: {script.episode_number}/{script.total_episodes}
- 目标时长: {script.target_duration}秒
- 风格: {script.style}
- 语气: {script.tone}

## 场景1: 开场
**时间**: 白天
**地点**: 城市街道
**人物**: 主角

（开场音乐起）
主角走在繁忙的街道上，表情若有所思。

主角（独白）：
"在这个充满可能性的世界里，每一个选择都像是一扇门..."

## 场景2: 冲突
**时间**: 傍晚
**地点**: 咖啡厅
**人物**: 主角，配角

配角坐在窗边，看到主角进来，招手示意。

配角：
"你终于来了，我有个重要的消息要告诉你。"

主角��坐下）：
"什么事这么紧急？"

## 场景3: 高潮
**时间**: 夜晚
**地点**: 天台
**人物**: 主角

主角站在天台上，看着城市的夜景，做出决定。

主角（坚定地）：
"是时候改变一切了。"

## 场景4: 结局
**时间**: 黎明
**地点**: 公园
**人物**: 主角

主角在公园里散步，脸上露出微笑，新的开始。

（音乐渐强，画面淡出）

## 结束
"""
        
        structured_content = {
            "metadata": {
                "title": title,
                "type": script.type.value,
                "episode": script.episode_number,
                "total_episodes": script.total_episodes,
                "target_duration": script.target_duration,
                "style": script.style,
                "tone": script.tone,
                "language": script.language,
            },
            "scenes": [
                {
                    "scene_number": 1,
                    "title": "开场",
                    "time_of_day": "白天",
                    "location": "城市街道",
                    "characters": ["主角"],
                    "description": "主角走在繁忙的街道上，表情若有所思",
                    "dialogue": [
                        {
                            "character": "主角",
                            "type": "独白",
                            "content": "在这个充满可能性的世界里，每一个选择都像是一扇门..."
                        }
                    ],
                    "estimated_duration": 15,
                },
                {
                    "scene_number": 2,
                    "title": "冲突",
                    "time_of_day": "傍晚",
                    "location": "咖啡厅",
                    "characters": ["主角", "配角"],
                    "description": "配角坐在窗边，看到主角进来，招手示意",
                    "dialogue": [
                        {
                            "character": "配角",
                            "type": "对话",
                            "content": "你终于来了，我有个重要的消息要告诉你。"
                        },
                        {
                            "character": "主角",
                            "type": "对话",
                            "content": "什么事这么紧急？"
                        }
                    ],
                    "estimated_duration": 20,
                },
                {
                    "scene_number": 3,
                    "title": "高潮",
                    "time_of_day": "夜晚",
                    "location": "天台",
                    "characters": ["主角"],
                    "description": "主角站在天台上，看着城市的夜景，做出决定",
                    "dialogue": [
                        {
                            "character": "主角",
                            "type": "独白",
                            "content": "是时候改变一切了。"
                        }
                    ],
                    "estimated_duration": 10,
                },
                {
                    "scene_number": 4,
                    "title": "结局",
                    "time_of_day": "黎明",
                    "location": "公园",
                    "characters": ["主角"],
                    "description": "主角在公园里散步，脸上露出微笑，新的开始",
                    "dialogue": [],
                    "estimated_duration": 15,
                }
            ],
            "total_scenes": 4,
            "total_estimated_duration": 60,
        }
        
        return content, structured_content
    
    def _estimate_duration(self, content: str) -> float:
        """
        估算剧本时长
        
        Args:
            content: 剧本内容
            
        Returns:
            float: 估算时长（秒）
        """
        # 简单的估算：每100字约10秒
        word_count = len(content.split())
        return min(word_count * 0.1, 300)  # 最多5分钟
    
    def _get_llm_model(self) -> str:
        """获取当前配置的LLM模型"""
        if settings.llm_provider == "openai":
            return settings.openai_llm_model
        elif settings.llm_provider == "anthropic":
            return settings.anthropic_model
        elif settings.llm_provider == "local":
            return settings.local_llm_model
        return "mock"
    
    def get_script(self, script_id: int, user_id: int) -> Optional[Script]:
        """
        获取剧本详情
        
        Args:
            script_id: 剧本ID
            user_id: 用户ID
            
        Returns:
            Optional[Script]: 剧本对象，如果不存在或无权访问则返回None
        """
        try:
            script = self.db.query(Script).filter(
                Script.id == script_id,
                Script.author_id == user_id,
            ).first()
            
            return script
            
        except Exception as e:
            logger.error(f"Failed to get script: {e}")
            return None
    
    def list_scripts(
        self,
        user_id: int,
        project_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ScriptStatus] = None,
    ) -> tuple[List[Script], int]:
        """
        列出剧本
        
        Args:
            user_id: 用户ID
            project_id: 项目ID（可选）
            skip: 跳过数量
            limit: 限制数量
            status: 状态过滤（可选）
            
        Returns:
            tuple[List[Script], int]: 剧本列表和总数
        """
        try:
            query = self.db.query(Script).filter(Script.author_id == user_id)
            
            if project_id:
                query = query.filter(Script.project_id == project_id)
            
            if status:
                query = query.filter(Script.status == status)
            
            total = query.count()
            scripts = query.order_by(Script.created_at.desc()).offset(skip).limit(limit).all()
            
            return scripts, total
            
        except Exception as e:
            logger.error(f"Failed to list scripts: {e}")
            return [], 0
    
    def update_script(
        self,
        script_id: int,
        user_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        structured_content: Optional[Dict] = None,
    ) -> Optional[Script]:
        """
        更新剧本
        
        Args:
            script_id: 剧本ID
            user_id: 用户ID
            title: 标题（可选）
            content: 内容（可选）
            structured_content: 结构化内容（可选）
            
        Returns:
            Optional[Script]: 更新后的剧本对象
        """
        try:
            script = self.get_script(script_id, user_id)
            if not script:
                return None
            
            if title:
                script.title = title
            
            if content:
                script.content = content
                script.estimated_duration = self._estimate_duration(content)
            
            if structured_content:
                script.structured_content = structured_content
            
            script.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(script)
            
            logger.info(f"Script updated: script_id={script.id}")
            return script
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during script update: {e}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during script update: {e}")
            return None
    
    def create_revision(
        self,
        script_id: int,
        user_id: int,
        content: str,
        structured_content: Dict,
        changes: str,
        feedback: Optional[str] = None,
    ) -> Optional[ScriptRevision]:
        """
        创建剧本修订
        
        Args:
            script_id: 剧本ID
            user_id: 用户ID
            content: 修订内容
            structured_content: 结构化内容
            changes: 变更说明
            feedback: 反馈意见（可选）
            
        Returns:
            Optional[ScriptRevision]: 修订记录
        """
        try:
            script = self.get_script(script_id, user_id)
            if not script:
                return None
            
            # 获取当前修订号
            current_revision = self.db.query(ScriptRevision).filter(
                ScriptRevision.script_id == script_id,
            ).order_by(ScriptRevision.revision_number.desc()).first()
            
            revision_number = 1
            if current_revision:
                revision_number = current_revision.revision_number + 1
            
            # 创建修订记录
            revision = ScriptRevision(
                script_id=script_id,
                revision_number=revision_number,
                content=content,
                structured_content=structured_content,
                changes=changes,
                feedback=feedback,
                revised_by_id=user_id,
                created_at=datetime.utcnow(),
            )
            
            self.db.add(revision)
            self.db.commit()
            self.db.refresh(revision)
            
            # 更新剧本状态
            script.status = ScriptStatus.REVISING
            script.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Script revision created: script_id={script_id}, revision={revision_number}")
            return revision
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during revision creation: {e}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during revision creation: {e}")
            return None
    
    def approve_script(self, script_id: int, user_id: int) -> Optional[Script]:
        """
        批准剧本
        
        Args:
            script_id: 剧本ID
            user_id: 用户ID
            
        Returns:
            Optional[Script]: 批准后的剧本对象
        """
        try:
            script = self.get_script(script_id, user_id)
            if not script:
                return None
            
            script.status = ScriptStatus.APPROVED
            script.approved_at = datetime.utcnow()
            script.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(script)
            
            logger.info(f"Script approved: script_id={script.id}")
            return script
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during script approval: {e}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during script approval: {e}")
            return None
    
    def delete_script(self, script_id: int, user_id: int) -> bool:
        """
        删除剧本
        
        Args:
            script_id: 剧本ID
            user_id: 用户ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            script = self.get_script(script_id, user_id)
            if not script:
                return False
            
            self.db.delete(script)
            self.db.commit()
            
            logger.info(f"Script deleted: script_id={script_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during script deletion: {e}")
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during script deletion: {e}")
            return False
