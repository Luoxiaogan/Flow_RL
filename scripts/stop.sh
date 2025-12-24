#!/bin/bash
# New_Flow_RL Stop Script
# 停止所有服务

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo "  New_Flow_RL - Stopping Services"
echo "================================================"

cd "$PROJECT_ROOT/docker"

# 停止服务
docker-compose down

echo ""
echo "All services stopped."
