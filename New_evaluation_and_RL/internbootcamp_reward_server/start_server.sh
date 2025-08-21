#!/bin/bash
# InternBootcamp Reward Server 启动脚本

echo "==========================================="
echo "启动 InternBootcamp Reward Server"
echo "==========================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查Python环境
echo "检查Python环境..."
python --version

# 检查config.yaml是否存在
CONFIG_FILE="../config.yaml"
if [ -f "$CONFIG_FILE" ]; then
    echo "✓ 找到配置文件: $CONFIG_FILE"
else
    echo "✗ 配置文件不存在: $CONFIG_FILE"
    echo "  请确保config.yaml存在于上级目录"
    exit 1
fi

# 设置环境变量
export PYTHONPATH="${SCRIPT_DIR}/..:${SCRIPT_DIR}/../..:$PYTHONPATH"
echo "PYTHONPATH设置为: $PYTHONPATH"

# 启动服务器
echo ""
echo "启动服务器..."
echo "使用配置文件: $CONFIG_FILE"
echo ""

# 使用nohup在后台运行，或者直接前台运行
if [ "$1" == "background" ]; then
    echo "在后台启动服务器..."
    nohup python internbootcamp_reward_server.py > server.log 2>&1 &
    echo "服务器PID: $!"
    echo "日志文件: server.log"
    echo ""
    echo "使用以下命令查看日志:"
    echo "  tail -f server.log"
else
    echo "在前台启动服务器..."
    echo "按Ctrl+C停止服务器"
    echo ""
    python internbootcamp_reward_server.py
fi