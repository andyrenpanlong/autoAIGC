# AI视频生成平台 - 快速开始指南

## 系统要求

### 最低配置
- **操作系统**: macOS 10.15+, Ubuntu 20.04+, Windows 10+ (WSL2)
- **内存**: 8GB RAM
- **存储**: 20GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置（用于本地模型）
- **操作系统**: Ubuntu 22.04+ 或 Windows 11
- **CPU**: Intel i7 或 AMD Ryzen 7 以上
- **内存**: 16GB RAM 或更多
- **GPU**: NVIDIA GPU with 8GB+ VRAM (用于本地模型加速)
- **存储**: 100GB SSD 可用空间

## 安装方法

### 方法一：Docker快速启动（推荐）

#### 1. 安装Docker和Docker Compose
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# macOS
brew install docker docker-compose

# Windows
# 从官网下载Docker Desktop: https://www.docker.com/products/docker-desktop
```

#### 2. 下载项目
```bash
git clone https://github.com/yourusername/ai-video-platform.git
cd ai-video-platform
```

#### 3. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件（根据需要修改）
# nano .env 或 vim .env
```

#### 4. 启动服务
```bash
# 使用快速启动脚本
chmod +x start.sh
./start.sh start --docker

# 或直接使用docker-compose
docker-compose up -d
```

#### 5. 访问应用
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- MinIO控制台: http://localhost:9001 (用户名: minioadmin, 密码: minioadmin)

### 方法二：手动安装（开发环境）

#### 1. 安装后端依赖
```bash
# 进入后端目录
cd backend

# 安装Python 3.12+
# Ubuntu/Debian
sudo apt install python3.12 python3.12-venv python3.12-dev

# macOS
brew install python@3.12

# 安装Poetry（Python包管理）
curl -sSL https://install.python-poetry.org | python3 -

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

#### 2. 安装前端依赖
```bash
# 进入前端目录
cd frontend

# 安装Node.js 18+
# 使用nvm（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# 安装依赖
npm install
```

#### 3. 安装数据库和缓存
```bash
# 使用Docker安装PostgreSQL和Redis
docker run -d -p 5432:5432 \
  -e POSTGRES_DB=ai_video_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  --name ai-video-postgres \
  postgres:alpine

docker run -d -p 6379:6379 \
  --name ai-video-redis \
  redis:alpine
```

#### 4. 配置环境
```bash
# 在后端目录创建.env文件
cd backend
cp .env.example .env

# 编辑.env文件，配置数据库连接
# DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_video_db
# REDIS_URL=redis://localhost:6379/0
```

#### 5. 初始化数据库
```bash
# 在后端目录执行
alembic upgrade head
```

#### 6. 启动服务
```bash
# 启动后端（在backend目录）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（在frontend目录，新终端）
npm run dev
```

## 首次使用

### 1. 注册账号
1. 访问 http://localhost:3000
2. 点击"注册"按钮
3. 输入邮箱、用户名和密码
4. 完成注册并登录

### 2. 配置API密钥（可选）
1. 登录后进入"设置"页面
2. 在"API密钥"部分配置：
   - OpenAI API密钥（用于剧本生成）
   - 其他AI服务API密钥（按需配置）

### 3. 创建第一个项目
1. 点击"创建新项目"
2. 输入项目名称和描述
3. 选择项目类型（短剧、广告等）
4. 配置项目设置

### 4. 生成第一个剧本
1. 在项目页面点击"生成剧本"
2. 输入剧本提示词，例如：
   ```
   一个30秒的咖啡广告，展示清晨在城市中忙碌的年轻人，
   通过一杯咖啡找到片刻宁静，风格温馨治愈。
   ```
3. 点击"生成"按钮
4. 等待AI生成剧本（约30秒）

### 5. 生成分镜脚本
1. 在剧本页面点击"生成分镜"
2. 调整分镜设置（镜头类型、角度等）
3. 点击"生成"按钮
4. 预览生成的分镜脚本

### 6. 生成视频（需要模型配置）
1. 在分镜页面点击"生成视频"
2. 选择视频模型（本地或云端）
3. 配置视频参数（分辨率、时长等）
4. 点击"开始生成"
5. 等待视频生成完成（时间取决于模型）

## 配置说明

### 环境变量详解

#### 必需配置
```bash
# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_video_db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT密钥（生产环境必须修改）
SECRET_KEY=your-secret-key-change-in-production
```

#### AI服务配置（按需）
```bash
# OpenAI（用于剧本生成）
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 其他视频生成服务
RUNWAY_API_KEY=your-runway-api-key
PIKA_API_KEY=your-pika-api-key
GOOGLE_API_KEY=your-google-api-key
```

#### 模型配置
```bash
# 使用本地模型（需要GPU）
ENABLE_LOCAL_MODELS=true
LTX_MODEL_PATH=./models/ltx-2.3

