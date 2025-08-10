# VERL格式数据生成计划

## 1. 项目目标
创建VERL格式的训练数据，用于工作流生成模型的强化学习训练：
- 上游模型：根据prompt生成工作流代码
- 下游模型：执行生成的工作流并产生结果
- 奖励函数：基于下游执行结果的准确率计算奖励

## 2. 数据结构设计

### 2.1 Parquet文件结构
创建包含以下字段的parquet文件：
```
data_source: str - 数据集名称 (如 "gsm8k", "mbpp")
prompt: str - HuggingFace chat_template格式的提示
ability: str - 任务类别 (如 "math_reasoning", "code_generation") 
reward_model: dict - 包含ground_truth字段的字典
extra_info: dict - 额外信息字段
```

### 2.2 字段详细设计
- **data_source**: 使用现有基准测试名称，与ScoreFlow/scripts/目录对应
- **prompt**: 构建工作流生成提示，包含：
  - 任务描述
  - 少量示例问题
  - 工作流生成要求
- **ability**: 根据data_source映射到具体能力类别
- **reward_model.ground_truth**: 存储测试用的数据索引列表
- **extra_info**: 记录原始问题索引、难度等元信息

### 2.3 训练/测试集分割策略
- **训练集**: 用于VERL强化学习训练的prompt数据
- **测试集**: 用于reward计算的问题索引
- **分割比例**: 建议80%训练，20%测试
- **确保不重叠**: 训练prompt中使用的问题索引不能出现在测试集中

## 3. 严格遵循现有系统架构

### 3.1 **必须严格按照现有脚本操作**
所有数据生成、执行和奖励计算必须完全复用现有系统的方法：

#### A. 数据生成 - 严格按照 `workflow_generator.py`
```python
# 1. 使用相同的Handler加载机制
handler = get_benchmark_handler(benchmark_name, dataset_path)

# 2. 使用相同的prompt构建逻辑
start_prompt, end_prompt, system_prompt, meta_prompts = handler._load_prompt_templates()
problem_text = handler.get_prompt_text(data_indices)

# 3. 使用相同的API调用方式
response = await call_openai_compatible_api(api_config, messages)
```

#### B. 工作流执行 - 严格按照 `workflow_executor.py`
```python
# 1. 读取元数据文件
meta_path = workflow_path.replace('.py', '.meta.json')
with open(meta_path, 'r') as f:
    meta = json.load(f)

# 2. 使用相同的Handler验证流程
handler = get_benchmark_handler(benchmark_name, dataset_path)
verification_data = handler.get_verification_data(verification_index)
is_correct = handler.judge(execution_result, verification_data)
```

#### C. 批次调度 - 严格按照 `master_runner.py`
```python
# 1. 使用相同的任务创建逻辑
all_tasks = create_generation_tasks(total_problems, min_sample_size, max_sample_size)

# 2. 使用相同的批次处理方式
for i in range(num_batches):
    batch_tasks = all_tasks[i * batch_size : (i + 1) * batch_size]
    start_index = i * batch_size
```

### 3.2 奖励函数设计

#### 函数结构 - 完全复用现有执行逻辑
```python
def compute_workflow_reward(generated_workflow, test_data_indices, data_source) -> float:
    """
    严格按照 workflow_executor.py 的逻辑计算奖励
    """
    # 1. 创建临时的.py和.meta.json文件 (复用executor的文件结构)
    # 2. 调用 workflow_executor.py 的 execute_and_verify 函数
    # 3. 解析CSV结果文件获取准确率
    # 4. 返回奖励分数
```

#### 评估流程 - 严格复用现有组件
1. **Handler加载**: 使用 `get_benchmark_handler()` 
2. **环境准备**: 复用 `convert_config_for_metagpt()` 和执行环境设置
3. **工作流执行**: 复用 `handler.build_executable_script()` 和 `exec()` 逻辑
4. **结果验证**: 复用 `handler.judge()` 方法
5. **结果记录**: 复用 `save_result_to_csv()` 格式

## 4. 实施步骤

