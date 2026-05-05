# AI视频生成平台

基于LTX Desktop开源项目的AI视频生成Web平台，支持短剧、广告、社交媒体内容的自动化生成。

## 🎯 项目目标

构建一个完整的AI视频生成平台，解决当前市场痛点：
- **成本高昂**：Runway等平台月费$95+，API调用按秒计费
- **控制力弱**：Sora等平台生成结果难以精确控制
- **本地化限制**：多数平台依赖云端，隐私和数据安全存疑
- **工作流不完整**：缺乏从剧本到成片的完整自动化流程
- **并发限制**：无法批量生成多集内容
- **模型选择单一**：无法灵活切换本地/云端模型

## ✨ 核心功能

### 1. 智能剧本生成系统
- 基于LLM的短剧/广告剧本自动生成
- 支持多集连续剧情生成
- 角色设定与对话生成
- 分集大纲与情节规划

### 2. 分镜脚本自动化
- 剧本转分镜脚本
- 镜头语言建议（景别、角度、运动）
- 时长与节奏规划
- 视觉风格设定

### 3. 多模型视频生成
- **文生图**：Stable Diffusion, DALL-E 3, Midjourney API
- **图生图**：ControlNet, IP-Adapter
- **文生视频**：LTX 2.3, Sora, Runway, Pika, Veo
- **图生视频**：AnimateDiff, Stable Video Diffusion

### 4. 并发批量生成
- 多集并行生成
- 分布式任务队列
- 进度跟踪与错误处理
- 资源优化调度

### 5. 本地化部署
- 支持本地模型运行（需NVIDIA GPU）
- 云端API降级方案
- 数据隐私保护
- 离线工作模式

## 🏗️ 技术架构

### 前端技术栈
- **框架**：Next.js 15 + React 19 + TypeScript
- **UI库**：shadcn/ui + Tailwind CSS
- **状态管理**：Zustand
- **视频处理**：FFmpeg.wasm, Video.js
- **编辑器**：Monaco Editor (剧本编辑)
- **图表**：Recharts

### 后端技术栈
- **框架**：FastAPI + Python 3.12+
- **任务队列**：Celery + Redis
- **数据库**：PostgreSQL + SQLAlchemy
- **文件存储**：MinIO (本地) / S3 (云端)
- **模型管理**：Hugging Face Transformers
- **LLM集成**：OpenAI API, Anthropic, Local LLM (Ollama)

### 模型服务层
- **本地视频模型**：LTX 2.3 (Apache 2.0开源)
- **本地图像模型**：Stable Diffusion XL
- **云端API集成**：
  - OpenAI Sora API
  - Runway ML API
  - Pika Labs API
  - Google Veo API
  - Stability AI API

## 📁 项目结构

```
ai-video-platform/
├── frontend/                 # Next.js前端
│   ├── app/                 # App Router
│   ├── components/          # 可复用组件
│   ├── lib/                 # 工具函数
│   └── styles/              # 样式文件
├── backend/                 # FastAPI后端
│   ├── api/                # API路由
│   ├── core/               # 核心逻辑
│   ├── models/             # 数据模型
│   ├── services/           # 业务服务
│   └── workers/            # Celery任务
├── model-service/          # 模型服务
│   ├── adapters/           # 模型适配器
│   ├── local_models/       # 本地模型管理
│   ├── cloud_apis/         # 云端API集成
│   └── cache/              # 缓存管理
├── docker/                 # Docker配置
├── docs/                   # 文档
└── scripts/                # 部署脚本
```

## 🚀 快速开始

### 1. 环境要求

- **操作系统**：macOS, Linux, Windows (WSL2)
- **Python**：3.12+
- **Node.js**：18+
- **数据库**：PostgreSQL 15+
- **缓存**：Redis 7+
- **GPU**：NVIDIA GPU with 16GB+ VRAM (推荐，用于本地模型)

### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 安装依赖
poetry install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库、API密钥等

# 初始化数据库
alembic upgrade head

# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动Celery worker
celery -A backend.workers.celery_app worker --loglevel=info
```

### 3. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 模型服务设置

```bash
# 进入模型服务目录
cd model-service

# 安装依赖
poetry install

# 下载模型权重
python scripts/download_models.py

# 启动模型服务
python main.py
```

## 📊 数据库设计

### 核心数据模型

1. **用户管理** (User, UserSession)
   - 用户认证与授权
   - API密钥管理
   - 使用限制与配额

2. **项目管理** (Project, ProjectCollaborator)
   - 项目创建与管理
   - 团队协作
   - 项目配置与状态

3. **剧本管理** (Script, ScriptRevision)
   - 剧本生成与编辑
   - 版本控制
   - 结构化数据存储

4. **分镜管理** (Storyboard, StoryboardShot)
   - 分镜脚本生成
   - 镜头规划
   - 视觉风格配置

5. **视频管理** (Video, VideoGenerationJob)
   - 视频生成任务
   - 进度跟踪
   - 文件管理

## 🔧 模型集成

### 本地模型配置

1. **LTX 2.3 配置**
```yaml
model:
  name: "ltx-2.3"
  path: "./models/ltx-2.3"
  cache_dir: "./cache/ltx"
  requirements:
    - cuda: "11.8"
    - vram: "16GB"
    - disk_space: "50GB"