# 或使用云端API
DEFAULT_MODEL_PROVIDER=openai
```

### 存储配置

#### 本地存储
```bash
STORAGE_TYPE=local
UPLOAD_DIR=./uploads
```

#### MinIO存储（推荐）
```bash
STORAGE_TYPE=minio
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=ai-videos
```

#### AWS S3存储
```bash
STORAGE_TYPE=s3
S3_REGION=us-east-1
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查PostgreSQL是否运行
docker ps | grep postgres

# 检查连接信息
echo $DATABASE_URL

# 手动测试连接
psql -h localhost -p 5432 -U postgres -d ai_video_db
```

#### 2. Redis连接失败
```bash
# 检查Redis是否运行
docker ps | grep redis

# 测试Redis连接
redis-cli ping
```

#### 3. 前端无法访问后端API
```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查CORS配置
# 确保CORS_ORIGINS包含前端地址
```

#### 4. 模型加载失败
```bash
# 检查模型文件是否存在
ls -la ./models/

# 检查GPU驱动（如果使用本地模型）
nvidia-smi

# 检查CUDA版本
python -c "import torch; print(torch.cuda.is_available())"
```

### 日志查看

#### Docker容器日志
```bash
# 查看所有容器日志
docker-compose logs

# 查看特定容器日志
docker-compose logs backend
docker-compose logs frontend

# 实时查看日志
docker-compose logs -f
```

#### 应用日志
```bash
# 后端日志
tail -f backend/logs/app.log

# 前端日志（开发模式）
# 在浏览器开发者工具中查看Console和Network标签
```

## 性能优化

### 开发环境优化
```bash
# 减少内存使用
# 在.env中配置
WORKERS=2
DATABASE_POOL_SIZE=10
MAX_CONCURRENT_TASKS=2
```

### 生产环境优化
```bash
# 增加资源分配
WORKERS=4
DATABASE_POOL_SIZE=20
MAX_CONCURRENT_TASKS=4

# 启用缓存
ENABLE_LOCAL_MODELS=true
LTX_CACHE_DIR=./cache/ltx
```

### GPU优化（如果可用）
```bash
# 启用GPU加速
ENABLE_GPU=true
CUDA_VISIBLE_DEVICES=0

# 调整批处理大小
BATCH_SIZE=2
```

## 安全建议

### 生产环境部署
1. **修改默认密码**：修改所有默认密码和密钥
2. **启用HTTPS**：配置SSL证书
3. **设置防火墙**：限制不必要的端口���问
4. **定期备份**：设置数据库和文件备份
5. **监控告警**：配置系统监控和告警

### 数据安全
1. **加密敏感数据**：API密钥、用户密码等
2. **访问控制**：实施最小权限原则
3. **审计日志**：记录所有重要操作
4. **数据隔离**：多租户数据隔离

## 更新和升级

### 更新代码
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
cd backend && poetry update
cd ../frontend && npm update

# 重启服务
docker-compose down
docker-compose up -d --build
```

### 数据库迁移
```bash
# 应用数据库迁移
cd backend
alembic upgrade head

# 回滚迁移（如果需要）
alembic downgrade -1
```

## 获取帮助

### 文档资源
- [架构设计](docs/architecture.md)
- [API文档](http://localhost:8000/docs)
- [开发指南](docs/development.md)

### 社区支持
- GitHub Issues: 报告问题和功能请求
- GitHub Discussions: 技术讨论和问答
- 邮件列表: 订阅更新和公告

### 商业支持
如需企业级支持、定制开发或培训服务，请联系：
- 邮箱: support@ai-video-platform.com
- 网站: https://ai-video-platform.com

---

**提示**：首次使用建议从"方法一：Docker快速启动"开始，这是最简单快捷的方式。

**注意**：生产环境部署前请仔细阅读安全建议，并进行充分测试。

**开始创作吧！** 🎬✨