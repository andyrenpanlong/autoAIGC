#!/bin/bash

# AI视频生成平台 - 快速启动脚本
# 作者: AI Video Platform Team
# 版本: 1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 $1 未安装，请先安装"
        exit 1
    fi
}

# 显示横幅
show_banner() {
    echo -e "${BLUE}"
    echo "================================================"
    echo "      AI视频生成平台 - 快速启动脚本"
    echo "================================================"
    echo -e "${NC}"
    echo "版本: 1.0.0"
    echo "环境: $MODE"
    echo ""
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
        log_success "Docker 已安装 ($DOCKER_VERSION)"
    else
        log_warning "Docker 未安装，将使用开发模式"
        USE_DOCKER=false
    fi
    
    # 检查Docker Compose
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose 已安装"
    elif docker compose version &> /dev/null; then
        log_success "Docker Compose (插件) 已安装"
    else
        log_warning "Docker Compose 未安装"
        USE_DOCKER=false
    fi
    
    # 检查Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js 已安装 ($NODE_VERSION)"
    else
        log_warning "Node.js 未安装"
    fi
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        log_success "Python 已安装 ($PYTHON_VERSION)"
    else
        log_warning "Python 3 未安装"
    fi
    
    # 检查Poetry
    if command -v poetry &> /dev/null; then
        log_success "Poetry 已安装"
    else
        log_warning "Poetry 未安装"
    fi
}

# 设置环境
setup_environment() {
    log_info "设置环境..."
    
    # 检查.env文件
    if [ ! -f .env ]; then
        log_warning ".env 文件不存在，从示例文件创建"
        if [ -f .env.example ]; then
            cp .env.example .env
            log_success "已创建 .env 文件，请编辑配置"
        else
            log_error ".env.example 文件不存在"
            exit 1
        fi
    else
        log_success ".env 文件已存在"
    fi
    
    # 创建必要的目录
    mkdir -p backend/logs
    mkdir -p backend/uploads
    mkdir -p backend/cache
    mkdir -p backend/models
    mkdir -p frontend/public
    log_success "目录结构已创建"
}

# 开发模式启动
start_development() {
    log_info "启动开发模式..."
    
    # 启动后端
    log_info "启动后端服务..."
    cd backend
    if [ ! -d ".venv" ]; then
        log_info "创建Python虚拟环境..."
        poetry install
    fi
    
    # 启动后端服务器（后台运行）
    log_info "启动FastAPI服务器..."
    poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # 启动前端
    log_info "启动前端服务..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        log_info "安装Node.js依赖..."
        npm install
    fi
    
    # 启动前端服务器（后台运行）
    log_info "启动Next.js服务器..."
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # 启动Redis（如果Docker可用）
    if [ "$USE_DOCKER" = true ]; then
        log_info "启动Redis..."
        docker run -d -p 6379:6379 --name ai-video-redis redis:alpine
    fi
    
    # 启动PostgreSQL（如果Docker可用）
    if [ "$USE_DOCKER" = true ]; then
        log_info "启动PostgreSQL..."
        docker run -d -p 5432:5432 \
            -e POSTGRES_DB=ai_video_db \
            -e POSTGRES_USER=postgres \
            -e POSTGRES_PASSWORD=password \
            --name ai-video-postgres \
            postgres:alpine
    fi
    
    # 保存PID文件
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    log_success "开发环境已启动！"
    echo ""
    echo "访问以下地址："
    echo "前端: http://localhost:3000"
    echo "后端API: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
    echo ""
    echo "按 Ctrl+C 停止所有服务"
    
    # 等待用户中断
    wait
}

