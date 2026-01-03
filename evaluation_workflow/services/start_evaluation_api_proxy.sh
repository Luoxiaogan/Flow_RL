#!/bin/bash

# ============================================
# 评估API代理服务启动脚本
# ============================================

unset http_proxy https_proxy all_proxy
echo "已清除代理设置"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"
LOG_DIR="${PROJECT_ROOT}/logs"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}     评估API代理服务启动器${NC}"
echo -e "${CYAN}========================================${NC}"

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}错误: 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi

# 创建日志目录
mkdir -p "$LOG_DIR"

# 读取配置
echo "读取配置文件..."
HOST=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['evaluation_api_proxy']['host'])" 2>/dev/null || echo "localhost")
PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['evaluation_api_proxy']['port'])" 2>/dev/null || echo "5010")
TARGET_URL=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['evaluation_api_proxy']['target_url'])" 2>/dev/null)
TARGET_KEY=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['evaluation_api_proxy']['target_api_key'])" 2>/dev/null)

echo "配置信息:"
echo "  主机: $HOST"
echo "  端口: $PORT"
echo "  目标URL: $TARGET_URL"
echo ""

# 检查端口是否被占用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}警告: 端口 $PORT 已被占用${NC}"
    echo "检查现有服务..."
    
    # 尝试健康检查
    if curl -s -o /dev/null -w "%{http_code}" "http://$HOST:$PORT/health" | grep -q "200"; then
        echo -e "${GREEN}✓ 评估API代理服务已在运行${NC}"
        echo ""
        echo "如需重启服务，请先停止现有服务:"
        echo "  kill \$(lsof -t -i:$PORT)"
        exit 0
    else
        echo -e "${RED}端口被其他服务占用，请先释放端口${NC}"
        echo "  使用命令查看: lsof -i:$PORT"
        echo "  终止进程: kill \$(lsof -t -i:$PORT)"
        exit 1
    fi
fi

# 启动服务
echo "启动评估API代理服务..."
LOG_FILE="${LOG_DIR}/evaluation_api_proxy_$(date +%Y%m%d_%H%M%S).log"
echo "日志文件: $LOG_FILE"
echo ""

# 检查是否有目标API密钥
if [ -z "$TARGET_KEY" ]; then
    echo -e "${YELLOW}警告: 未配置目标API密钥${NC}"
    echo "服务将使用请求中的原始API密钥"
    
    # 启动基础版本（不替换API密钥）
    nohup python3 "${SCRIPT_DIR}/evaluation_api_proxy.py" > "$LOG_FILE" 2>&1 &
else
    echo "使用增强版API代理（配置了目标API密钥）"
    
    # 启动增强版本
    nohup python3 "${SCRIPT_DIR}/evaluation_api_proxy.py" > "$LOG_FILE" 2>&1 &
fi

PID=$!
echo "进程ID: $PID"

# 等待服务启动
echo -e "${YELLOW}✓ 正在启动评估API代理服务...${NC}"
sleep 3

# 检查服务状态
if kill -0 $PID 2>/dev/null; then
    # 进程存在，检查健康状态
    if curl -s -o /dev/null -w "%{http_code}" "http://$HOST:$PORT/health" | grep -q "200"; then
        echo -e "${GREEN}✓ 评估API代理服务启动成功！${NC}"
        echo ""
        echo "服务信息:"
        echo "  URL: http://$HOST:$PORT"
        echo "  健康检查: http://$HOST:$PORT/health"
        echo "  日志: $LOG_FILE"
        echo "  进程ID: $PID"
        echo ""
        echo "模型评估配置:"
        echo "  在config.yaml中设置 model.mode: evaluation_api"
        echo "  API URL将指向: http://$HOST:$PORT/v1/chat/completions"
        echo ""
        echo "提示: 按 Ctrl+C 不会停止后台服务"
        echo "停止服务: kill $PID"
        echo -e "${CYAN}========================================${NC}"
        
        # 显示实时日志
        echo ""
        echo "显示最新日志 (Ctrl+C 退出查看):"
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}✗ 服务启动失败：健康检查未通过${NC}"
        echo "查看日志: tail -f $LOG_FILE"
        exit 1
    fi
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo "查看日志了解详情:"
    tail -20 "$LOG_FILE"
    exit 1
fi