### 4.1 创建数据生成脚本 (generate_verl_data.py)
```python
# 核心原则：完全复用现有系统的方法
class VerlDataGenerator:
    def __init__(self, config):
        # 严格按照 workflow_generator.py 初始化Handler
        self.handler = get_benchmark_handler(config.benchmark, config.dataset_path)
        
    def generate_training_prompts(self):
        # 复用 workflow_generator.py 的 _construct_generation_prompt
        pass
        
    def split_train_test_data(self, total_problems):
        # 按照 master_runner.py 的 create_generation_tasks 逻辑分割
        pass
```

### 4.2 创建奖励函数 (workflow_reward.py)
```python
# 核心原则：完全复用 workflow_executor.py 的执行逻辑
async def compute_workflow_reward(workflow_code, test_indices, benchmark_name, dataset_path, exec_llm_config):
    # 1. 创建临时工作流文件 (复用 _save_workflow_files 格式)
    # 2. 调用 execute_and_verify 逻辑 (完全相同的函数)
    # 3. 解析执行结果 (复用 save_result_to_csv 格式)
    # 4. 计算准确率奖励
```

### 4.3 配置文件设计
```json
{
    "benchmarks": {
        "gsm8k": {
            "ability": "math_reasoning",
            "dataset_path": "./data/gsm8k/train.jsonl",
            "total_problems": 7473,
            "train_ratio": 0.8
        },
        "mbpp": {
            "ability": "code_generation", 
            "dataset_path": "./data/mbpp/train.jsonl",
            "total_problems": 374,
            "train_ratio": 0.8
        }
    },
    "generation_config": {
        "min_sample_size": 2,
        "max_sample_size": 4,
        "batch_size": 10
    }
}
```

### 4.4 训练/测试集分割实现
```python
def create_train_test_split(total_problems, train_ratio=0.8):
    """
    严格按照 master_runner.py 的逻辑进行分割
    """
    # 1. 使用相同的随机打乱逻辑
    indices = list(range(total_problems))
    random.shuffle(indices)
    
    # 2. 按比例分割
    split_point = int(total_problems * train_ratio)
    train_indices = indices[:split_point]
    test_indices = indices[split_point:]
    
    # 3. 使用相同的任务创建逻辑
    train_tasks = create_generation_tasks_from_indices(train_indices, min_sample, max_sample)
    
    return train_tasks, test_indices
```

## 5. 文件结构
```
Test_FILE/verl_support/
├── plan.md                    # 本计划文件
├── math.py                    # 现有数学评估函数
├── generate_verl_data.py      # 数据生成脚本 (严格复用现有逻辑)
├── workflow_reward.py         # 工作流奖励函数 (严格复用executor逻辑)
├── config.json               # 配置文件
├── utils.py                  # 复用现有系统组件的工具函数
└── data/
    ├── gsm8k_verl_train.parquet    # GSM8K训练集VERL数据
    ├── gsm8k_verl_test.parquet     # GSM8K测试集数据索引
    ├── mbpp_verl_train.parquet     # MBPP训练集VERL数据
    └── mbpp_verl_test.parquet      # MBPP测试集数据索引
```

## 6. 关键约束与原则

### 6.1 **绝对约束**
- ✅ **必须复用**: `get_benchmark_handler()`, `_construct_generation_prompt()`, `execute_and_verify()`, `handler.judge()`
- ✅ **必须保持**: 文件结构(.py + .meta.json)、CSV结果格式、Handler接口
- ✅ **必须兼容**: 现有的API配置、LLM配置、工作空间结构

### 6.2 **数据一致性**
- 训练prompt生成必须使用与现有系统完全相同的模板和逻辑
- 测试数据验证必须使用与现有系统完全相同的judge方法
- 工作流执行环境必须与现有executor完全一致

### 6.3 **分割原则**
- 确保训练集和测试集完全不重叠
- 测试集大小足够进行可靠的奖励计算
- 训练集保持现有系统的prompt质量和多样性

## 7. 测试验证
- 生成小规模测试数据验证分割正确性
- 确保奖励函数与现有executor结果完全一致
- 验证训练/测试数据的不重叠性

请审批此更新计划，我将严格按照现有系统的方法实施。
