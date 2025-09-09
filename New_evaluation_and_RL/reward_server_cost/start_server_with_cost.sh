#!/bin/bash
# Start ScoreFlow Reward Server with Token Tracking
# 启动带Token追踪功能的ScoreFlow Reward服务器

echo "=================================="
echo "Starting ScoreFlow Reward Server with Token Tracking"
echo "启动带Token追踪的ScoreFlow Reward服务器"
echo "=================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 设置Python路径
export PYTHONPATH="${SCRIPT_DIR}:${SCRIPT_DIR}/..:${PYTHONPATH}"

# 检查Python环境
echo "检查Python环境..."
python --version

# 检查必要的依赖
echo "检查依赖..."
python -c "import flask; print('✓ Flask已安装')" 2>/dev/null || echo "✗ Flask未安装，请运行: pip install flask flask-cors"
python -c "import yaml; print('✓ PyYAML已安装')" 2>/dev/null || echo "✗ PyYAML未安装，请运行: pip install pyyaml"
python -c "import metagpt; print('✓ MetaGPT已安装')" 2>/dev/null || echo "⚠️ MetaGPT未安装，token追踪将被禁用"

echo ""
echo "配置信息:"
echo "  - 配置文件: config_cost.yaml"
echo "  - 服务端口: 8899"
echo "  - Token追踪: 启用"
echo "  - 费用惩罚: 可配置"
echo ""

# 启动服务器
echo "启动服务器..."
cd "${SCRIPT_DIR}"
python scoreflow_reward_server_with_cost.py --host 0.0.0.0 --port 8899

echo ""
echo "服务器已停止"