# Docker模式启动
start_docker() {
    log_info "启动Docker模式..."
    
    # 检查Docker Compose文件
    if [ ! -f docker-compose.yml ]; then
        log_error "docker-compose.yml 文件不存在"
        exit 1
    fi
    
    # 启动服务
    log_info "启动Docker Compose服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    log_info "检查服务状态..."
    docker-compose ps
    
    log_success "Docker环境已启动！"
    echo ""
    echo "访问以下地址："
    echo "前端: http://localhost:3000"
    echo "后端API: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
    echo "MinIO控制台: http://localhost:9001 (用户名: minioadmin, 密码: minioadmin)"
    echo "Grafana监控: http://localhost:3001 (用户名: admin, 密码: admin)"
    echo ""
    echo "使用以下命令查看日志："
    echo "  docker-compose logs -f"
    echo "使用以下命令停止服务："
    echo "  docker-compose down"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    # 停止开发模式进程
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            log_success "后端服务已停止"
        fi
        rm -f .backend.pid
    fi
    
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            log_success "前端服务已停止"
        fi
        rm -f .frontend.pid
    fi
    
    # 停止Docker容器
    if [ "$USE_DOCKER" = true ]; then
        docker stop ai-video-redis ai-video-postgres 2>/dev/null || true
        docker rm ai-video-redis ai-video-postgres 2>/dev/null || true
        log_success "Docker容器已停止"
    fi
    
    log_success "所有服务已停止"
}

# 清理环境
cleanup() {
    log_info "清理环境..."
    
    # 删除PID文件
    rm -f .backend.pid .frontend.pid
    
    # 停止Docker Compose
    if [ -f docker-compose.yml ] && [ "$USE_DOCKER" = true ]; then
        docker-compose down -v
    fi
    
    log_success "环��已清理"
}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start      启动服务（默认）"
    echo "  stop       停止服务"
    echo "  restart    重启服务"
    echo "  status     显示服务状态"
    echo "  clean      清理环境"
    echo "  help       显示此帮助信息"
    echo ""
    echo "模式:"
    echo "  -d, --docker    使用Docker模式（默认）"
    echo "  -D, --dev       使用开发模式"
    echo ""
    echo "示例:"
    echo "  $0 start           # 使用Docker模式启动"
    echo "  $0 start --dev     # 使用开发模式启动"
    echo "  $0 stop            # 停止服务"
    echo "  $0 status          # 显示状态"
}

# 显示状态
show_status() {
    log_info "服务状态："
    
    # 检查后端
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "后端API: ${GREEN}运行中${NC} (http://localhost:8000)"
    else
        echo -e "后端API: ${RED}未运行${NC}"
    fi
    
    # 检查前端
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "前端应用: ${GREEN}运行中${NC} (http://localhost:3000)"
    else
        echo -e "前端应用: ${RED}未运行${NC}"
    fi
    
    # 检查Redis
    if docker ps | grep -q ai-video-redis; then
        echo -e "Redis: ${GREEN}运行中${NC}"
    elif redis-cli ping 2>/dev/null | grep -q PONG; then
        echo -e "Redis: ${GREEN}运行中${NC}"
    else
        echo -e "Redis: ${RED}未运行${NC}"
    fi
    
    # 检查PostgreSQL
    if docker ps | grep -q ai-video-postgres; then
        echo -e "PostgreSQL: ${GREEN}运行中${NC}"
    elif pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        echo -e "PostgreSQL: ${GREEN}运行中${NC}"
    else
        echo -e "PostgreSQL: ${RED}未运行${NC}"
    fi
    
    # 检查Docker Compose
    if [ -f docker-compose.yml ]; then
        echo ""
        echo "Docker Compose 服务："
        docker-compose ps 2>/dev/null || echo "Docker Compose 未运行"
    fi
}

# 主函数
main() {
    # 默认值
    MODE="docker"
    USE_DOCKER=true
    ACTION="start"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            start|stop|restart|status|clean|help)
                ACTION=$1
                shift
                ;;
            -d|--docker)
                MODE="docker"
                USE_DOCKER=true
                shift
                ;;
            -D|--dev)
                MODE="development"
                USE_DOCKER=false
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 显示横幅
    show_banner
    
    # 执行操作
    case $ACTION in
        start)
            check_dependencies
            setup_environment
            if [ "$MODE" = "docker" ] && [ "$USE_DOCKER" = true ]; then
                start_docker
            else
                start_development
            fi
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            if [ "$MODE" = "docker" ] && [ "$USE_DOCKER" = true ]; then
                start_docker
            else
                start_development
            fi
            ;;
        status)
            show_status
            ;;
        clean)
            cleanup
            ;;
        help)
            show_help
            ;;
    esac
}

# 捕获Ctrl+C
trap 'log_info "接收到中断信号，停止服务..."; stop_services; exit 0' INT

# 运行主函数
main "$@"
