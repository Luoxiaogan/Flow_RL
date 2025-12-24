#!/bin/bash
# New_Flow_RL Startup Script
# 一键启动所有服务

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo "  New_Flow_RL - Starting Services"
echo "================================================"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed"
    exit 1
fi

# 检查环境变量文件
ENV_FILE="$PROJECT_ROOT/docker/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Warning: .env file not found"
    echo "Copying from .env.example..."
    cp "$PROJECT_ROOT/docker/.env.example" "$ENV_FILE"
    echo "Please edit $ENV_FILE and add your API keys"
    exit 1
fi

# 检查必要的环境变量
source "$ENV_FILE"
if [ -z "$DASHSCOPE_API_KEY" ] || [ "$DASHSCOPE_API_KEY" = "your-dashscope-api-key-here" ]; then
    echo "Error: DASHSCOPE_API_KEY not set in .env"
    exit 1
fi

# 选择启动模式
MODE=${1:-"all"}

case $MODE in
    "all")
        echo "Starting all services..."
        cd "$PROJECT_ROOT/docker"
        docker-compose up -d
        ;;
    "proxy")
        echo "Starting proxy service only..."
        cd "$PROJECT_ROOT/docker"
        docker-compose up -d proxy
        ;;
    "reward")
        echo "Starting proxy and reward services..."
        cd "$PROJECT_ROOT/docker"
        docker-compose up -d proxy reward
        ;;
    "inference")
        echo "Starting inference service..."
        cd "$PROJECT_ROOT/docker"
        docker-compose up -d inference
        ;;
    "trainer")
        echo "Starting all services including trainer..."
        cd "$PROJECT_ROOT/docker"
        docker-compose up -d
        ;;
    *)
        echo "Usage: $0 [all|proxy|reward|inference|trainer]"
        exit 1
        ;;
esac

echo ""
echo "================================================"
echo "  Services Status"
echo "================================================"
docker-compose ps

echo ""
echo "Service URLs:"
echo "  - API Proxy:  http://localhost:5059"
echo "  - Reward:     http://localhost:7788"
echo "  - Inference:  http://localhost:30009"
echo ""
echo "Use 'docker-compose logs -f <service>' to view logs"