```

2. **Stable Diffusion 配置**
```yaml
model:
  name: "stable-diffusion-xl"
  path: "./models/sdxl"
  cache_dir: "./cache/sd"
  controlnet: true
  ip_adapter: true
```

### 云端API配置

支持多种云端API的灵活切换：
- OpenAI Sora：高质量视频生成
- Runway ML：专业视频编辑
- Pika Labs：快速生成
- Google Veo：最新技术
- Stability AI：图像生成

## 🎨 用户界面

### 主要页面

1. **仪表盘**：项目概览、统计数据
2. **剧本编辑器**：AI辅助剧本创作
3. **分镜生成器**：可视化分镜规划
4. **视频生成器**：多模型视频生成
5. **项目管理**：项目设置与协作
6. **用户设置**：API密钥、偏好设置

### 设计特点

- **现代化UI**：基于shadcn/ui的组件库
- **响应式设计**：支持桌面和移动端
- **暗色模式**：完整的暗色主题支持
- **实时预览**：生成过程实时预览
- **拖拽交互**：直观的拖拽操作

## 🔒 安全特性

- **JWT认证**：安全的用户认证
- **API密钥加密**：用户API密钥安全存储
- **输入验证**：全面的输入验证和清理
- **速率限制**：API调用速率限制
- **CORS配置**：安全的跨域请求
- **数据加密**：敏感数据加密存储

## 📈 性能优化

### 前端优化
- **代码分割**：按需加载组件
- **图片优化**：Next.js Image组件
- **缓存策略**：SWR数据缓存
- **懒加载**：组件和图片懒加载

### 后端优化
- **数据库连接池**：SQLAlchemy连接池
- **Redis缓存**：频繁查询缓存
- **异步任务**：Celery异步处理
- **CDN集成**：静态资源CDN

### 模型优化
- **模型缓存**：常用模型内存缓存
- **批量处理**：支持批量生成
- **GPU优化**：CUDA加速
- **量化压缩**：模型量化减少内存

## 🐳 部署方案

### Docker部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_video_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/ai_video_db
      REDIS_URL: redis://redis:6379/0
    ports:
      - "8000:8000"

  celery:
    build: ./backend
    command: celery -A backend.workers.celery_app worker --loglevel=info
    depends_on:
      - redis
      - backend

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes部署

提供完整的K8s部署配置：
- 命名空间配置
- 服务发现
- 自动扩缩容
- 健康检查
- 日志收集

## 📚 API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点

```
GET    /api/v1/auth/me          # 获取当前用户
POST   /api/v1/auth/login       # 用户登录
POST   /api/v1/auth/register    # 用户注册

GET    /api/v1/projects         # 获取项目列表
POST   /api/v1/projects         # 创建项目
GET    /api/v1/projects/{id}    # 获取项目详情

POST   /api/v1/scripts/generate # 生成剧本
GET    /api/v1/scripts/{id}     # 获取剧本详情

POST   /api/v1/storyboards/generate # 生成分镜
GET    /api/v1/storyboards/{id} # 获取分镜详情

POST   /api/v1/videos/generate  # 生成视频
GET    /api/v1/videos/{id}      # 获取视频详情
GET    /api/v1/videos/{id}/progress # 获取生成进度
```

## 🧪 测试

### 单元测试
```bash
# 后端测试
cd backend
pytest tests/unit/

# 前端测试
cd frontend
npm test
```

### 集成测试
```bash
# 运行完整集成测试
pytest tests/integration/
```

### 性能测试
```bash
# 使用Locust进行性能测试
locust -f tests/performance/locustfile.py
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

### 代码规范
- 使用Black进行Python代码格式化
- 使用Prettier进行前端代码格式化
- 遵循TypeScript严格模式
- 编写单元测试

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [LTX Desktop](https://github.com/Lightricks/LTX-Desktop) - 开源视频生成应用
- [Stable Diffusion](https://github.com/Stability-AI/StableDiffusion) - 开源图像生成模型
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Next.js](https://nextjs.org/) - React框架

## 📞 支持

- 问题反馈：[GitHub Issues](https://github.com/yourusername/ai-video-platform/issues)
- 文档：[项目Wiki](https://github.com/yourusername/ai-video-platform/wiki)
- 讨论：[GitHub Discussions](https://github.com/yourusername/ai-video-platform/discussions)

---

**开始创建令人惊叹的AI视频吧！** 🎬✨