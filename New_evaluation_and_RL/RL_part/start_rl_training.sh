#!/bin/bash

# ============================================
# VERL RL训练启动脚本
# ============================================
# 功能：从config.yaml读取配置并启动PPO训练
# 依赖：ScoreFlow奖励服务器必须已经启动

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
CONFIG_FILE="$SCRIPT_DIR/../config.yaml"

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}     🚀 VERL RL训练系统启动${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 配置文件: $CONFIG_FILE${NC}"

# ============================================
# 服务依赖检查
# ============================================
echo ""
echo -e "${CYAN}========== 检查依赖服务 ==========${NC}"

# 1. 检查MetaGPT API代理
echo -e "${BLUE}🔍 检查MetaGPT API代理...${NC}"
METAGPT_PORT=$(python3 -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
port = config.get('services', {}).get('metagpt_api_proxy', {}).get('port', 5009)
print(port)
" 2>/dev/null || echo "5009")

if ! lsof -i :$METAGPT_PORT > /dev/null 2>&1; then
    echo -e "${RED}❌ MetaGPT API代理未运行 (端口 $METAGPT_PORT)${NC}"
    echo -e "${YELLOW}请先启动MetaGPT API代理:${NC}"
    echo -e "${YELLOW}  cd $SCRIPT_DIR/../servers_and_proxy${NC}"
    echo -e "${YELLOW}  bash start_api_proxy.sh${NC}"
    exit 1
else
    echo -e "${GREEN}✅ MetaGPT API代理运行正常 (端口 $METAGPT_PORT)${NC}"
fi

# 2. VERL训练模式说明
echo -e "${BLUE}📝 VERL训练模式说明...${NC}"
echo -e "${GREEN}✅ VERL训练使用GPU上的模型直接生成workflow${NC}"
echo -e "${GREEN}✅ 不需要evaluation_api_proxy (仅evaluation模式需要)${NC}"

# 3. 检查ScoreFlow奖励服务器
echo -e "${BLUE}🔍 检查ScoreFlow奖励服务器...${NC}"
SCOREFLOW_PORT=$(python3 -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
port = config.get('services', {}).get('scoreflow_reward', {}).get('port', 8899)
print(port)
" 2>/dev/null || echo "8899")

if ! lsof -i :$SCOREFLOW_PORT > /dev/null 2>&1; then
    echo -e "${RED}❌ ScoreFlow奖励服务器未运行 (端口 $SCOREFLOW_PORT)${NC}"
    echo -e "${YELLOW}请先启动ScoreFlow服务器:${NC}"
    echo -e "${YELLOW}  cd $SCRIPT_DIR/../servers_and_proxy${NC}"
    echo -e "${YELLOW}  bash start_scoreflow_reward.sh${NC}"
    exit 1
else
    echo -e "${GREEN}✅ ScoreFlow奖励服务器运行正常 (端口 $SCOREFLOW_PORT)${NC}"
fi

# ============================================
# 测试服务链路
# ============================================
echo ""
echo -e "${CYAN}========== 测试服务链路 ==========${NC}"

# 测试ScoreFlow奖励计算
echo -e "${BLUE}测试VERL-ScoreFlow reward链路...${NC}"
echo -e "${BLUE}模拟VERL训练调用reward计算接口...${NC}"

# 检查测试workflow文件是否存在
TEST_WORKFLOW_FILE="$SCRIPT_DIR/test_workflow.py"
if [ ! -f "$TEST_WORKFLOW_FILE" ]; then
    echo -e "${RED}❌ 测试workflow文件不存在: $TEST_WORKFLOW_FILE${NC}"
    echo -e "${YELLOW}请确保test_workflow.py文件存在${NC}"
    exit 1
fi

echo -e "${BLUE}📁 使用外部workflow文件: $TEST_WORKFLOW_FILE${NC}"

REWARD_TEST_RESULT=$(python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
try:
    from scoreflow_reward_client import compute_score
    
    # 读取外部测试workflow文件
    with open('$TEST_WORKFLOW_FILE', 'r', encoding='utf-8') as f:
        test_workflow = f.read()
    
    print('📄 已加载外部workflow文件')
    print(f'📏 Workflow代码长度: {len(test_workflow)} 字符')
    
    # VERL标准调用参数
    extra_info = {
        'test_cases': [2], 
        'data_path': '/Users/luogan/Code/workflow_generation/Flow_RL/Processed_dataset/gsm8k/1000_train.jsonl'
    }
    
    print('🚀 开始VERL reward链路测试...')
    print('📝 模拟: VERL训练 → compute_score() → HTTP API → reward_server')
    
    score = compute_score('gsm8k', test_workflow, 'default', extra_info)
    
    if score >= 0.8:
        print(f'✅ 成功! VERL-ScoreFlow链路正常 - 分数: {score:.3f}')
    elif score > 0.0:
        print(f'⚠️ 部分成功! 链路可用但分数较低 - 分数: {score:.3f}')
    else:
        print(f'❌ 失败! 链路异常 - 分数: {score:.3f}')
        
except FileNotFoundError as e:
    print(f'❌ 文件错误: {str(e)}')
except Exception as e:
    print(f'❌ VERL客户端错误: {str(e)[:100]}')
    import traceback
    print(f'详细错误: {traceback.format_exc()[:200]}')
" 2>&1)

# 显示完整的测试输出（用于调试）
echo -e "${CYAN}📋 测试详细输出:${NC}"
echo "$REWARD_TEST_RESULT"
echo ""

# 检查测试结果
if [[ "$REWARD_TEST_RESULT" == *"✅ 成功"* ]]; then
    echo -e "${GREEN}✅ VERL-ScoreFlow链路测试通过${NC}"
    echo -e "${GREEN}   reward_server正常响应，VERL训练可以开始${NC}"
elif [[ "$REWARD_TEST_RESULT" == *"⚠️ 部分成功"* ]]; then
    echo -e "${YELLOW}⚠️ VERL-ScoreFlow链路部分可用${NC}"
    echo -e "${YELLOW}   链路正常但分数较低，可能是workflow或数据问题${NC}"
    echo -e "${YELLOW}   建议检查workflow代码和数据集路径${NC}"
elif [[ "$REWARD_TEST_RESULT" == *"❌ 失败"* ]]; then
    echo -e "${RED}❌ VERL-ScoreFlow链路测试失败${NC}"
    echo -e "${RED}   reward_server可能未响应或内部错误${NC}"
    echo -e "${YELLOW}   建议检查:${NC}"
    echo -e "${YELLOW}     1. reward_server是否正常运行 (端口 $SCOREFLOW_PORT)${NC}"
    echo -e "${YELLOW}     2. MetaGPT API代理是否可用 (端口 $METAGPT_PORT)${NC}"
    echo -e "${YELLOW}     3. workflow代码是否语法正确${NC}"
    echo -e "${RED}   警告: 训练可能失败，建议先解决链路问题${NC}"
else
    echo -e "${RED}❌ VERL客户端连接失败${NC}"
    echo -e "${RED}   $REWARD_TEST_RESULT${NC}"
    echo -e "${YELLOW}   请检查:${NC}"
    echo -e "${YELLOW}     1. scoreflow_reward_client.py是否存在${NC}"
    echo -e "${YELLOW}     2. Python依赖是否安装 (requests, yaml)${NC}"
    echo -e "${YELLOW}     3. config.yaml路径配置是否正确${NC}"
    echo -e "${RED}   训练无法继续，请修复后重试${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}📊 VERL训练架构说明:${NC}"
echo -e "${GREEN}   1. VERL GPU模型生成workflow响应${NC}"  
echo -e "${GREEN}   2. 调用 compute_score() 计算reward${NC}"
echo -e "${GREEN}   3. scoreflow_reward_client 转发HTTP请求${NC}"
echo -e "${GREEN}   4. reward_server 执行workflow获得分数${NC}"
echo -e "${GREEN}   5. 分数返回给VERL用于PPO训练${NC}"

# ============================================
# 参数验证和计算
# ============================================
echo ""
echo -e "${CYAN}========== 参数验证和计算 ==========${NC}"

# 验证参数约束并计算相关值
echo -e "${BLUE}📊 使用外部验证器: $SCRIPT_DIR/validate_training_params.py${NC}"
PARAM_VALIDATION=$(python3 "$SCRIPT_DIR/validate_training_params.py" "$CONFIG_FILE" 2>&1)

# 检查参数验证结果
if [ $? -ne 0 ]; then
    echo -e "${RED}$PARAM_VALIDATION${NC}"
    echo ""
    echo -e "${RED}参数验证失败，请修改config.yaml后重试${NC}"
    exit 1
else
    echo -e "${GREEN}$PARAM_VALIDATION${NC}"
fi

# 使用Python解析配置并生成训练参数
echo ""
echo -e "${BLUE}📝 生成训练参数...${NC}"

# 生成训练参数
echo -e "${BLUE}⚙️ 使用外部生成器: $SCRIPT_DIR/generate_training_params.py${NC}"
TRAINING_PARAMS=$(python3 "$SCRIPT_DIR/generate_training_params.py" "$CONFIG_FILE" 2>&1)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 解析配置失败${NC}"
    echo -e "${RED}错误信息：${NC}"
    echo "$TRAINING_PARAMS"
    exit 1
fi

# 显示生成的参数
echo -e "${GREEN}✅ 成功生成训练参数${NC}"
echo -e "${CYAN}生成的参数列表：${NC}"
echo "----------------------------------------"
# 使用cat避免shell解释$符号
echo "$TRAINING_PARAMS" | cat | while IFS= read -r line; do
    echo "  $line"
done
echo "----------------------------------------"
echo -e "${GREEN}共 $(echo "$TRAINING_PARAMS" | wc -l) 个参数${NC}"

# 设置环境变量
echo ""
echo -e "${BLUE}🔧 设置环境变量...${NC}"

# 从配置读取环境变量
eval $(python3 -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
env_config = config.get('rl_training', {}).get('environment', {})
for key, value in env_config.items():
    print(f'export {key}=\"{value}\"')
" 2>/dev/null)

# 显示环境变量
echo "USE_SGLANG=$USE_SGLANG"
echo "NCCL_DEBUG=$NCCL_DEBUG"
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"

# 获取VERL主脚本路径
VERL_MAIN_SCRIPT=$(python3 -c "
from pathlib import Path
project_root = Path('$PROJECT_ROOT')
verl_main = project_root / 'verl' / 'verl' / 'trainer' / 'main_ppo.py'
if verl_main.exists():
    print(verl_main)
else:
    # 尝试查找其他可能的位置
    import glob
    possible_paths = glob.glob(str(project_root / '**/verl/trainer/main_ppo.py'), recursive=True)
    if possible_paths:
        print(possible_paths[0])
    else:
        print('NOT_FOUND')
" 2>/dev/null)

if [ "$VERL_MAIN_SCRIPT" = "NOT_FOUND" ] || [ -z "$VERL_MAIN_SCRIPT" ]; then
    echo -e "${RED}❌ 找不到VERL主脚本 main_ppo.py${NC}"
    echo -e "${YELLOW}请确保VERL已正确安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ VERL主脚本: $VERL_MAIN_SCRIPT${NC}"

# 显示训练配置摘要
echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}     📊 训练配置摘要${NC}"
echo -e "${CYAN}============================================${NC}"

python3 -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
rl = config.get('rl_training', {})
trainer = rl.get('trainer', {})
actor = rl.get('actor', {})
rollout = rl.get('rollout', {})
data = rl.get('data', {})
scoreflow = config.get('services', {}).get('scoreflow_reward', {})

# 计算一些派生值
n_gpus = trainer['n_gpus_per_node']
tp_size = rollout['tensor_model_parallel_size']
dp_size = n_gpus // tp_size
real_batch = data['train_batch_size'] * rollout['n']

print('【基本配置】')
print(f'模型: {rl[\"model\"][\"base_model_path\"]}')
print(f'批次大小: {rl[\"data\"][\"train_batch_size\"]}')
print(f'学习率: {rl[\"actor\"][\"learning_rate\"]}')
print(f'训练轮数: {trainer[\"total_epochs\"]}')
print(f'GPU数量: {trainer[\"n_gpus_per_node\"]}')

print('\\n【并行配置】')
print(f'张量并行(TP): {tp_size}')
print(f'数据并行(DP): {dp_size}')
print(f'每个prompt生成: {rollout[\"n\"]}个响应')
print(f'真实批次大小: {real_batch}')

print('\\n【ScoreFlow奖励服务】')
print(f'端口: {scoreflow[\"port\"]}')
print(f'超时: {scoreflow[\"timeout\"]}秒')
print(f'并发限制: 最多{scoreflow.get(\"max_wf_data_pair_running\", 5)}个(workflow,test_case)对')

print('\\n【Checkpoint配置】')
checkpoint = actor.get('checkpoint', {})
print(f'保存内容: {checkpoint.get(\"save_contents\", [\"model\", \"optimizer\", \"extra\"])}')
print(f'保存频率: 每 {trainer[\"save_freq\"]} 步')
print(f'测试频率: 每 {trainer[\"test_freq\"]} 步')
print(f'最多保留: {trainer.get(\"max_ckpt_num\", \"所有\")} 个checkpoint')

print('\\n【日志配置】')
print(f'日志输出: {trainer.get(\"logger\", [\"console\"])}')
print(f'日志频率: 每 {trainer.get(\"log_freq\", 1)} 步')
print(f'WandB上传: 每 {trainer.get(\"log_to_wandb_every_n_steps\", 1)} 步')

print('\\n【实验标识】')
print(f'项目名称: {trainer[\"project_name\"]}')
print(f'实验名称: {trainer[\"experiment_name\"]}')
if 'wandb' in trainer.get('logger', []):
    wandb_cfg = trainer.get('wandb_config', {})
    if wandb_cfg.get('tags'):
        print(f'标签: {wandb_cfg[\"tags\"]}')
    if wandb_cfg.get('notes'):
        print(f'备注: {wandb_cfg[\"notes\"][:50]}...')

print('\\n【数据配置】')
print(f'训练数据: {data[\"train_files\"]}')
print(f'测试数据: {data[\"test_files\"]}')
print(f'最大prompt长度: {data[\"max_prompt_length\"]}')
print(f'最大响应长度: {data[\"max_response_length\"]}')
" 2>/dev/null

# 询问是否继续
echo ""
echo -e "${YELLOW}是否开始训练？ (y/n)${NC}"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo -e "${RED}训练已取消${NC}"
    exit 0
fi

# 启动训练
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}     🚀 开始PPO训练${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# # 构建完整的训练命令 - 直接使用参数，避免引号嵌套
# # TRAIN_CMD="python $VERL_MAIN_SCRIPT --config-path=config --config-name=ppo_trainer.yaml $TRAINING_PARAMS"
# TRAIN_CMD="python $VERL_MAIN_SCRIPT --config-path=config --config-name=ppo_trainer.yaml"

# # 逐条处理参数：含 $$LIST$$ 的整条加单引号，其余原样追加
# for raw in $TRAINING_PARAMS; do
#     if [[ $raw == \$\$LIST\$\$* && $raw == *\$\$LIST\$\$ ]]; then
#         param="${raw#\$\$LIST\$\$}"      # 去掉前缀
#         param="${param%\$\$LIST\$\$}"    # 去掉后缀
#         TRAIN_CMD="$TRAIN_CMD '$param'"  # 整体包单引号
#     else
#         TRAIN_CMD="$TRAIN_CMD $raw"
#     fi
# done

# ---------- 构造命令 ----------
echo -e "${BLUE}📦 构建训练命令...${NC}"

# 兼容macOS的方法：使用while循环读取参数到数组
PARAMS=()
while IFS= read -r line; do
    if [[ -n "$line" ]]; then
        PARAMS+=("$line")
    fi
done <<< "$TRAINING_PARAMS"

# 验证数组不为空
if [ ${#PARAMS[@]} -eq 0 ]; then
    echo -e "${RED}❌ 错误: 无法读取参数到数组${NC}"
    echo -e "${YELLOW}参数内容: $TRAINING_PARAMS${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 成功读取 ${#PARAMS[@]} 个参数${NC}"

# 构建基础命令
CMD=(python "$VERL_MAIN_SCRIPT" --config-path=config --config-name=ppo_trainer.yaml)

# 显示和构建命令
echo -e "${CYAN}完整的训练命令：${NC}"
echo "----------------------------------------"

# 构建显示用的命令
DISPLAY_CMD="python $VERL_MAIN_SCRIPT \\"$'\n'
DISPLAY_CMD+="  --config-path=config \\"$'\n'
DISPLAY_CMD+="  --config-name=ppo_trainer.yaml \\"$'\n'

# 处理每个参数
for raw in "${PARAMS[@]}"; do
    if [[ -z "$raw" ]]; then
        continue
    fi
    
    # 处理占位符：$$LIST$$参数$$LIST$$ -> '参数'
    if [[ $raw == *"$$LIST$$"* ]]; then
        # 去掉前后的占位符标记
        param="${raw#\$\$LIST\$\$}"      # 去掉前缀
        param="${param%\$\$LIST\$\$}"    # 去掉后缀
        # 对于包含特殊字符的参数，需要加引号
        CMD+=("'$param'")
        DISPLAY_CMD+="  '$param' \\"$'\n'
    else
        # 普通参数直接添加
        CMD+=("$raw")
        DISPLAY_CMD+="  $raw \\"$'\n'
    fi
done

# 显示命令
echo "$DISPLAY_CMD"
echo "----------------------------------------"

# 保存命令到文件
COMMAND_FILE="$SCRIPT_DIR/last_training_command.sh"
echo -e "${BLUE}💾 保存命令到: $COMMAND_FILE${NC}"
{
    echo "#!/bin/bash"
    echo "# VERL RL训练命令 - 生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "# 设置环境变量"
    echo "export USE_SGLANG=$USE_SGLANG"
    echo "export NCCL_DEBUG=$NCCL_DEBUG"
    echo "export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
    echo ""
    echo "# 执行训练命令"
    echo -n "python $VERL_MAIN_SCRIPT"
    echo " \\"
    echo "  --config-path=config \\"
    echo "  --config-name=ppo_trainer.yaml \\"
    for raw in "${PARAMS[@]}"; do
        if [[ -z "$raw" ]]; then
            continue
        fi
        if [[ $raw == \$\$LIST\$\$* && $raw == *\$\$LIST\$\$ ]]; then
            param="${raw#\$\$LIST\$\$}"
            param="${param%\$\$LIST\$\$}"
            echo "  '$param' \\"
        else
            echo "  $raw \\"
        fi
    done
    echo ""
} > "$COMMAND_FILE"
chmod +x "$COMMAND_FILE"

echo -e "${GREEN}✅ 命令已保存，可以通过以下方式手动执行：${NC}"
echo "  bash $COMMAND_FILE"
echo ""

# 显示即将执行的命令（简化版）
echo -e "${YELLOW}🚀 即将执行训练命令${NC}"
echo -e "${YELLOW}提示: 如果命令执行失败，请检查参数是否正确${NC}"
echo ""

# 执行命令
echo -e "${GREEN}开始执行...${NC}"
echo "=========================================="

# 构建完整的命令字符串用于执行
FULL_CMD="python $VERL_MAIN_SCRIPT --config-path=config --config-name=ppo_trainer.yaml"

for raw in "${PARAMS[@]}"; do
    if [[ -z "$raw" ]]; then
        continue
    fi
    
    if [[ $raw == \$\$LIST\$\$* && $raw == *\$\$LIST\$\$ ]]; then
        # 去掉占位符
        param="${raw#\$\$LIST\$\$}"
        param="${param%\$\$LIST\$\$}"
        # 添加参数（带引号）
        FULL_CMD="$FULL_CMD '$param'"
    else
        # 普通参数
        FULL_CMD="$FULL_CMD $raw"
    fi
done

# 显示最终要执行的命令（简化版）
echo ""
echo -e "${CYAN}即将执行的命令：${NC}"
echo "----------------------------------------"
echo "$FULL_CMD"
echo "----------------------------------------"
echo ""

# 确认执行
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    开始执行VERL训练${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 执行命令 - 使用exec替换当前shell进程
# 这确保所有输出都直接显示在终端
exec bash -c "$FULL_CMD"