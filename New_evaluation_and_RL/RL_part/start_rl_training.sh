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

# 2. 检查Evaluation API代理（如果配置为evaluation_api模式）
MODEL_MODE=$(python3 -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
mode = config.get('model', {}).get('mode', 'evaluation_api')
print(mode)
" 2>/dev/null || echo "evaluation_api")

if [ "$MODEL_MODE" = "evaluation_api" ]; then
    echo -e "${BLUE}🔍 检查Evaluation API代理...${NC}"
    EVAL_PORT=$(python3 -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
port = config.get('services', {}).get('evaluation_api_proxy', {}).get('port', 5010)
print(port)
" 2>/dev/null || echo "5010")
    
    if ! lsof -i :$EVAL_PORT > /dev/null 2>&1; then
        echo -e "${RED}❌ Evaluation API代理未运行 (端口 $EVAL_PORT)${NC}"
        echo -e "${YELLOW}请先启动Evaluation API代理:${NC}"
        echo -e "${YELLOW}  cd $SCRIPT_DIR/../servers_and_proxy${NC}"
        echo -e "${YELLOW}  bash start_evaluation_api_proxy.sh${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Evaluation API代理运行正常 (端口 $EVAL_PORT)${NC}"
    fi
fi

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
echo -e "${BLUE}测试ScoreFlow奖励计算...${NC}"
REWARD_TEST_RESULT=$(python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
try:
    from scoreflow_reward_client import compute_score
    test_workflow = '''
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.custom(instruction='Solve the problem.')
        return solution
'''
    score = compute_score('gsm8k', test_workflow, 'default', {'test_cases': [0], 'data_path': 'Processed_dataset/gsm8k/test.jsonl'})
    print(f'成功! 测试分数: {score:.3f}')
except Exception as e:
    print(f'失败: {str(e)[:100]}')
" 2>&1)

if [[ "$REWARD_TEST_RESULT" == *"成功"* ]]; then
    echo -e "${GREEN}✅ ScoreFlow奖励计算测试: $REWARD_TEST_RESULT${NC}"
else
    echo -e "${YELLOW}⚠️ ScoreFlow奖励计算测试: $REWARD_TEST_RESULT${NC}"
    echo -e "${YELLOW}   这可能影响训练过程，请确保scoreflow_reward_client.py配置正确${NC}"
fi

# ============================================
# 参数验证和计算
# ============================================
echo ""
echo -e "${CYAN}========== 参数验证和计算 ==========${NC}"

# 验证参数约束并计算相关值
PARAM_VALIDATION=$(python3 << 'EOF'
import yaml
import sys
from pathlib import Path

# 加载配置
config_file = '$CONFIG_FILE'
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

# 获取RL训练配置
rl_config = config.get('rl_training', {})

# 提取关键参数
train_batch_size = rl_config['data']['train_batch_size']
ppo_mini_batch_size = rl_config['actor']['ppo_mini_batch_size']
ppo_micro_batch_size = rl_config['actor']['ppo_micro_batch_size_per_gpu']
tensor_model_parallel_size = rl_config['rollout']['tensor_model_parallel_size']
n_gpus_per_node = rl_config['trainer']['n_gpus_per_node']
rollout_n = rl_config['rollout']['n']  # 每个prompt生成的响应数量

# ScoreFlow配置
max_wf_data_pair = config['services']['scoreflow_reward'].get('max_wf_data_pair_running', 5)

# 计算派生参数
data_parallel_size = n_gpus_per_node // tensor_model_parallel_size
real_train_batch_size = train_batch_size * rollout_n
gradient_accumulation_steps = ppo_mini_batch_size // ppo_micro_batch_size

# 默认test_cases数量（从data_generation配置读取）
default_test_cases = config.get('data_generation', {}).get('default_test_cases_per_entry', 5)

print("【参数计算】")
print(f"  GPU总数: {n_gpus_per_node}")
print(f"  张量并行度(TP): {tensor_model_parallel_size}")
print(f"  数据并行度(DP): {data_parallel_size}")
print(f"  训练批次大小: {train_batch_size}")
print(f"  每个prompt生成: {rollout_n}个响应")
print(f"  真实批次大小: {real_train_batch_size} = {train_batch_size} × {rollout_n}")
print(f"  PPO mini批次: {ppo_mini_batch_size}")
print(f"  PPO micro批次: {ppo_micro_batch_size}")
print(f"  梯度累积步数: {gradient_accumulation_steps}")
print()

print("【数据流分析】")
print(f"  每个prompt → 生成{rollout_n}个workflow")
print(f"  每个workflow → 评估{default_test_cases}个test cases (默认)")
print(f"  总计: 每个prompt产生 {rollout_n * default_test_cases} 个(workflow,test_case)对")
print(f"  并发限制: 最多{max_wf_data_pair}个(workflow,test_case)对同时执行")
print()

# 验证约束
errors = []
warnings = []

# 约束1: GPU数量必须能被TP整除
if n_gpus_per_node % tensor_model_parallel_size != 0:
    errors.append(f"GPU数量({n_gpus_per_node})必须能被tensor_model_parallel_size({tensor_model_parallel_size})整除")
    errors.append(f"  建议: 修改tensor_model_parallel_size为 1, 2, 4 或 8")

# 约束2: 真实批次大小必须能被DP整除
if real_train_batch_size % data_parallel_size != 0:
    errors.append(f"真实批次大小({real_train_batch_size})必须能被数据并行度({data_parallel_size})整除")
    errors.append(f"  建议: 调整train_batch_size或rollout.n")

# 约束3: mini批次必须能被micro批次整除
if ppo_mini_batch_size % ppo_micro_batch_size != 0:
    errors.append(f"PPO mini批次({ppo_mini_batch_size})必须能被micro批次({ppo_micro_batch_size})整除")
    errors.append(f"  建议: 调整ppo_mini_batch_size为{ppo_micro_batch_size}的倍数")

# 约束4: train_batch_size必须>=ppo_mini_batch_size
if train_batch_size < ppo_mini_batch_size:
    errors.append(f"训练批次({train_batch_size})必须≥PPO mini批次({ppo_mini_batch_size})")
    errors.append(f"  建议: 增加train_batch_size或减少ppo_mini_batch_size")

# 约束5: micro批次检查
if ppo_micro_batch_size < n_gpus_per_node:
    warnings.append(f"PPO micro批次({ppo_micro_batch_size})小于GPU数量({n_gpus_per_node})，可能导致GPU利用率低")

# 输出验证结果
if errors:
    print("【❌ 参数约束错误】")
    for error in errors:
        print(f"  {error}")
    sys.exit(1)
else:
    print("【✅ 参数约束验证】")
    print(f"  ✓ GPU数量可被TP整除: {n_gpus_per_node} % {tensor_model_parallel_size} = 0")
    print(f"  ✓ 批次大小可被DP整除: {real_train_batch_size} % {data_parallel_size} = 0")
    print(f"  ✓ Mini批次可被Micro批次整除: {ppo_mini_batch_size} % {ppo_micro_batch_size} = 0")
    print(f"  ✓ 训练批次≥PPO mini批次: {train_batch_size} ≥ {ppo_mini_batch_size}")

if warnings:
    print("\n【⚠️ 警告】")
    for warning in warnings:
        print(f"  {warning}")
EOF
)

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
TRAINING_PARAMS=$(python3 << 'EOF'
import yaml
import sys
from pathlib import Path

# 加载配置
config_file = '$CONFIG_FILE'
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

# 获取project_root
project_root = Path(config.get('project_root', '$PROJECT_ROOT'))

# 获取RL训练配置
rl_config = config.get('rl_training', {})

# 构建参数列表
params = []

# 数据配置
data_config = rl_config.get('data', {})
train_files = data_config.get('train_files')
test_files = data_config.get('test_files')

# 构建数据文件的完整路径
if train_files:
    train_path = project_root / train_files
    params.append(f'data.train_files="[\'{train_path}\']"')

if test_files:
    test_path = project_root / test_files
    params.append(f'data.val_files="[\'{test_path}\']"')

# 添加其他数据参数
params.append(f'data.train_batch_size={data_config.get("train_batch_size", 16)}')
params.append(f'data.max_prompt_length={data_config.get("max_prompt_length", 8192)}')
params.append(f'data.max_response_length={data_config.get("max_response_length", 8192)}')
params.append(f'data.filter_overlong_prompts={str(data_config.get("filter_overlong_prompts", True)).lower()}')
params.append(f'data.truncation="{data_config.get("truncation", "error")}"')

# 模型配置
model_config = rl_config.get('model', {})
model_path = model_config.get('base_model_path', '/nas/models/Qwen2.5-7B-Instruct')
params.append(f'actor_rollout_ref.model.path={model_path}')
params.append(f'actor_rollout_ref.model.enable_gradient_checkpointing={str(model_config.get("enable_gradient_checkpointing", True)).lower()}')
params.append(f'actor_rollout_ref.model.trust_remote_code={str(model_config.get("trust_remote_code", False)).lower()}')

# Actor配置
actor_config = rl_config.get('actor', {})
params.append(f'actor_rollout_ref.actor.optim.lr={actor_config.get("learning_rate", "5e-7")}')
params.append(f'actor_rollout_ref.actor.ppo_mini_batch_size={actor_config.get("ppo_mini_batch_size", 8)}')
params.append(f'actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu={actor_config.get("ppo_micro_batch_size_per_gpu", 2)}')
params.append(f'actor_rollout_ref.actor.use_kl_loss={str(actor_config.get("use_kl_loss", True)).lower()}')
params.append(f'actor_rollout_ref.actor.kl_loss_coef={actor_config.get("kl_loss_coef", 0.001)}')
params.append(f'actor_rollout_ref.actor.kl_loss_type="{actor_config.get("kl_loss_type", "low_var_kl")}"')
params.append(f'actor_rollout_ref.actor.entropy_coeff={actor_config.get("entropy_coeff", 0)}')
params.append(f'actor_rollout_ref.actor.use_torch_compile={str(actor_config.get("use_torch_compile", False)).lower()}')

# Actor Checkpoint配置
checkpoint_config = actor_config.get('checkpoint', {})
if checkpoint_config:
    save_contents = checkpoint_config.get('save_contents', ['model', 'optimizer', 'extra'])
    load_contents = checkpoint_config.get('load_contents', save_contents)
    # 格式化为字符串列表
    save_contents_str = '[' + ','.join([f'"{item}"' for item in save_contents]) + ']'
    load_contents_str = '[' + ','.join([f'"{item}"' for item in load_contents]) + ']'
    params.append(f'actor_rollout_ref.actor.checkpoint.save_contents=\'{save_contents_str}\'')
    params.append(f'actor_rollout_ref.actor.checkpoint.load_contents=\'{load_contents_str}\'')

# Rollout配置
rollout_config = rl_config.get('rollout', {})
params.append(f'actor_rollout_ref.rollout.tensor_model_parallel_size={rollout_config.get("tensor_model_parallel_size", 2)}')
params.append(f'actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu={rollout_config.get("log_prob_micro_batch_size_per_gpu", 2)}')
params.append(f'actor_rollout_ref.rollout.n={rollout_config.get("n", 2)}')
params.append(f'actor_rollout_ref.rollout.name="{rollout_config.get("name", "sglang")}"')
params.append(f'actor_rollout_ref.rollout.gpu_memory_utilization={model_config.get("gpu_memory_utilization", 0.5)}')
params.append(f'actor_rollout_ref.hybrid_engine={str(rollout_config.get("hybrid_engine", True)).lower()}')

# Reference模型配置
ref_config = rl_config.get('ref', {})
params.append(f'actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu={ref_config.get("log_prob_micro_batch_size_per_gpu", 2)}')
params.append(f'actor_rollout_ref.ref.use_torch_compile={str(ref_config.get("use_torch_compile", False)).lower()}')

# Critic配置（如果存在）
critic_config = rl_config.get('critic', {})
if critic_config:
    critic_checkpoint = critic_config.get('checkpoint', {})
    if critic_checkpoint:
        save_contents = critic_checkpoint.get('save_contents', ['model', 'optimizer', 'extra'])
        load_contents = critic_checkpoint.get('load_contents', save_contents)
        save_contents_str = '[' + ','.join([f'"{item}"' for item in save_contents]) + ']'
        load_contents_str = '[' + ','.join([f'"{item}"' for item in load_contents]) + ']'
        params.append(f'critic.checkpoint.save_contents=\'{save_contents_str}\'')
        params.append(f'critic.checkpoint.load_contents=\'{load_contents_str}\'')

# 算法配置
algorithm_config = rl_config.get('algorithm', {})
params.append(f'algorithm.adv_estimator="{algorithm_config.get("adv_estimator", "grpo")}"')
params.append(f'algorithm.use_kl_in_reward={str(algorithm_config.get("use_kl_in_reward", False)).lower()}')

# 训练器配置
trainer_config = rl_config.get('trainer', {})
params.append(f'trainer.total_epochs={trainer_config.get("total_epochs", 3)}')
params.append(f'trainer.n_gpus_per_node={trainer_config.get("n_gpus_per_node", 8)}')
params.append(f'trainer.nnodes={trainer_config.get("nnodes", 1)}')
params.append(f'trainer.save_freq={trainer_config.get("save_freq", 10)}')
params.append(f'trainer.test_freq={trainer_config.get("test_freq", 2)}')
params.append(f'trainer.critic_warmup={trainer_config.get("critic_warmup", 0)}')
params.append(f'trainer.project_name="{trainer_config.get("project_name", "verl_grpo_h100_test")}"')
params.append(f'trainer.experiment_name="{trainer_config.get("experiment_name", "qwen2.5_7b_h100_8gpu_test")}"')

# Checkpoint管理配置
max_ckpt_num = trainer_config.get('max_ckpt_num', 3)
if max_ckpt_num is not None:
    params.append(f'trainer.max_ckpt_num={max_ckpt_num}')
params.append(f'trainer.save_on_each_node={str(trainer_config.get("save_on_each_node", False)).lower()}')

# 日志配置
logger_config = trainer_config.get('logger', ['console'])
logger_str = '["' + '","'.join(logger_config) + '"]' if isinstance(logger_config, list) else '["console"]'
params.append(f'trainer.logger=\'{logger_str}\'')

# 日志频率配置
log_freq = trainer_config.get('log_freq', 1)
params.append(f'trainer.log_freq={log_freq}')

log_to_wandb_every_n_steps = trainer_config.get('log_to_wandb_every_n_steps', 1)
params.append(f'trainer.log_to_wandb_every_n_steps={log_to_wandb_every_n_steps}')

# WandB配置
wandb_config = trainer_config.get('wandb_config', {})
if wandb_config and 'wandb' in logger_config:
    if wandb_config.get('entity'):
        params.append(f'trainer.wandb_entity="{wandb_config["entity"]}"')
    if wandb_config.get('tags'):
        tags_str = '[' + ','.join([f'"{tag}"' for tag in wandb_config['tags']]) + ']'
        params.append(f'trainer.wandb_tags=\'{tags_str}\'')
    if wandb_config.get('notes'):
        params.append(f'trainer.wandb_notes="{wandb_config["notes"]}"')
    params.append(f'trainer.wandb_save_code={str(wandb_config.get("save_code", True)).lower()}')
    params.append(f'trainer.wandb_log_model={str(wandb_config.get("log_model", False)).lower()}')

# 检查点目录
checkpoint_dir = trainer_config.get('default_local_dir', 'rl_out/checkpoints')
if not Path(checkpoint_dir).is_absolute():
    checkpoint_dir = project_root / checkpoint_dir
params.append(f'++trainer.default_local_dir={checkpoint_dir}')

# 奖励配置
reward_config = rl_config.get('reward', {})
params.append(f'++reward_model.reward_manager="{reward_config.get("reward_manager", "prime")}"')

# 自定义奖励函数
custom_reward = reward_config.get('custom_reward_function', {})
if custom_reward.get('enabled', False):
    reward_path = custom_reward.get('path')
    if reward_path:
        reward_path = project_root / reward_path
        params.append(f'++custom_reward_function.path={reward_path}')
        params.append(f'++custom_reward_function.name={custom_reward.get("name", "compute_score")}')

# 输出参数
print(' \\\n    '.join(params))
EOF
)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 解析配置失败${NC}"
    exit 1
fi

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

# 构建完整的训练命令
TRAIN_CMD="python $VERL_MAIN_SCRIPT --config-path=config --config-name='ppo_trainer.yaml' $TRAINING_PARAMS"

echo -e "${BLUE}执行命令:${NC}"
echo "$TRAIN_CMD"
echo ""

# 执行训练
eval $TRAIN_CMD