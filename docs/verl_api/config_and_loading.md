# verl 配置与环境加载机制

> **核心问题**：verl 是如何知道环境叫什么名字、路径在哪、接口是什么的？
>
> **简答**：通过 **config.yaml + Python 动态导入** 机制

---

## 目录

1. [配置文件架构](#1-配置文件架构)
2. [环境发现机制](#2-环境发现机制)
3. [Tool 加载流程](#3-tool-加载流程)
4. [数据路径配置](#4-数据路径配置)
5. [Generation Manager 配置](#5-generation-manager-配置)
6. [完整配置示例](#6-完整配置示例)
7. [自定义环境接入清单](#7-自定义环境接入清单)

---

## 1. 配置文件架构

### 1.1 Hydra 多层配置系统

verl 使用 **Hydra** 配置框架，支持配置的层级组织和覆盖：

```yaml
# 主配置文件：examples/sglang_multiturn/config/gsm8k_multiturn_grpo.yaml
hydra:
  searchpath:
    - file://verl/trainer/config    # 搜索基础配置模板

defaults:
  - ppo_trainer                      # 继承基础 PPO trainer 配置
  - _self_                           # 当前文件配置优先级最高
```

### 1.2 配置层级结构

```
config/
├── ppo_trainer.yaml                 # 基础配置模板（verl/trainer/config/）
├── gsm8k_multiturn_grpo.yaml        # 任务特定配置
└── tool_config/
    ├── gsm8k_tool_config.yaml       # Tool 定义
    ├── search_tool_config.yaml
    └── sandbox_fusion_tool_config.yaml
```

---

## 2. 环境发现机制

### 2.1 不是"环境路径"，而是"组件路径"

**关键理解**：verl 不直接加载"环境"，而是通过配置加载各个**组件**：

| 组件 | 配置方式 | 加载时机 |
|------|---------|---------|
| **Data** | `data.train_files` | `RLHFDataset.__init__` |
| **Tools** | `actor_rollout_ref.rollout.multi_turn.tool_config_path` | `SglangRollout._initialize_tools` |
| **Reward Function** | Python import + `config.reward_manager.type` | `main.py` 中手动实例化 |
| **Generation Manager** | Python import（硬编码） | `RayGRPOTrainer.__init__` |

**没有统一的"环境配置"字段**，而是通过多个配置项分别指定各组件。

### 2.2 配置项详解

#### (1) 数据路径配置

```yaml
# 在 YAML 中
data:
  train_files: /path/to/train.parquet
  val_files: /path/to/val.parquet
  max_prompt_length: 1024
  max_response_length: 1024
  return_raw_chat: True

# 或在命令行覆盖
python -m verl.trainer.main_ppo \
    --config-name='gsm8k_multiturn_grpo' \
    data.train_files=$HOME/data/gsm8k/train.parquet \
    data.val_files=$HOME/data/gsm8k/test.parquet
```

**加载代码**（`main.py` 或 `ray_trainer.py`）：
```python
from verl.utils.dataset.rl_dataset import RLHFDataset

train_dataset = RLHFDataset(
    data_files=config.data.train_files,    # 从配置读取路径
    tokenizer=tokenizer,
    config=config.data,
)
```

#### (2) Tool 配置路径

```yaml
# 在 YAML 中
actor_rollout_ref:
  rollout:
    multi_turn:
      enable: True
      max_turns: 5
      tool_config_path: "./config/tool_config/gsm8k_tool_config.yaml"
```

**Tool 配置文件内容**（`gsm8k_tool_config.yaml`）：
```yaml
tools:
  - class_name: "verl.tools.gsm8k_tool.Gsm8kTool"  # ← Python 类路径
    config: {}                                      # ← Tool 初始化参数
    tool_schema:                                    # ← OpenAI function calling schema
      type: "function"
      function:
        name: "calc_gsm8k_reward"
        description: "A tool for calculating the reward of gsm8k."
        parameters:
          type: "object"
          properties:
            answer:
              type: "string"
              description: "The model's answer to the GSM8K math problem"
          required: ["answer"]
```

#### (3) Reward Manager 配置

```yaml
# 在 YAML 中
reward_manager:
  type: "match"    # 或 "naive", "custom_name"
```

**加载代码**（`main.py` 中）：
```python
reward_manager_name = config.reward_manager.get("type", "naive")

if reward_manager_name == 'match':
    reward_fn = RewardManager(tokenizer=tokenizer, num_examine=1, use_format_score=True)
elif reward_manager_name == 'custom_name':
    reward_fn = CustomRewardManager(...)
else:
    raise NotImplementedError
```

---

## 3. Tool 加载流程

### 3.1 完整流程图

```
启动训练
  ↓
main.py 读取 config.yaml
  ↓
config.actor_rollout_ref.rollout.multi_turn.tool_config_path
  ↓
SglangRollout._initialize_tools(config, tokenizer)
  ↓
OmegaConf.load(tool_config_path)  # 读取 tool_config.yaml
  ↓
遍历 tools 列表
  ↓
对每个 tool:
  1. 解析 class_name (例如 "verl.tools.gsm8k_tool.Gsm8kTool")
  2. 动态导入模块 (importlib.util)
  3. 获取类 (getattr(module, class_name))
  4. 实例化 tool_cls(config=..., tool_schema=...)
  ↓
返回 tool_schemas, tool_map, tool_call_parser
  ↓
在 Rollout 中使用 tool_map 执行 tool calls
```

### 3.2 关键代码（`sglang_rollout.py:_initialize_tools`）

```python
def _initialize_tools(self, config, tokenizer):
    """从配置初始化 tools"""

    # 1. 读取 tool_config_path
    if config.multi_turn.tool_config_path is None:
        return [], {}, None, [], None

    tools_config_file = config.multi_turn.tool_config_path  # ← 从配置获取
    tools_config = OmegaConf.load(tools_config_file)        # ← 加载 YAML

    # 2. 遍历 tools 列表
    tool_list = []
    for tool_config in tools_config.tools:
        cls_name = tool_config.class_name  # 例如 "verl.tools.gsm8k_tool.Gsm8kTool"

        # 3. 动态导入模块
        module_name, class_name = cls_name.rsplit(".", 1)  # ("verl.tools.gsm8k_tool", "Gsm8kTool")

        if module_name not in sys.modules:
            spec = importlib.util.find_spec(module_name)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        else:
            module = sys.modules[module_name]

        # 4. 获取类并实例化
        tool_cls = getattr(module, class_name)

        tool_schema = OpenAIFunctionToolSchema.model_validate(tool_config.tool_schema)
        tool = tool_cls(
            config=OmegaConf.to_container(tool_config.config, resolve=True),
            tool_schema=tool_schema,
        )
        tool_list.append(tool)

    # 5. 构建 tool_map 等返回值
    tool_schemas = [tool.get_openai_tool_schema().model_dump() for tool in tool_list]
    tool_map = {tool.name: tool for tool in tool_list}  # ← name → tool 实例的映射

    return tool_schemas, tool_map, ...
```

### 3.3 Tool 使用示例

当模型生成 tool call 后：

```python
# 在 Rollout 中
tool_call_result = tool_map[tool_name].execute(**tool_args)
```

**为什么这样设计？**
- ✅ **解耦**：Tool 定义与训练代码分离
- ✅ **灵活**：无需修改代码即可切换 tools
- ✅ **扩展**：新增 tool 只需添加 YAML 配置

---

## 4. 数据路径配置

### 4.1 Parquet 数据格式

verl 使用 **Parquet** 格式存储训练数据，必须包含以下字段：

```python
{
    'prompt': [{"role": "user", "content": "问题描述"}],  # List[Dict] - Chat 格式
    'extra_info': {
        'index': '0',                        # 样本唯一标识
        'category': 'qa',                    # 'qa' 或 'func_call'
        'problem': '具体问题文本',
        'tools': [...],                      # OpenAI function calling schema 列表
        'data_source': 'gsm8k',
        'ground_truth': '42',
        'model_mapping': {...},              # tool model 映射
        'tool_pricing': {...},               # tool 成本信息
        'cur_transfer_dir': '/tmp/transfer', # IPC 目录（func_call 需要）
        # ... 其他任务特定字段
    }
}
```

### 4.2 数据加载链路

```
Parquet 文件 (config.data.train_files)
  ↓
RLHFDataset.__init__
  ↓ copy_to_local() 下载到本地缓存
  ↓ datasets.Dataset.from_pandas() 读取
  ↓ tokenize + filter 预处理
  ↓
RLHFDataset.__getitem__(index)
  ↓ 返回 dict:
      - input_ids, attention_mask, position_ids  (Tensor)
      - index, category, problem, tools, ...     (从 extra_info 提取)
  ↓
collate_fn(batch) → DataProto
  ↓
传递给 GenerationManager.run_llm_loop()
```

### 4.3 关键代码

**RLHFDataset.__getitem__**（`rl_dataset.py:210`）：
```python
def __getitem__(self, item):
    row_dict = self.dataframe[item]  # ← 从 Parquet 读取的原始数据
    messages = self._build_messages(row_dict)

    # Tokenize
    input_ids = self.tokenizer.apply_chat_template(messages, ...)

    # 提取 extra_info 中的元数据
    index = row_dict.get("extra_info", {}).get("index", 0)
    tools_kwargs = row_dict.get("extra_info", {}).get("tools_kwargs", {})

    row_dict["input_ids"] = input_ids
    row_dict["index"] = index
    row_dict["tools_kwargs"] = tools_kwargs
    # ... 其他字段

    return row_dict  # ← 返回的 dict 会被 collate_fn 处理成 DataProto
```

---

## 5. Generation Manager 配置

### 5.1 ToolOrchestra 的特殊处理

**问题**：ToolOrchestra 使用自定义的 `LLMGenerationManager`，但配置中**没有** `generation_manager` 字段！

**原因**：`LLMGenerationManager` 是**硬编码导入**的，不通过配置加载：

```python
# recipe/algo/grpo_ray_trainer_quick3.py:354

from lead_agent.llm_agent.generation_quick3 import LLMGenerationManager

# 直接在代码中创建
generation_manager = LLMGenerationManager(
    tokenizer=self.tokenizer,
    actor_rollout_wg=self.actor_rollout_wg,
    config=gen_config,  # ← 只传递配置参数，不指定类路径
)
```

### 5.2 为什么不配置化？

对比标准 verl 的做法：

| 标准 verl | ToolOrchestra |
|----------|---------------|
| 使用 `SglangRollout.generate_sequences()` | 自定义 `LLMGenerationManager.run_llm_loop()` |
| 通过 config.rollout.name 指定类型 | 硬编码导入 |
| 环境逻辑在 Rollout Worker 内 | 环境逻辑在 Generation Manager 内 |

**ToolOrchestra 的设计选择**：
- 因为需要**复杂的多轮交互逻辑**（tool calling, IPC with tau2, cost tracking）
- 所以将 Generation Manager 作为一个**固定的业务逻辑层**
- 只通过 `gen_config` 传递参数，不支持切换实现

### 5.3 标准 verl 的 Rollout 配置

标准 verl 通过 `config.actor_rollout_ref.rollout.name` 指定 Rollout 类型：

```yaml
actor_rollout_ref:
  rollout:
    name: sglang        # ← 对应 SglangRollout
    # 或 name: vllm     # ← 对应 VLLMRollout
```

**加载代码**（`ray_trainer.py`）：
```python
from verl.workers.rollout.sglang_rollout import SglangRollout
from verl.workers.rollout.vllm_rollout import VLLMRollout

rollout_name = config.actor_rollout_ref.rollout.name

if rollout_name == 'sglang':
    rollout_cls = SglangRollout
elif rollout_name == 'vllm':
    rollout_cls = VLLMRollout
else:
    raise ValueError(f"Unknown rollout: {rollout_name}")

rollout_worker = rollout_cls(config=config.actor_rollout_ref.rollout, ...)
```

---

## 6. 完整配置示例

### 6.1 ToolOrchestra GSM8K 训练配置

**主配置**（`gsm8k_multiturn_grpo.yaml`）：
```yaml
hydra:
  searchpath:
    - file://verl/trainer/config

defaults:
  - ppo_trainer
  - _self_

# 数据配置
data:
  max_prompt_length: 1024
  max_response_length: 1024
  train_batch_size: 256
  return_raw_chat: True

# Rollout 配置
actor_rollout_ref:
  hybrid_engine: True
  rollout:
    name: sglang                    # ← Rollout 引擎类型
    multi_turn:
      enable: True                  # ← 启用多轮对话
      max_turns: 5
      format: qwen
      tool_config_path: "./config/tool_config/gsm8k_tool_config.yaml"  # ← Tool 配置路径

# Reward 配置
reward_manager:
  type: "match"                     # ← Reward Manager 类型

# 训练器配置
trainer:
  n_gpus_per_node: 8
  nnodes: 1
  total_epochs: 15
  save_freq: -1
  test_freq: 20
```

**Tool 配置**（`tool_config/gsm8k_tool_config.yaml`）：
```yaml
tools:
  - class_name: "verl.tools.gsm8k_tool.Gsm8kTool"  # ← Python 类路径
    config:                                         # ← Tool 初始化参数
      timeout: 10
    tool_schema:                                    # ← OpenAI schema
      type: "function"
      function:
        name: "calc_gsm8k_reward"
        description: "Calculate GSM8K reward"
        parameters:
          type: "object"
          properties:
            answer:
              type: "string"
              description: "Model's answer"
          required: ["answer"]
```

**启动脚本**（`run_qwen2.5-3b_gsm8k_multiturn.sh`）：
```bash
python3 -m verl.trainer.main_ppo \
    --config-path="$CONFIG_PATH" \
    --config-name='gsm8k_multiturn_grpo' \
    data.train_files=$HOME/data/gsm8k/train.parquet \         # ← 命令行覆盖
    data.val_files=$HOME/data/gsm8k/test.parquet \
    actor_rollout_ref.rollout.multi_turn.tool_config_path="$PROJECT_DIR/examples/sglang_multiturn/config/tool_config/gsm8k_tool_config.yaml" \
    trainer.project_name='gsm8k_async_rl' \
    trainer.experiment_name='qwen2.5-3b_function_rm-gsm8k'
```

### 6.2 配置参数传递链路

```
命令行参数
  ↓
main.py: @hydra.main(config_path="...", config_name="...")
  ↓
Hydra 合并配置（defaults + YAML + 命令行覆盖）
  ↓
config 对象（OmegaConf.DictConfig）
  ↓
传递给各组件:
  - RLHFDataset(config=config.data)
  - RayGRPOTrainer(config=config)
    ↓ trainer.init_workers()
      ↓ ActorRolloutRefWorker(config=config.actor_rollout_ref)
        ↓ SglangRollout._initialize_tools(config=config.actor_rollout_ref.rollout)
          ↓ 加载 tool_config.yaml
  - RewardManager (根据 config.reward_manager.type 实例化)
```

---

## 7. 自定义环境接入清单

### 7.1 需要配置的内容

| 配置项 | 配置方式 | 示例 |
|--------|---------|------|
| **数据路径** | `data.train_files` | `$HOME/data/my_task/train.parquet` |
| **Tool 配置** | `actor_rollout_ref.rollout.multi_turn.tool_config_path` | `"./config/tool_config/my_tool_config.yaml"` |
| **Reward 类型** | `reward_manager.type` + 代码实现 | `"my_custom_reward"` |
| **模型路径** | `actor_rollout_ref.model.path` | `"meta-llama/Llama-3-8B"` |
| **Rollout 引擎** | `actor_rollout_ref.rollout.name` | `"sglang"` 或 `"vllm"` |

### 7.2 需要实现的代码

#### (1) 准备 Parquet 数据

**必需字段**：
```python
{
    'prompt': [...],           # Chat 格式的 prompt
    'extra_info': {
        'index': str,          # 唯一标识
        'category': str,       # 'qa' 或 'func_call'
        'problem': str,        # 问题文本
        'tools': list,         # Tool schemas (可选)
        'data_source': str,
        'ground_truth': Any,
        # ... 任务特定字段
    }
}
```

**生成脚本示例**：
```python
import pandas as pd

data = []
for i, item in enumerate(your_dataset):
    data.append({
        'prompt': [{"role": "user", "content": item['question']}],
        'extra_info': {
            'index': str(i),
            'category': 'qa',
            'problem': item['question'],
            'data_source': 'my_task',
            'ground_truth': item['answer'],
            'tools': [...]  # 如果需要 tool calling
        }
    })

df = pd.DataFrame(data)
df.to_parquet('train.parquet', index=False)
```

#### (2) 实现自定义 Tool

**文件位置**：`verl/tools/my_tool.py`

```python
from verl.tools.base import BaseTool

class MyCustomTool(BaseTool):
    """自定义 Tool 实现"""

    def __init__(self, config, tool_schema):
        super().__init__(config, tool_schema)
        self.timeout = config.get('timeout', 10)

    def execute(self, **kwargs):
        """执行 tool 并返回结果"""
        # 实现 tool 逻辑
        result = self._call_external_api(**kwargs)
        return result

    @property
    def name(self):
        return self.tool_schema.function.name
```

**Tool 配置**（`my_tool_config.yaml`）：
```yaml
tools:
  - class_name: "verl.tools.my_tool.MyCustomTool"
    config:
      timeout: 10
    tool_schema:
      type: "function"
      function:
        name: "my_tool_function"
        description: "Description of my tool"
        parameters:
          type: "object"
          properties:
            param1:
              type: "string"
              description: "Parameter description"
          required: ["param1"]
```

#### (3) 实现自定义 Reward Manager

**文件位置**：在你的训练主脚本中（例如 `main.py`）

```python
class MyCustomRewardManager:
    def __init__(self, tokenizer, **kwargs):
        self.tokenizer = tokenizer
        # 初始化参数

    def __call__(self, data: DataProto, global_step: int) -> torch.Tensor:
        """计算 reward

        Args:
            data: DataProto, 包含 batch 和 non_tensor_batch
            global_step: 当前训练步数

        Returns:
            reward_tensor: shape (batch_size, seq_len), 通常只有最后一个 token 非零
        """
        reward_tensor = torch.zeros_like(data.batch['responses'], dtype=torch.float32)

        for i in range(len(data)):
            data_item = data[i]  # DataProtoItem

            # 从 non_tensor_batch 获取信息
            problem = data_item.non_tensor_batch['problem']
            ground_truth = data_item.non_tensor_batch['ground_truth']

            # 从 batch 获取生成的 response
            response_ids = data_item.batch['responses']
            response_text = self.tokenizer.decode(response_ids, skip_special_tokens=True)

            # 计算 reward
            score = self.compute_score(response_text, ground_truth)

            # Reward 只赋值给最后一个 token
            reward_tensor[i, 0] = score

        return reward_tensor

    def compute_score(self, response, ground_truth):
        # 实现 reward 计算逻辑
        pass
```

**在主脚本中注册**：
```python
# main.py

reward_manager_name = config.reward_manager.get("type", "naive")

if reward_manager_name == 'my_custom_reward':
    reward_fn = MyCustomRewardManager(tokenizer=tokenizer, ...)
elif reward_manager_name == 'naive':
    reward_fn = ...
else:
    raise NotImplementedError(f"Unknown reward manager: {reward_manager_name}")

trainer = RayGRPOTrainer(
    config=config,
    tokenizer=tokenizer,
    reward_fn=reward_fn,  # ← 传递给 trainer
    ...
)
```

#### (4) 编写配置文件

**文件位置**：`config/my_task.yaml`

```yaml
hydra:
  searchpath:
    - file://verl/trainer/config

defaults:
  - ppo_trainer
  - _self_

data:
  train_files: /path/to/my_task/train.parquet
  val_files: /path/to/my_task/val.parquet
  max_prompt_length: 1024
  max_response_length: 512
  return_raw_chat: True

actor_rollout_ref:
  model:
    path: meta-llama/Llama-3-8B
  rollout:
    name: sglang
    multi_turn:
      enable: True
      max_turns: 3
      tool_config_path: "./config/tool_config/my_tool_config.yaml"

reward_manager:
  type: "my_custom_reward"

trainer:
  n_gpus_per_node: 4
  nnodes: 1
  total_epochs: 10
  project_name: 'my_task_rl'
  experiment_name: 'llama3-8b-my-task'
```

#### (5) 启动训练

```bash
python -m verl.trainer.main_ppo \
    --config-path="./config" \
    --config-name="my_task"
```

---

## 8. ToolOrchestra 特殊设计说明

### 8.1 为什么 tau2 环境路径是硬编码的？

在 `generation_quick3.py:1064`，tau2 subprocess 启动命令是硬编码的：

```python
func_call_cmd = [
    'python',
    'rollout/tau2/cli.py',  # ← 硬编码路径！
    '--domain', cur_domain,
    '--agent-llm', 'train',
    ...
]
subprocess.Popen(func_call_cmd)
```

**原因**：
1. **ToolOrchestra 的特定架构**：tau2-bench 是一个独立的环境系统，通过 IPC 与训练进程通信
2. **简化设计**：tau2 作为固定的基础设施，不需要切换实现
3. **路径解析**：依赖 `REPO_PATH` 环境变量和当前工作目录

**如何自定义**：
- 如果要替换 tau2，需要修改 `generation_quick3.py` 的代码
- 或者实现一个新的 Generation Manager 类

### 8.2 环境信息从 Parquet 数据传递

关键字段在 `extra_info` 中：

```python
{
    'extra_info': {
        'category': 'func_call',              # ← 决定是否启动 tau2
        'index': 'airline____task_001',       # ← 包含 domain 信息
        'cur_transfer_dir': '/tmp/transfer',  # ← IPC 目录
        'tools': [...],                       # ← Tool schemas
        ...
    }
}
```

**解析流程**：
```python
# generation_quick3.py:1050-1067

category = gen_batch.non_tensor_batch['category'][item_idx]  # ← 从数据读取

if category == 'func_call':
    item_index = gen_batch.non_tensor_batch['index'][item_idx]
    cur_domain = item_index.split('____')[0]  # ← 提取 domain（例如 'airline'）

    func_call_cmd = ['python', 'rollout/tau2/cli.py', '--domain', cur_domain, ...]
    subprocess.Popen(func_call_cmd)  # ← 启动对应 domain 的 tau2 环境
```

---

## 9. 总结

### 9.1 核心机制

| 问题 | 答案 |
|------|------|
| verl 如何知道环境名称？ | 通过 **config.actor_rollout_ref.rollout.name** 指定 Rollout 类型 |
| verl 如何知道环境路径？ | **不存在统一的环境路径配置**，各组件分别配置 |
| verl 如何知道接口？ | Tool 通过 **class_name** 动态导入，必须实现 `BaseTool` 接口 |
| 数据路径在哪配置？ | `data.train_files` 和 `data.val_files` |
| Reward 函数在哪配置？ | `reward_manager.type` + 在主脚本中实例化 |

### 9.2 配置 vs 代码

| 通过配置指定 | 通过代码实现 |
|-------------|-------------|
| 数据文件路径 | Reward Manager 实例化逻辑 |
| Tool 类路径 + schema | Tool 类实现 |
| Rollout 引擎类型 | Generation Manager（ToolOrchestra 硬编码） |
| 模型路径 | 环境逻辑（如 tau2 subprocess 启动） |

### 9.3 设计理念

**verl 的设计哲学**：
- ✅ **组件化**：各功能模块独立配置和实现
- ✅ **灵活性**：通过 Python class_name 支持任意自定义实现
- ✅ **解耦**：配置与代码分离，便于实验迭代
- ⚠️ **非标准化**：没有统一的"环境配置"规范，需要根据任务自行设计

**ToolOrchestra 的特殊之处**：
- 在 verl 基础上增加了 **Generation Manager** 层
- 将多轮对话、tool calling、IPC 通信封装在 Generation Manager 内
- tau2-bench 作为**独立进程**运行，通过文件系统 IPC 通信

---

## 10. 快速参考

### 配置文件模板

```yaml
# config/my_task.yaml
hydra:
  searchpath: [file://verl/trainer/config]
defaults: [ppo_trainer, _self_]

data:
  train_files: /path/to/train.parquet
  val_files: /path/to/val.parquet

actor_rollout_ref:
  model.path: your-model-path
  rollout:
    name: sglang
    multi_turn:
      tool_config_path: "./config/tool_config/my_tool.yaml"

reward_manager:
  type: "my_reward"
```

### Tool 配置模板

```yaml
# config/tool_config/my_tool.yaml
tools:
  - class_name: "verl.tools.my_tool.MyTool"
    config: {}
    tool_schema:
      type: "function"
      function:
        name: "tool_name"
        description: "Tool description"
        parameters:
          type: "object"
          properties:
            param1: {type: "string", description: "..."}
          required: ["param1"]
```

### 启动命令模板

```bash
python -m verl.trainer.main_ppo \
    --config-path="./config" \
    --config-name="my_task" \
    data.train_files=/path/to/data.parquet
```

---

**相关文档**：
- [环境对接完整指南](./environment_integration.md)
- [数据接口规范](./data_interface.md)
- [Reward 接口规范](./reward_interface.md)
- [训练配置规范](./training_config.md)
