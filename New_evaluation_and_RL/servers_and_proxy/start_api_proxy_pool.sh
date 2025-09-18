#!/bin/bash

# API代理启动脚本 - 多API池负载均衡版本
# 支持Round-Robin分发请求到多个API endpoints

# 清除代理设置，避免干扰
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY

# 设置NO_PROXY来排除localhost（即使Clash开启系统代理也有效）
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,*.local"
export no_proxy="localhost,127.0.0.1,0.0.0.0,*.local"

echo "✓ 已设置NO_PROXY='$NO_PROXY'"
echo "  localhost请求将绕过所有代理"

# 设置Python无缓冲输出，确保实时看到print内容
export PYTHONUNBUFFERED=1

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 检查主配置文件
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 主配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 检查API池配置文件
API_POOL_CONFIG="${PROJECT_ROOT}/metagpt_api_key_proxy/api_pool_config.yaml"
if [ ! -f "$API_POOL_CONFIG" ]; then
    echo "警告: API池配置文件不存在: $API_POOL_CONFIG"
    echo "      将使用主配置文件中的单个API endpoint"
fi

echo "=========================================="
echo "启动 MetaGPT API 代理服务 (独立速率限制版本)"
echo "=========================================="

# 从主配置文件只读取端口和调试模式
PORT=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(c['services']['metagpt_api_proxy']['port'])" 2>/dev/null || echo "5059")
DEBUG=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONFIG_FILE')); print(str(c['services']['metagpt_api_proxy'].get('debug', False)).lower())" 2>/dev/null || echo "false")

# 从API池配置读取详细信息
if [ -f "$API_POOL_CONFIG" ]; then
    API_INFO=$(python3 -c "
import yaml
with open('$API_POOL_CONFIG', 'r') as f:
    config = yaml.safe_load(f)
    pool = config.get('api_pool', [])
    if pool:
        print(f'API数量: {len(pool)}')
        total_rate = sum(api.get('rate_per_second', 4.0) for api in pool)
        print(f'总吞吐量: {total_rate:.1f} req/s')
        for i, api in enumerate(pool):
            rate = api.get('rate_per_second', 4.0)
            conc = api.get('max_concurrency', 20)
            key = api.get('target_api_key', '')
            key_suffix = key[-4:] if key else 'None'
            print(f'  API #{i+1} (***{key_suffix}): {rate}req/s, 并发{conc}')
    else:
        print('未找到API配置')
" 2>/dev/null || echo "加载API池配置失败")
else
    API_INFO="API池配置文件不存在"
fi

# 检查端口是否被占用
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "端口 $PORT 已被占用，正在终止现有进程..."
    kill -9 $(lsof -t -i:$PORT) 2>/dev/null
    sleep 1
fi

# 创建日志目录
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/api_proxy_pool_$(date +%Y%m%d_%H%M%S).log"

echo "配置文件:"
echo "  - 主配置: $CONFIG_FILE"
echo "  - API池配置: $API_POOL_CONFIG"
echo "日志文件: $LOG_FILE"
echo ""
echo "服务配置:"
echo "  - 端口: $PORT"
if [ -f "$API_POOL_CONFIG" ]; then
    echo "$API_INFO"
else
    echo "  - 警告: 将使用主配置文件中的默认配置"
fi
echo "  - 负载均衡: Round-Robin (每个API独立限流)"
if [ "$DEBUG" = "true" ]; then
    echo "  - 模式: 调试模式 (显示详细信息)"
else
    echo "  - 模式: 正常模式 (仅显示进度条和错误)"
fi
echo ""
echo "正在启动代理服务器..."
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

# 启动代理服务（使用-u选项禁用缓冲，确保实时输出）
cd "${PROJECT_ROOT}/metagpt_api_key_proxy"
python3 -u api_key_proxy_pool.py 2>&1 | tee "$LOG_FILE"