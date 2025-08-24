#!/bin/bash

# ============================================
# InternBootcamp Reward服务启动脚本
# ============================================
# 用于InternBootcamp专属workflow执行和评分计算
#
# 使用方法:
#   bash start_server.sh          # 正常模式
#   bash start_server.sh --debug  # 调试模式（开启详细日志）
#   bash start_server.sh --background  # 后台运行模式
#
# 调试模式说明:
#   - Flask服务器以debug模式运行，显示详细错误信息
#   - 生成debug日志文件到 debug_logs/ 目录
#   - 记录每个workflow的执行详情、LLM调用、耗时等

# 清除代理设置，避免干扰本地服务通信
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY

# 设置NO_PROXY来排除localhost（即使Clash开启系统代理也有效）
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"

echo "✓ 已清除代理设置并设置NO_PROXY"
echo "  NO_PROXY='$NO_PROXY'"
echo "  localhost请求将绕过所有代理"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}    InternBootcamp Reward服务启动器${NC}"
echo -e "${CYAN}========================================${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
SERVICE_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 读取配置文件
CONFIG_FILE="${SERVICE_ROOT}/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}错误: 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi

# 解析命令行参数
DEBUG_MODE=false
BACKGROUND_MODE=false
for arg in "$@"; do
    case $arg in
        --debug)
            DEBUG_MODE=true
            shift
            ;;
        --background)
            BACKGROUND_MODE=true
            shift
            ;;
        *)
            ;;
    esac
done

# ============================================
# 自检步骤1: Python环境检查
# ============================================
echo -e "${YELLOW}[1/7] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3未安装${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "${GREEN}✓ Python已安装: $PYTHON_VERSION${NC}"

# 检查必要的Python包
echo -e "${YELLOW}检查必要的Python包...${NC}"
REQUIRED_PACKAGES=("yaml" "flask" "requests")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES+=($package)
        echo -e "${RED}  ✗ 缺少包: $package${NC}"
    else
        echo -e "${GREEN}  ✓ $package 已安装${NC}"
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${RED}错误: 缺少必要的Python包${NC}"
    echo -e "${YELLOW}请运行: pip install ${MISSING_PACKAGES[@]}${NC}"
    exit 1
fi

# ============================================
# 自检步骤2: 配置文件验证
# ============================================
echo ""
echo -e "${YELLOW}[2/7] 验证配置文件...${NC}"

# 从YAML提取配置（使用Python解析）
PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['internbootcamp_reward']['port'])" 2>/dev/null || echo "8900")
HOST=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['internbootcamp_reward']['host'])" 2>/dev/null || echo "0.0.0.0")
ENABLED=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['internbootcamp_reward']['enabled'])" 2>/dev/null || echo "True")
TIMEOUT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['internbootcamp_reward']['timeout'])" 2>/dev/null || echo "300")
WORKSPACE=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['internbootcamp_reward']['workspace'])" 2>/dev/null || echo "workspace/internbootcamp")

if [ "$ENABLED" != "True" ]; then
    echo -e "${YELLOW}InternBootcamp Reward服务已禁用（config.yaml中enabled=false）${NC}"
    exit 0
fi

echo -e "${GREEN}✓ 配置文件解析成功${NC}"
echo "  主机: $HOST"
echo "  端口: $PORT"
echo "  超时: ${TIMEOUT}秒"
echo "  工作目录: $WORKSPACE"

# ============================================
# 自检步骤3: 端口占用检查
# ============================================
echo ""
echo -e "${YELLOW}[3/7] 检查端口占用...${NC}"

# 检查lsof命令是否可用
if command -v lsof &> /dev/null; then
    if lsof -i :$PORT > /dev/null 2>&1; then
        echo -e "${YELLOW}警告: 端口 $PORT 已被占用${NC}"
        echo "占用进程:"
        lsof -i :$PORT
        echo ""
        read -p "是否终止占用进程并重新启动? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill -9 $(lsof -t -i:$PORT) 2>/dev/null
            echo -e "${GREEN}✓ 已终止占用进程${NC}"
            sleep 1
        else
            echo -e "${RED}退出启动${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ 端口 $PORT 可用${NC}"
    fi
else
    # 如果lsof不可用，尝试使用netstat
    if command -v netstat &> /dev/null; then
        if netstat -an | grep -q ":$PORT "; then
            echo -e "${YELLOW}警告: 端口 $PORT 可能被占用${NC}"
            read -p "是否继续? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${RED}退出启动${NC}"
                exit 1
            fi
        else
            echo -e "${GREEN}✓ 端口 $PORT 可用${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  无法检查端口占用（lsof和netstat都不可用）${NC}"
    fi
fi

# ============================================
# 自检步骤4: API代理服务检查
# ============================================
echo ""
echo -e "${YELLOW}[4/7] 检查API代理服务连通性...${NC}"

# 获取API代理配置
API_PROXY_PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['metagpt_api_proxy']['port'])" 2>/dev/null || echo "5009")
EVAL_API_PROXY_PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['evaluation_api_proxy']['port'])" 2>/dev/null || echo "5010")

# 使用Python socket检查MetaGPT API代理（更可靠）
echo -e "${YELLOW}检查MetaGPT API代理服务 (端口 $API_PROXY_PORT)...${NC}"
if python3 -c "import socket; s=socket.socket(); s.settimeout(2); result=s.connect_ex(('localhost', $API_PROXY_PORT)); s.close(); exit(0 if result==0 else 1)" 2>/dev/null; then
    echo -e "${GREEN}✓ MetaGPT API代理服务连接成功${NC}"
