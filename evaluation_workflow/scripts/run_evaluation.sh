#!/bin/bash

# ============================================
# 主评测执行脚本
# ============================================

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

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}         模型评测系统${NC}"
echo -e "${CYAN}========================================${NC}"

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}错误: 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi

# 检查Python和必要的包
echo -e "${YELLOW}检查环境...${NC}"
if ! python3 -c "import yaml" 2>/dev/null; then
    echo -e "${RED}错误: 缺少PyYAML包，请运行: pip install pyyaml${NC}"
    exit 1
fi

# 读取配置
echo -e "${YELLOW}读取配置文件...${NC}"
MODE=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['model']['mode'])" 2>/dev/null)
SKIP_SCORING=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['evaluation']['skip_scoring'])" 2>/dev/null)

echo -e "${GREEN}评测模式: $MODE${NC}"

# 检查服务状态
echo ""
echo -e "${BLUE}检查必要服务...${NC}"

# 检查API代理（如果使用API模式）
if [ "$MODE" = "api" ]; then
    API_PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['api_proxy']['port'])" 2>/dev/null)
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$API_PORT" | grep -q "404\|200"; then
        echo -e "${GREEN}✓ API代理服务运行中 (端口: $API_PORT)${NC}"
    else
        echo -e "${RED}✗ API代理服务未运行${NC}"
        echo -e "${YELLOW}请先启动API代理服务:${NC}"
        echo -e "${CYAN}  cd $PROJECT_ROOT/services${NC}"
        echo -e "${CYAN}  ./start_api_proxy.sh${NC}"
        exit 1
    fi
fi

# 检查ScoreFlow Reward服务（如果不跳过评分）
if [ "$SKIP_SCORING" != "True" ]; then
    REWARD_PORT=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['services']['scoreflow_reward']['port'])" 2>/dev/null)
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$REWARD_PORT/health" | grep -q "200"; then
        echo -e "${GREEN}✓ ScoreFlow Reward服务运行中 (端口: $REWARD_PORT)${NC}"
    else
        echo -e "${RED}✗ ScoreFlow Reward服务未运行${NC}"
        echo -e "${YELLOW}请先启动Reward服务:${NC}"
        echo -e "${CYAN}  cd $PROJECT_ROOT/services${NC}"
        echo -e "${CYAN}  ./start_reward_server.sh${NC}"
        echo ""
        echo -e "${YELLOW}或者在config.yaml中设置 skip_scoring: true 跳过评分${NC}"
        exit 1
    fi
fi

# 构建Python评测命令
echo ""
echo -e "${BLUE}准备评测参数...${NC}"

# 创建Python脚本来解析YAML并生成命令
TEMP_PY="${PROJECT_ROOT}/.temp_build_cmd.py"
cat > "$TEMP_PY" << 'EOF'
import yaml
import sys

config_file = sys.argv[1]
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

cmd = ["python3", "evaluation/evaluate_model.py"]

# 模型配置
mode = config['model']['mode']
if mode == 'local':
    local_config = config['model']['local']
    cmd.extend([
        "--model-path", local_config['model_path'],
        "--port", str(local_config['port']),
        "--tensor-parallel", str(local_config['tensor_parallel'])
    ])
    if local_config.get('debug_mode'):
        cmd.append("--debug")
else:  # api mode
    # 创建临时API配置文件
    api_config = config['model']['api']
    import json
    api_config_file = '/tmp/temp_api_config.json'
    with open(api_config_file, 'w') as f:
        json.dump({
            'api_url': api_config['url'],
            'api_key': api_config['key'],
            'api_model': api_config['model']
        }, f)
    cmd.extend(["--api-config", api_config_file])

# 评测参数
eval_config = config['evaluation']
cmd.extend([
    "--test-data", eval_config['test_data'],
    "--output-dir", eval_config['output_dir'],
    "--max-inference-workers", str(eval_config['max_inference_workers']),
    "--max-scoring-workers", str(eval_config['max_scoring_workers']),
    "--batch-size", str(eval_config['batch_size']),
    "--temperature", str(eval_config['temperature']),
    "--max-tokens", str(eval_config['max_tokens'])
])

if eval_config.get('limit'):
    cmd.extend(["--limit", str(eval_config['limit'])])

if eval_config.get('skip_scoring'):
    cmd.append("--skip-scoring")

print(' '.join(cmd))
EOF

# 生成命令
CMD=$(cd "$PROJECT_ROOT/scripts" && python3 "$TEMP_PY" "$CONFIG_FILE")
rm -f "$TEMP_PY"

# 显示配置摘要
echo -e "${GREEN}配置摘要:${NC}"
python3 << EOF
import yaml
config = yaml.safe_load(open('$CONFIG_FILE'))
print(f"  模式: {config['model']['mode']}")
if config['model']['mode'] == 'local':
    print(f"  模型: {config['model']['local']['model_path'].split('/')[-1]}")
else:
    print(f"  API模型: {config['model']['api']['model']}")
print(f"  测试数据: {config['evaluation']['test_data']}")
print(f"  输出目录: {config['evaluation']['output_dir']}")
print(f"  推理并发: {config['evaluation']['max_inference_workers']}")
print(f"  评分并发: {config['evaluation']['max_scoring_workers']}")
print(f"  跳过评分: {config['evaluation'].get('skip_scoring', False)}")
if config['evaluation'].get('limit'):
    print(f"  样本限制: {config['evaluation']['limit']}")
EOF

echo ""
echo -e "${YELLOW}将执行的命令:${NC}"
echo -e "${CYAN}$CMD${NC}"
echo ""

# 确认执行
read -p "是否开始评测? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}评测已取消${NC}"
    exit 1
fi

# 创建输出目录
OUTPUT_DIR=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['evaluation']['output_dir'])")
mkdir -p "$PROJECT_ROOT/$OUTPUT_DIR"

# 执行评测
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}          开始评测${NC}"
echo -e "${GREEN}========================================${NC}"

cd "$PROJECT_ROOT"
START_TIME=$(date +%s)

# 执行命令
eval $CMD
EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${GREEN}========================================${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ 评测完成！${NC}"
    echo -e "${GREEN}耗时: $((DURATION / 60)) 分钟 $((DURATION % 60)) 秒${NC}"
    
    # 查找最新的结果
    if [ -d "$OUTPUT_DIR" ]; then
        LATEST=$(ls -td "$OUTPUT_DIR"/*/ 2>/dev/null | head -1)
        if [ -n "$LATEST" ]; then
            echo ""
            echo -e "${BLUE}结果目录: $LATEST${NC}"
            if [ -f "$LATEST/summary_report.md" ]; then
                echo -e "${YELLOW}查看报告:${NC}"
                echo -e "${CYAN}  cat $LATEST/summary_report.md${NC}"
            fi
        fi
    fi
else
    echo -e "${RED}✗ 评测失败 (退出码: $EXIT_CODE)${NC}"
fi

echo -e "${GREEN}========================================${NC}"