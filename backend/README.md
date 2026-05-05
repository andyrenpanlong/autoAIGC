# AI Video Generation Platform - Backend

基于FastAPI的AI视频生成平台后端服务，支持剧本生成、分镜脚本、多模型视频生成和并发处理。

## 功能特性

- ✅ 用户认证与项目管理
- ✅ 智能剧本生成（LLM集成）
- ✅ 分镜脚本自动化
- ✅ 多模型视频生成（本地+云端）
- ✅ 并发批量生成
- ✅ 任务队列与进度跟踪

## 技术栈

- **框架**: FastAPI + Python 3.12+
- **数据库**: PostgreSQL + SQLAlchemy
- **任务队列**: Celery + Redis
- **认证**: JWT + OAuth2
- **文件存储**: MinIO / S3
- **模型**: LTX 2.3, Stable Diffusion, OpenAI API等

## 快速开始

### 1. 环境准备

```bash
# 安装Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件配置数据库、Redis、API密钥等。

### 3. 数据库初始化

```bash
# 创建数据库迁移
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

### 4. 启动服务

```bash
# 开发模式
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式（使用Gunicorn）
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5. 启动Celery Worker

```bash
# 启动Celery worker
celery -A backend.workers.celery_app worker --loglevel=info

# 启动Celery beat（定时任务）
celery -A backend.workers.celery_app beat --loglevel=info
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── api/                    # API路由
│   ├── v1/                # API版本1
│   │   ├── auth.py        # 认证相关
│   │   ├── projects.py    # 项目管理
│   │   ├── scripts.py     # 剧本生成
│   │   ├── storyboards.py # 分镜脚本
│   │   └── videos.py      # 视频生成
│   └── dependencies.py    # 依赖注入
├── core/                  # 核心模块
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接
│   ├── security.py       # 安全相关
│   └── exceptions.py     # 异常处理
├── models/               # 数据模型
│   ├── user.py          # 用户模型
│   ├── project.py       # 项目模型
│   ├── script.py        # 剧本模型
│   ├── storyboard.py    # 分镜模型
│   └── video.py         # 视频模型
├── services/            # 业务服务
│   ├── auth.py         # 认证服务
│   ├── script_gen.py   # 剧本生成服务
│   ├── storyboard_gen.py # 分镜生成服务
│   ├── video_gen.py    # 视频生成服务
│   └── task_queue.py   # 任务队列服务
├── workers/            # Celery任务
│   ├── celery_app.py  # Celery应用
│   ├── tasks.py       # 异步任务
│   └── schedules.py   # 定时任务
├── schemas/           # Pydantic模式
├── utils/             # 工具函数
├── alembic/           # 数据库迁移
├── tests/             # 测试文件
├── main.py           # 应用入口
└── .env.example      # 环境变量示例
```

## 模型集成

### 本地模型
- **LTX 2.3**: 开源视频生成模型
- **Stable Diffusion**: 图像生成
- **ControlNet**: 图像控制
- **AnimateDiff**: 图像转视频

### 云端API
- **OpenAI Sora**: 文生视频
- **Runway ML**: 视频生成与编辑
- **Pika Labs**: 快速视频生成
- **Google Veo**: 高质量视频生成
- **Stability AI**: 图像生成

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t ai-video-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env ai-video-backend
```

### Kubernetes部署

参考 `k8s/` 目录下的配置文件。

## 开发指南

### 代码规范
- 使用Black进行代码格式化
- 使用Ruff进行代码检查
- 使用MyPy进行类型检查

### 测试
```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=backend tests/
```

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具

## 许可证

MIT License