else
    echo -e "${YELLOW}⚠️  警告: 无法连接到MetaGPT API代理服务 (localhost:$API_PROXY_PORT)${NC}"
    echo -e "${YELLOW}   请确保已启动: bash servers_and_proxy/start_api_proxy.sh${NC}"
fi

# 使用Python socket检查Evaluation API代理（更可靠）
echo -e "${YELLOW}检查Evaluation API代理服务 (端口 $EVAL_API_PROXY_PORT)...${NC}"
if python3 -c "import socket; s=socket.socket(); s.settimeout(2); result=s.connect_ex(('localhost', $EVAL_API_PROXY_PORT)); s.close(); exit(0 if result==0 else 1)" 2>/dev/null; then
    echo -e "${GREEN}✓ Evaluation API代理服务连接成功${NC}"
else
    echo -e "${YELLOW}⚠️  警告: 无法连接到Evaluation API代理服务 (localhost:$EVAL_API_PROXY_PORT)${NC}"
    echo -e "${YELLOW}   如需使用评估功能，请启动评估API代理${NC}"
fi

# ============================================
# 自检步骤5: 目录结构检查
# ============================================
echo ""
echo -e "${YELLOW}[5/7] 检查目录结构...${NC}"

# 创建必要的目录
WORKSPACE_DIR="${PROJECT_ROOT}/${WORKSPACE}"
LOG_DIR="${SERVICE_ROOT}/logs"
DEBUG_LOG_DIR="${SERVICE_ROOT}/debug_logs"

mkdir -p "$WORKSPACE_DIR"
echo -e "${GREEN}✓ 工作目录已创建: $WORKSPACE_DIR${NC}"

mkdir -p "$LOG_DIR"
echo -e "${GREEN}✓ 日志目录已创建: $LOG_DIR${NC}"

if [ "$DEBUG_MODE" = true ]; then
    mkdir -p "$DEBUG_LOG_DIR"
    echo -e "${GREEN}✓ Debug日志目录已创建: $DEBUG_LOG_DIR${NC}"
fi

# ============================================
# 自检步骤6: 依赖文件检查
# ============================================
echo ""
echo -e "${YELLOW}[6/7] 检查依赖文件...${NC}"

# 检查必要的Python文件
REQUIRED_FILES=(
    "internbootcamp_reward_server.py"
    "internbootcamp_reward_utils.py"
    "internbootcamp_utils.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        echo -e "${GREEN}✓ $file 存在${NC}"
    else
        echo -e "${RED}✗ 缺少文件: $file${NC}"
        exit 1
    fi
done

# 检查ScoreFlow路径
SCOREFLOW_PATH="${PROJECT_ROOT}"
if [ -d "$SCOREFLOW_PATH/ScoreFlow" ]; then
    echo -e "${GREEN}✓ ScoreFlow目录存在${NC}"
else
    echo -e "${YELLOW}⚠️  警告: ScoreFlow目录不存在: $SCOREFLOW_PATH/ScoreFlow${NC}"
fi

# ============================================
# 自检步骤7: 环境变量设置
# ============================================
echo ""
echo -e "${YELLOW}[7/7] 设置环境变量...${NC}"

# 设置PYTHONPATH
export PYTHONPATH="${SCRIPT_DIR}:${SERVICE_ROOT}:${PROJECT_ROOT}:$PYTHONPATH"
echo -e "${GREEN}✓ PYTHONPATH已设置${NC}"

# 设置API相关环境变量
API_KEY=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['metagpt_api_proxy']['target_api_key'])" 2>/dev/null || echo "")
if [ -n "$API_KEY" ]; then
    export OPENAI_API_KEY="$API_KEY"
    export OPENAI_API_BASE="http://localhost:$API_PROXY_PORT"
    echo -e "${GREEN}✓ API环境变量已设置${NC}"
fi

# ============================================
# 启动服务
# ============================================
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ 所有检查通过，正在启动服务...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 生成日志文件名
LOG_FILE="${LOG_DIR}/internbootcamp_reward_$(date +%Y%m%d_%H%M%S).log"

# 显示服务信息
echo -e "${CYAN}服务信息:${NC}"
echo "  URL: http://$HOST:$PORT"
echo "  日志: $LOG_FILE"
echo "  工作目录: $WORKSPACE_DIR"

if [ "$DEBUG_MODE" = true ]; then
    echo -e "  ${YELLOW}调试模式: 已启用${NC}"
    echo -e "  ${YELLOW}Debug日志: $DEBUG_LOG_DIR${NC}"
fi

if [ "$BACKGROUND_MODE" = true ]; then
    echo -e "  ${YELLOW}后台模式: 已启用${NC}"
fi

echo ""
echo -e "${YELLOW}提示: 按 Ctrl+C 停止服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 切换到服务目录
cd "$SCRIPT_DIR"

# 构建启动命令
CMD="python3 internbootcamp_reward_server.py --port $PORT --host $HOST"

# 如果启用debug模式，添加--debug参数
if [ "$DEBUG_MODE" = true ]; then
    CMD="$CMD --debug"
fi

# 启动服务
if [ "$BACKGROUND_MODE" = true ]; then
    echo "在后台启动服务器..."
    nohup $CMD > "$LOG_FILE" 2>&1 &
    PID=$!
    echo -e "${GREEN}✓ 服务器已在后台启动${NC}"
    echo "  PID: $PID"
    echo "  日志文件: $LOG_FILE"
    echo ""
    echo "使用以下命令查看日志:"
    echo "  tail -f $LOG_FILE"
    echo ""
    echo "使用以下命令停止服务:"
    echo "  kill $PID"
else
    # 前台运行，同时输出到终端和日志文件
    $CMD 2>&1 | tee "$LOG_FILE"
fi