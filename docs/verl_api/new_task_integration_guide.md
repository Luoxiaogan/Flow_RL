# 新任务 RL 训练接入完整指南

> **文档定位**: 从零开始在新任务上进行 RL 训练，需要修改/创建的所有文件的详细清单

**适用场景**:
- ✅ 接入全新的任务类型（如新的数学推理、代码生成、工具调用任务）
- ✅ 基于 ToolOrchestra/verl 框架进行定制化开发
- ✅ 实现 multi-turn RL 训练

**前置阅读**:
- [环境集成指南](environment_integration.md)
- [数据接口规范](data_interface.md)
- [Reward 接口规范](reward_interface.md)
- [训练配置规范](training_config.md)

---

## 📋 修改清单概览

```
新任务接入修改点
├── 【必需】数据准备 (3个文件)
│   ├── 1. 数据预处理脚本
│   ├── 2. Parquet 数据文件
│   └── 3. Dataset 配置
│
├── 【必需】Reward 系统 (2-3个文件)
│   ├── 1. Reward 计分函数
│   ├── 2. RewardManager 注册
│   └── 3. (可选) 自定义 RewardManager
│
├── 【必需】训练配置 (2-3个文件)
│   ├── 1. 主配置文件 (YAML)
│   ├── 2. Tool 配置文件
│   └── 3. (可选) 环境配置
│
├── 【可选】Tool 实现 (2-4个文件)
│   ├── 1. Tool 类实现
│   ├── 2. Tool 注册
│   ├── 3. Tool Schema 定义
│   └── 4. Tool 配置 JSON
│
├── 【可选】Generation Manager (1-2个文件)
│   ├── 1. 自定义 Generation Manager
│   └── 2. 上下文管理逻辑
│
├── 【可选】Trainer 定制 (1个文件)
│   └── 1. 自定义 Trainer
│
└── 【必需】启动脚本 (1-2个文件)
    ├── 1. 训练启动脚本
    └── 2. (可选) 评估脚本
```

**统计**:
- 最少修改: **7个文件** (简单任务)
- 完整定制: **15-20个文件** (复杂 multi-turn 任务)

---

## 第一部分：数据准备【必需】

### 1.1 数据预处理脚本

**文件位置**: `examples/data_preprocess/your_task.py`

**作用**: 将原始数据转换为 verl 所需的 Parquet 格式

**参考文件**:
- `examples/data_preprocess/gsm8k_multiturn_w_tool.py` (multi-turn 数学任务)
- `examples/data_preprocess/aime2024_multiturn_w_tool.py` (AIME2024 任务)

**需要实现的内容**:

```python
"""
examples/data_preprocess/your_task.py
"""
import pandas as pd
import json
from pathlib import Path

def load_raw_data(data_path):
    """
    从原始数据源加载数据

    Returns:
        List[dict]: 原始数据列表
    """
    # TODO: 实现你的数据加载逻辑
    pass

def preprocess_item(item):
    """
    预处理单个数据项

    Args:
        item: 原始数据项

    Returns:
        dict: 符合 verl 格式的数据项
        {
            'prompt': List[dict],           # 必需：对话历史
            'reward_model': dict,            # 必需：Reward 所需信息
            'data_source': str,              # 必需：任务标识
            'id': str,                       # 可选：数据 ID
            'extra_info': dict,              # 可选：额外信息
        }
    """
    # 1. 构建 prompt (对话格式)
    prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": item['question']}
    ]

    # 2. 构建 reward_model (包含 ground truth 等信息)
    reward_model = {
        'ground_truth': item['answer'],
        'difficulty': item.get('difficulty', 'medium'),
        # 其他 Reward 计算需要的信息
    }

    # 3. 设置 data_source (任务标识，用于 Reward 路由)
    data_source = "your_task"

    # 4. (可选) 设置 ID
    item_id = item.get('id', str(hash(item['question'])))

    # 5. (可选) 额外信息
    extra_info = {
        'original_dataset': item.get('dataset', 'unknown'),
        'topic': item.get('topic', 'general'),
    }

    return {
        'prompt': prompt,
        'reward_model': reward_model,
        'data_source': data_source,
        'id': item_id,
        'extra_info': extra_info,
    }

def main():
    # 加载原始数据
    raw_data = load_raw_data("path/to/raw/data.json")

    # 预处理
    processed_data = [preprocess_item(item) for item in raw_data]

    # 转换为 DataFrame
    df = pd.DataFrame(processed_data)

    # 保存为 Parquet
    output_dir = Path("data/your_task/")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 分割 train/valid/test
    train_size = int(len(df) * 0.8)
    valid_size = int(len(df) * 0.1)

    train_df = df[:train_size]
    valid_df = df[train_size:train_size+valid_size]
    test_df = df[train_size+valid_size:]

    # 保存
    train_df.to_parquet(output_dir / "train.parquet", index=False)
    valid_df.to_parquet(output_dir / "valid.parquet", index=False)
    test_df.to_parquet(output_dir / "test.parquet", index=False)

    print(f"数据预处理完成:")
    print(f"  Train: {len(train_df)} samples")
    print(f"  Valid: {len(valid_df)} samples")
    print(f"  Test: {len(test_df)} samples")

if __name__ == "__main__":
    main()
```

**关键注意事项**:
1. **prompt 格式**: 必须是 List[dict]，每个 dict 包含 `role` 和 `content`
2. **reward_model**: 必须包含 `ground_truth` 字段，其他字段根据 Reward 函数需求
3. **data_source**: 用于 Reward 路由，必须与 Reward 函数中的匹配
4. **Parquet 格式**: 使用 `pandas.to_parquet()` 保存，设置 `index=False`

**验证数据**:
```python
# 验证脚本
import pandas as pd

df = pd.read_parquet("data/your_task/train.parquet")
print("数据字段:", df.columns.tolist())
print("样本数:", len(df))
print("\n第一个样本:")
print(df.iloc[0])

# 检查必需字段
assert 'prompt' in df.columns
assert 'reward_model' in df.columns
assert 'data_source' in df.columns

print("\n✅ 数据格式验证通过")
```

---

### 1.2 Parquet 数据文件

**文件位置**: `data/your_task/train.parquet`, `data/your_task/valid.parquet`

**作用**: 存储预处理后的训练数据

**格式要求**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `prompt` | List[dict] | ✅ | 对话历史，格式: `[{"role": "user", "content": "..."}]` |
| `reward_model` | dict | ✅ | Reward 计算所需信息，至少包含 `ground_truth` |
| `data_source` | str | ✅ | 任务标识，用于 Reward 路由 |
| `id` | str | ❌ | 数据 ID，用于追踪和调试 |
| `extra_info` | dict | ❌ | 额外信息，如难度、类别等 |

**示例数据**:
```python
{
    "prompt": [
        {"role": "system", "content": "You are a math expert."},
        {"role": "user", "content": "Solve: 2x + 5 = 13"}
    ],
    "reward_model": {
        "ground_truth": "4",
        "solution_steps": ["2x + 5 = 13", "2x = 8", "x = 4"],
        "difficulty": "easy"
    },
    "data_source": "algebra_task",
    "id": "algebra_001",
    "extra_info": {
        "topic": "linear_equations",
        "source_dataset": "custom_algebra"
    }
}
```

---

### 1.3 Dataset 配置

**文件位置**: 在主配置文件中（见第三部分 3.1）

**需要配置的内容**:

```yaml
# config/your_task_grpo.yaml 中的 data 部分
data:
  train_files:
    - data/your_task/train.parquet
  val_files:
    - data/your_task/valid.parquet

  train_batch_size: 512        # 训练 batch size
  val_batch_size: 1024         # 验证 batch size

  max_prompt_length: 4096      # 最大 prompt 长度
  max_response_length: 2048    # 最大 response 长度

  # 可选：采样权重
  train_sample_weight: null

  # 可选：Tokenizer 配置
  tokenizer_path: "path/to/tokenizer"
  tokenizer_type: "transformers"  # 或 "megatron"
```

**注意事项**:
1. `train_files` 和 `val_files` 可以指定多个文件
2. `max_prompt_length` 和 `max_response_length` 需要根据你的任务调整
3. 数据路径可以是相对路径（相对于工作目录）或绝对路径

---

## 第二部分：Reward 系统【必需】

### 2.1 Reward 计分函数

**文件位置**: `verl/utils/reward_score/your_task.py`

**作用**: 实现任务特定的 Reward 计算逻辑

**参考文件**:
- `verl/utils/reward_score/gsm8k.py` (数学任务)
- `verl/utils/reward_score/math.py` (通用数学)
- `verl/utils/reward_score/search_r1_like_qa_em.py` (问答任务)

**核心接口**:

```python
"""
verl/utils/reward_score/your_task.py
"""
import re
from typing import Union, Dict, Any

def compute_score(
    data_source: str,
    solution_str: str,
    ground_truth: Union[str, dict],
    extra_info: Dict[str, Any] = None,
    **kwargs
) -> float:
    """
    计算 Reward 分数

    Args:
        data_source: 任务标识（与数据中的 data_source 匹配）
        solution_str: 模型生成的解答字符串
        ground_truth: 标准答案（从 reward_model 字段传入）
        extra_info: 额外信息（从 extra_info 字段传入）
        **kwargs: 其他参数（如 tokenizer, num_examine 等）

    Returns:
        float: Reward 分数，通常 [0, 1] 或 {0, 1}

    注意:
        - 这个函数会被大量并行调用，务必保证线程安全
        - 避免使用全局状态
        - 如果计算失败，应该返回 0.0 而不是抛出异常
    """
    # ==================== 任务路由 ====================
    # 如果你的任务有多个子类型，可以在这里路由
    if data_source not in ["your_task", "your_task_v2"]:
        # 不是我的任务，返回 0.0
        return 0.0

    # ==================== 提取答案 ====================
    # 从模型生成的文本中提取答案
    try:
        # 方法1: 使用正则表达式
        # 假设模型输出格式: "...<answer>42</answer>..."
        answer_match = re.search(r'<answer>(.*?)</answer>', solution_str)
        if answer_match:
            predicted_answer = answer_match.group(1).strip()
        else:
            # 没有找到答案标签，可能模型没有按格式输出
            # 尝试其他提取方法或直接返回 0
            return 0.0

        # 方法2: 使用 LLM 辅助提取（适用于复杂格式）
        # predicted_answer = extract_answer_with_llm(solution_str)

    except Exception as e:
        # 提取失败，返回 0
        print(f"答案提取失败: {e}")
        return 0.0

    # ==================== 标准化答案 ====================
    # 将答案标准化，便于比较
    def normalize_answer(ans: str) -> str:
        # 去除首尾空格
        ans = ans.strip()

        # 转小写
        ans = ans.lower()

        # 去除标点符号（根据任务需求）
        ans = re.sub(r'[^\w\s]', '', ans)

        # 去除多余空格
        ans = ' '.join(ans.split())

        return ans

    pred_normalized = normalize_answer(predicted_answer)

    # 处理 ground_truth（可能是 str 或 dict）
    if isinstance(ground_truth, dict):
        # 如果 ground_truth 是字典，提取答案字段
        gt_answer = ground_truth.get('answer', ground_truth.get('ground_truth', ''))
    else:
        gt_answer = ground_truth

    gt_normalized = normalize_answer(str(gt_answer))

    # ==================== 评分逻辑 ====================

    # 简单的完全匹配
    if pred_normalized == gt_normalized:
        reward = 1.0
    else:
        reward = 0.0

    # 或者更复杂的评分逻辑
    # reward = compute_similarity(pred_normalized, gt_normalized)

    # ==================== 调试输出 ====================
    # 使用 num_examine 参数控制是否打印调试信息
    num_examine = kwargs.get('num_examine', 0)
    if num_examine > 0:
        print(f"=" * 80)
        print(f"Data Source: {data_source}")
        print(f"Solution String:\n{solution_str[:500]}...")
        print(f"\nExtracted Answer: {predicted_answer}")
        print(f"Ground Truth: {gt_answer}")
        print(f"Normalized Pred: {pred_normalized}")
        print(f"Normalized GT: {gt_normalized}")
        print(f"Reward: {reward}")
        print(f"=" * 80)

    return reward


# ==================== 辅助函数 ====================

def extract_answer_with_llm(solution_str: str) -> str:
    """
    使用 LLM 辅助提取答案（适用于复杂格式）

    注意：这会增加计算成本，谨慎使用
    """
    # TODO: 实现 LLM 辅助提取
    pass

def compute_similarity(pred: str, gt: str) -> float:
    """
    计算相似度（用于部分正确的场景）

    可以使用：
    - Levenshtein 距离
    - BLEU / ROUGE 分数
    - Embedding 相似度
    """
    # TODO: 实现相似度计算
    pass
```

**高级技巧**:

1. **多标准答案处理**:
```python
# 如果有多个正确答案
if isinstance(ground_truth, dict) and 'acceptable_answers' in ground_truth:
    acceptable = ground_truth['acceptable_answers']
    reward = 1.0 if pred_normalized in [normalize_answer(a) for a in acceptable] else 0.0
```

2. **数值答案处理**:
```python
# 对于数学题，使用数值比较
try:
    pred_num = float(pred_normalized)
    gt_num = float(gt_normalized)

    # 允许小误差
    if abs(pred_num - gt_num) < 1e-5:
        reward = 1.0
    else:
        reward = 0.0
except ValueError:
    # 不是数值，使用字符串比较
    reward = 1.0 if pred_normalized == gt_normalized else 0.0
```

3. **代码执行验证**:
```python
# 对于代码生成任务
def verify_code(code_str: str, test_cases: list) -> float:
    """执行代码并验证测试用例"""
    try:
        # 在沙箱中执行代码
        exec_globals = {}
        exec(code_str, exec_globals)

        # 运行测试用例
        passed = 0
        for test in test_cases:
            input_val = test['input']
            expected = test['output']
            actual = exec_globals['solution'](input_val)
            if actual == expected:
                passed += 1

        return passed / len(test_cases)
    except Exception:
        return 0.0
```

**注意事项**:
1. **线程安全**: 函数会被并行调用，避免使用全局变量
2. **异常处理**: 必须捕获所有异常，不能让异常传播
3. **返回值**: 必须返回 float 类型，通常在 [0, 1] 范围
4. **性能**: 这个函数会被调用数万次，注意优化性能

---

### 2.2 RewardManager 注册

**文件位置**: `verl/trainer/ppo/reward.py`

**作用**: 将你的 Reward 函数注册到 verl 系统

**修改内容**:

```python
"""
verl/trainer/ppo/reward.py
"""

# 在文件开头添加导入
from verl.utils.reward_score.your_task import compute_score as your_task_compute_score

def get_reward_fn(config):
    """
    根据配置加载 Reward 函数

    Args:
        config: Hydra 配置对象

    Returns:
        callable: compute_score 函数
    """
    # 从配置中获取 reward 类型
    reward_type = config.reward_manager.get('reward_type', 'default')

    # 路由到对应的 Reward 函数
    if reward_type == 'gsm8k':
        from verl.utils.reward_score.gsm8k import compute_score
        return compute_score

    elif reward_type == 'math':
        from verl.utils.reward_score.math import compute_score
        return compute_score

    # ===== 添加你的任务 =====
    elif reward_type == 'your_task':
        return your_task_compute_score

    # ========================

    else:
        raise ValueError(f"Unknown reward type: {reward_type}")
```

**配置对应**（在主配置文件中）:
```yaml
# config/your_task_grpo.yaml
reward_manager:
  reward_type: your_task  # 指定使用你的 Reward 函数

  # 其他 Reward 相关配置
  length_penalty: 0.0
  kl_penalty: 0.01
  num_examine: 5          # 打印前 5 个样本的详细信息
```

---

### 2.3 自定义 RewardManager【可选】

**文件位置**: `verl/workers/reward_manager/your_task_manager.py`

**作用**: 实现复杂的 Reward 计算逻辑（如需要模型推理、外部 API 调用等）

**何时需要**:
- ✅ Reward 计算需要调用其他模型（如 Reward Model）
- ✅ 需要批量处理以提高效率
- ✅ Reward 计算逻辑非常复杂，需要自定义流程

**参考文件**:
- `verl/workers/reward_manager/naive.py` (基础实现)
- `verl/workers/reward_manager/prime.py` (PRIME 实现)

**实现示例**:

```python
"""
verl/workers/reward_manager/your_task_manager.py
"""
from typing import List, Dict, Any
import torch
from verl.workers.reward_manager.base import BaseRewardManager
from verl.utils.reward_score.your_task import compute_score

class YourTaskRewardManager(BaseRewardManager):
    """
    自定义 Reward Manager

    适用于需要复杂 Reward 计算的场景
    """

    def __init__(
        self,
        tokenizer,
        num_examine: int = 0,
        length_penalty: float = 0.0,
        kl_penalty: float = 0.01,
        **kwargs
    ):
        """
        初始化 Reward Manager

        Args:
            tokenizer: Tokenizer 对象
            num_examine: 打印前 N 个样本的详细信息
            length_penalty: 长度惩罚系数
            kl_penalty: KL 散度惩罚系数
        """
        super().__init__()

        self.tokenizer = tokenizer
        self.num_examine = num_examine
        self.length_penalty = length_penalty
        self.kl_penalty = kl_penalty

        # 如果需要加载额外的模型（如 Reward Model）
        # self.reward_model = self._load_reward_model(kwargs)

    def compute_rewards(
        self,
        prompts: List[str],
        responses: List[str],
        reward_model_data: List[Dict],
        extra_info: List[Dict] = None,
    ) -> torch.Tensor:
        """
        批量计算 Rewards

        Args:
            prompts: Prompt 列表
            responses: 模型生成的 Response 列表
            reward_model_data: Reward 计算所需的数据（从 dataset 的 reward_model 字段）
            extra_info: 额外信息列表

        Returns:
            torch.Tensor: Reward 分数，shape [batch_size]
        """
        batch_size = len(responses)
        rewards = []

        for i in range(batch_size):
            # 获取数据源
            data_source = reward_model_data[i].get('data_source', 'unknown')

            # 获取 ground truth
            ground_truth = reward_model_data[i].get('ground_truth', '')

            # 获取额外信息
            extra = extra_info[i] if extra_info else {}

            # 计算 Reward
            try:
                reward = compute_score(
                    data_source=data_source,
                    solution_str=responses[i],
                    ground_truth=ground_truth,
                    extra_info=extra,
                    num_examine=self.num_examine if i < self.num_examine else 0,
                    tokenizer=self.tokenizer,
                )
            except Exception as e:
                print(f"Reward 计算失败: {e}")
                reward = 0.0

            rewards.append(reward)

        # 转换为 Tensor
        rewards_tensor = torch.tensor(rewards, dtype=torch.float32)

        # 应用后处理（长度惩罚、KL 惩罚等）
        if self.length_penalty != 0.0:
            response_lengths = torch.tensor([len(r.split()) for r in responses])
            rewards_tensor -= self.length_penalty * response_lengths

        return rewards_tensor

    def _load_reward_model(self, kwargs):
        """
        加载 Reward Model（如果需要）
        """
        # TODO: 实现 Reward Model 加载
        pass
```

**注册自定义 RewardManager**:

在 `verl/workers/reward_manager/registry.py` 中注册:

```python
# verl/workers/reward_manager/registry.py

from .your_task_manager import YourTaskRewardManager

REWARD_MANAGER_REGISTRY = {
    'naive': 'verl.workers.reward_manager.naive.NaiveRewardManager',
    'prime': 'verl.workers.reward_manager.prime.PrimeRewardManager',
    # 添加你的 RewardManager
    'your_task': 'verl.workers.reward_manager.your_task_manager.YourTaskRewardManager',
}
```

**配置使用**:
```yaml
# config/your_task_grpo.yaml
reward_manager:
  type: your_task  # 使用自定义 RewardManager

  # 自定义参数
  num_examine: 5
  length_penalty: 0.0
  kl_penalty: 0.01
```

---

## 第三部分：训练配置【必需】

### 3.1 主配置文件

**文件位置**: `config/your_task_grpo.yaml`

**作用**: 定义完整的训练配置（数据、模型、算法、Trainer）

**参考文件**:
- `examples/sglang_multiturn/config/search_multiturn_grpo.yaml`
- `examples/sglang_multiturn/config/gsm8k_multiturn_grpo.yaml`

**完整模板**:

```yaml
# config/your_task_grpo.yaml

# ==================== Hydra 配置 ====================
defaults:
  - _self_
  - override hydra/job_logging: stdout

hydra:
  run:
    dir: ${output_dir}/${exp_name}/hydra_outputs/${now:%Y-%m-%d}/${now:%H-%M-%S}

# ==================== 全局参数 ====================
project: your_project_name
exp_name: your_task_grpo
output_dir: ./outputs

# ==================== 数据配置 ====================
data:
  # 数据文件路径
  train_files:
    - data/your_task/train.parquet
  val_files:
    - data/your_task/valid.parquet

  # Batch size
  train_batch_size: 512
  val_batch_size: 1024

  # 长度限制
  max_prompt_length: 4096
  max_response_length: 2048

  # 可选：采样权重
  train_sample_weight: null

  # Tokenizer
  tokenizer_path: "path/to/tokenizer"  # 或模型路径
  tokenizer_type: "transformers"

# ==================== Reward Manager 配置 ====================
reward_manager:
  # Reward 类型
  reward_type: your_task  # 对应 2.2 中注册的类型

  # 或使用自定义 RewardManager
  # type: your_task

  # Reward 后处理
  length_penalty: 0.0      # 长度惩罚系数（负数鼓励长响应，正数鼓励短响应）
  kl_penalty: 0.01         # KL 散度惩罚系数

  # 调试
  num_examine: 5           # 打印前 5 个样本的详细信息

# ==================== Actor Rollout 配置 ====================
actor_rollout_ref:
  # 模型路径
  model:
    path: "path/to/your/model"  # 模型权重路径
    enable_gradient_checkpointing: false

  # Rollout 配置
  rollout:
    # 使用的推理引擎
    name: vllm  # 或 sglang, naive

    # GPU 分配
    tensor_model_parallel_size: 2  # 模型并行度
    gpu_memory_utilization: 0.4

    # 生成参数
    temperature: 1.0
    top_p: 1.0
    top_k: -1
    max_new_tokens: 2048

    # ===== Multi-turn 配置 =====
    multi_turn:
      enable: true                # 启用 multi-turn
      max_turns: 5                # 最大轮次

      # Tool 配置文件
      tool_config_path: ./config/tool_config/your_task_tools.yaml

      # Generation Manager（可选，默认使用标准实现）
      # generation_manager: "path.to.YourGenerationManager"

    # ===== 其他配置 =====
    # 是否使用 bf16
    dtype: bfloat16

# ==================== Critic 配置 ====================
critic:
  model:
    path: "path/to/your/model"  # 通常与 Actor 相同
    enable_gradient_checkpointing: true

  # Critic 训练参数
  optim:
    lr: 1e-6
    min_lr: 1e-7
    weight_decay: 0.01

# ==================== Reference Model 配置 ====================
ref:
  # 参考模型（用于 KL 散度计算）
  # 通常与初始 Actor 相同
  model:
    path: "path/to/your/model"

  rollout:
    name: vllm
    tensor_model_parallel_size: 2
    gpu_memory_utilization: 0.3

# ==================== 算法配置 (GRPO/PPO) ====================
algorithm:
  # 算法类型
  name: grpo  # 或 ppo

  # GRPO 特定参数
  kl_ctrl:
    type: fixed  # 或 adaptive
    kl_coef: 0.001

  # 优势函数估计
  gamma: 1.0
  lam: 0.95

  # PPO clip
  clip_ratio: 0.2

  # Entropy bonus
  entropy_coef: 0.0

# ==================== Trainer 配置 ====================
trainer:
  # 训练引擎
  backend: fsdp  # 或 megatron

  # 训练步数
  total_epochs: 10
  total_training_steps: 10000

  # Rollout 参数
  rollout_batch_size: 512      # 每次 rollout 的 batch size
  rollout_batch_size_per_device: 32

  # PPO 训练参数
  ppo_mini_batch_size: 128
  ppo_micro_batch_size: 16
  ppo_epochs: 2                # 每次 rollout 后的 PPO 更新轮次

  # 优化器
  optim:
    lr: 5e-7
    min_lr: 5e-8
    weight_decay: 0.01
    warmup_steps: 100

  # 梯度
  grad_clip: 1.0

  # 日志和保存
  log_interval: 1
  save_interval: 50
  eval_interval: 50

  # Ray 配置（如果使用分布式）
  ray:
    address: auto
    num_gpus: 8
    resources_per_trial:
      cpu: 16
      gpu: 2

# ==================== 实验追踪 ====================
logger:
  # Wandb
  use_wandb: true
  wandb:
    project: ${project}
    name: ${exp_name}
    entity: your_wandb_entity

  # Tensorboard
  use_tensorboard: false

# ==================== 其他 ====================
# 随机种子
seed: 42

# 是否使用混合精度
use_amp: true

# 检查点
checkpoint:
  save_dir: ${output_dir}/${exp_name}/checkpoints
  load_dir: null  # 如果需要从检查点恢复
```

**关键配置说明**:

1. **数据路径**: 指向第一部分生成的 Parquet 文件
2. **reward_type**: 对应第二部分注册的 Reward 函数
3. **multi_turn.enable**: 如果是 multi-turn 任务，设置为 true
4. **tool_config_path**: 指向 Tool 配置文件（见 3.2）

---

### 3.2 Tool 配置文件【multi-turn 必需】

**文件位置**: `config/tool_config/your_task_tools.yaml`

**作用**: 定义 multi-turn 任务中可用的工具

**参考文件**:
- `examples/sglang_multiturn/config/tool_config/gsm8k_tools.yaml`
- `examples/sglang_multiturn/config/tool_config/search_tools.yaml`

**格式**:

```yaml
# config/tool_config/your_task_tools.yaml

# 工具列表
tools:
  # ===== Tool 1: 搜索工具 =====
  - name: search
    description: "Search for relevant information from knowledge base"

    # 工具类型
    type: function

    # 参数 schema
    parameters:
      type: object
      properties:
        query:
          type: string
          description: "The search query"
        topk:
          type: integer
          description: "Number of results to return"
          default: 5
      required:
        - query

    # 工具实现类（Python 类路径）
    implementation: "verl.tools.search_tool.SearchTool"

    # 工具配置
    config:
      search_url: "http://localhost:8000/search"
      timeout: 30

  # ===== Tool 2: 代码执行工具 =====
  - name: execute_code
    description: "Execute Python code and return the output"

    type: function

    parameters:
      type: object
      properties:
        code:
          type: string
          description: "The Python code to execute"
        timeout:
          type: integer
          description: "Execution timeout in seconds"
          default: 10
      required:
        - code

    implementation: "verl.tools.code_executor.CodeExecutor"

    config:
      sandbox_url: "http://localhost:8001/execute"
      max_output_length: 10000

  # ===== Tool 3: 答案工具 =====
  - name: answer
    description: "Provide the final answer to the question"

    type: function

    parameters:
      type: object
      properties:
        answer:
          type: string
          description: "The final answer"
      required:
        - answer

    # 答案工具通常不需要实现，用于标记终止
    implementation: null

# ===== 工具使用配置 =====
tool_usage:
  # 每轮最多调用的工具数
  max_tools_per_turn: 3

  # 工具调用超时
  timeout: 60

  # 是否允许重复调用同一工具
  allow_repeated_tools: true

  # 终止条件
  termination:
    # 如果调用了这些工具，则终止
    terminal_tools:
      - answer

    # 或者达到最大轮次
    max_turns: 10

# ===== 工具格式 =====
tool_format:
  # 工具调用格式（用于 prompt）
  call_format: |
    <tool_call>
    {"name": "tool_name", "arguments": {"arg1": "value1"}}
    </tool_call>

  # 工具结果格式
  result_format: |
    <tool_result>
    {result}
    </tool_result>
```

**注意事项**:
1. `implementation` 字段指向 Python 类，需要在第四部分实现
2. `terminal_tools` 中的工具被调用后，该轮对话结束
3. 如果不需要复杂的工具实现，可以只定义 schema，在 Generation Manager 中处理

---

### 3.3 环境配置【可选】

**文件位置**: `config/runtime_env.yaml`

**作用**: 配置 Ray、GPU、分布式训练等环境参数

**何时需要**: 使用多机多卡训练时

**示例**:

```yaml
# config/runtime_env.yaml

# Ray 配置
ray:
  address: auto  # 或指定 Ray 集群地址

  # 资源配置
  resources:
    num_cpus: 64
    num_gpus: 8

  # Actor 配置
  actor_rollout:
    num_gpus: 2
    num_cpus: 8

  critic:
    num_gpus: 2
    num_cpus: 8

  ref:
    num_gpus: 2
    num_cpus: 8

# GPU 配置
gpu:
  # 可见的 GPU
  visible_devices: "0,1,2,3,4,5,6,7"

  # 内存分配策略
  memory_fraction: 0.9

# 分布式配置
distributed:
  # 是否使用 FSDP
  use_fsdp: true

  # FSDP 配置
  fsdp:
    sharding_strategy: "FULL_SHARD"  # 或 SHARD_GRAD_OP, NO_SHARD
    cpu_offload: false
    mixed_precision: true
```

---

## 第四部分：Tool 实现【multi-turn 可选】

### 4.1 Tool 类实现

**文件位置**: `verl/tools/your_task_tool.py`

**作用**: 实现工具的具体逻辑

**何时需要**:
- ✅ 实现 multi-turn 任务
- ✅ 需要调用外部 API、搜索引擎、数据库等
- ✅ 需要执行代码、验证答案等

**参考文件**:
- `verl/tools/search_tool.py`
- `verl/tools/gsm8k_tool.py`
- `verl/tools/sandbox_fusion_tools.py`

**实现示例**:

```python
"""
verl/tools/your_task_tool.py
"""
from typing import Dict, Any, List
import requests
import json
from verl.tools.base_tool import BaseTool

class YourTaskSearchTool(BaseTool):
    """
    搜索工具实现

    用于从知识库中检索相关信息
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化工具

        Args:
            config: 工具配置（从 tool_config.yaml 的 config 字段传入）
        """
        super().__init__(config)

        self.search_url = config.get('search_url', 'http://localhost:8000/search')
        self.timeout = config.get('timeout', 30)
        self.max_results = config.get('max_results', 10)

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具调用

        Args:
            arguments: 工具参数（从模型生成的 tool_call 中提取）

        Returns:
            dict: 工具执行结果
            {
                'success': bool,      # 是否执行成功
                'result': Any,        # 执行结果
                'error': str,         # 错误信息（如果失败）
                'metadata': dict,     # 元数据（如耗时、Token 数等）
            }
        """
        # 1. 提取参数
        query = arguments.get('query', '')
        topk = arguments.get('topk', 5)

        if not query:
            return {
                'success': False,
                'result': None,
                'error': 'Query is empty',
                'metadata': {}
            }

        # 2. 调用搜索 API
        try:
            response = requests.post(
                self.search_url,
                json={
                    'query': query,
                    'topk': min(topk, self.max_results)
                },
                timeout=self.timeout
            )

            response.raise_for_status()
            search_results = response.json()

        except requests.RequestException as e:
            return {
                'success': False,
                'result': None,
                'error': f'Search API error: {str(e)}',
                'metadata': {}
            }

        # 3. 处理搜索结果
        documents = search_results.get('documents', [])

        # 格式化结果
        formatted_results = []
        for i, doc in enumerate(documents[:topk]):
            formatted_results.append({
                'rank': i + 1,
                'title': doc.get('title', ''),
                'content': doc.get('content', '')[:500],  # 截断到 500 字符
                'score': doc.get('score', 0.0)
            })

        # 4. 返回结果
        return {
            'success': True,
            'result': formatted_results,
            'error': None,
            'metadata': {
                'num_results': len(formatted_results),
                'query': query,
            }
        }

    def format_result(self, result: Dict[str, Any]) -> str:
        """
        格式化结果为字符串（用于拼接到 prompt）

        Args:
            result: execute 方法的返回值

        Returns:
            str: 格式化后的结果字符串
        """
        if not result['success']:
            return f"Error: {result['error']}"

        documents = result['result']

        if not documents:
            return "No relevant documents found."

        # 格式化为 prompt 友好的格式
        formatted = []
        for doc in documents:
            formatted.append(
                f"Doc {doc['rank']}: {doc['title']}\n"
                f"{doc['content']}\n"
                f"(Score: {doc['score']:.3f})\n"
            )

        return "\n".join(formatted)


class YourTaskCodeExecutor(BaseTool):
    """
    代码执行工具

    在沙箱中安全执行 Python 代码
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.sandbox_url = config.get('sandbox_url', 'http://localhost:8001/execute')
        self.timeout = config.get('timeout', 30)
        self.max_output_length = config.get('max_output_length', 10000)

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行代码"""
        code = arguments.get('code', '')
        timeout = arguments.get('timeout', 10)

        if not code:
            return {
                'success': False,
                'result': None,
                'error': 'Code is empty',
                'metadata': {}
            }

        try:
            # 调用沙箱 API
            response = requests.post(
                self.sandbox_url,
                json={
                    'code': code,
                    'timeout': min(timeout, self.timeout)
                },
                timeout=self.timeout + 5
            )

            response.raise_for_status()
            exec_result = response.json()

            # 检查执行状态
            if exec_result.get('status') == 'success':
                output = exec_result.get('output', '')

                # 截断过长的输出
                if len(output) > self.max_output_length:
                    output = output[:self.max_output_length] + "\n... (output truncated)"

                return {
                    'success': True,
                    'result': {
                        'stdout': output,
                        'stderr': exec_result.get('stderr', ''),
                        'return_code': 0
                    },
                    'error': None,
                    'metadata': {
                        'execution_time': exec_result.get('execution_time', 0)
                    }
                }
            else:
                # 执行失败
                return {
                    'success': False,
                    'result': None,
                    'error': exec_result.get('error', 'Unknown execution error'),
                    'metadata': {}
                }

        except requests.RequestException as e:
            return {
                'success': False,
                'result': None,
                'error': f'Sandbox API error: {str(e)}',
                'metadata': {}
            }

    def format_result(self, result: Dict[str, Any]) -> str:
        """格式化执行结果"""
        if not result['success']:
            return f"Execution Error:\n{result['error']}"

        exec_info = result['result']

        formatted = []

        # 标准输出
        if exec_info['stdout']:
            formatted.append(f"Output:\n{exec_info['stdout']}")

        # 标准错误
        if exec_info['stderr']:
            formatted.append(f"Errors:\n{exec_info['stderr']}")

        # 元数据
        if result['metadata'].get('execution_time'):
            formatted.append(f"Execution time: {result['metadata']['execution_time']:.3f}s")

        return "\n\n".join(formatted)
```

**BaseTool 基类**（已在 verl 中实现）:

```python
# verl/tools/base_tool.py (reference)
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """工具基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用"""
        pass

    @abstractmethod
    def format_result(self, result: Dict[str, Any]) -> str:
        """格式化结果"""
        pass
```

---

### 4.2 Tool 注册

**文件位置**: `verl/tools/__init__.py`

**作用**: 注册工具，使其可被 verl 发现

**修改内容**:

```python
# verl/tools/__init__.py

from .base_tool import BaseTool
from .search_tool import SearchTool
from .gsm8k_tool import GSM8KTool

# 添加你的工具
from .your_task_tool import YourTaskSearchTool, YourTaskCodeExecutor

# 工具注册表
TOOL_REGISTRY = {
    'search': SearchTool,
    'gsm8k': GSM8KTool,

    # 注册你的工具
    'your_task_search': YourTaskSearchTool,
    'your_task_code': YourTaskCodeExecutor,
}

def get_tool(tool_name: str, config: dict):
    """
    获取工具实例

    Args:
        tool_name: 工具名称
        config: 工具配置

    Returns:
        BaseTool: 工具实例
    """
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {tool_name}")

    tool_class = TOOL_REGISTRY[tool_name]
    return tool_class(config)
```

**在配置中引用**:

```yaml
# config/tool_config/your_task_tools.yaml
tools:
  - name: search
    # 指向注册表中的 key
    implementation: your_task_search
    config:
      search_url: "http://localhost:8000/search"
```

---

### 4.3 Tool Schema 定义【可选】

**文件位置**: `verl/tools/schemas.py`

**作用**: 定义工具的 JSON Schema，用于模型理解工具功能

**何时需要**: 当你需要更复杂的 Schema 定义时

**示例**:

```python
# verl/tools/schemas.py

# 添加你的 Schema
YOUR_TASK_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search for relevant information from the knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant documents."
                    },
                    "topk": {
                        "type": "integer",
                        "description": "Number of top results to return (1-10).",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": "Execute Python code in a secure sandbox and return the output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to execute. Must be self-contained."
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maximum execution time in seconds (1-30).",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 30
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "answer",
            "description": "Provide the final answer to the user's question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The final answer to the question."
                    }
                },
                "required": ["answer"]
            }
        }
    }
]
```

**在配置中使用**:

```yaml
# config/tool_config/your_task_tools.yaml
# 引用预定义的 Schema
schema: "verl.tools.schemas.YOUR_TASK_TOOLS_SCHEMA"
```

---

### 4.4 Tool 配置 JSON【可选】

**文件位置**: `tools.json` 或 `config/tool_config/tools.json`

**作用**: 集中管理所有工具的配置（如 API endpoint、credentials 等）

**格式**:

```json
{
  "your_task_search": {
    "search_url": "http://search-api.example.com/search",
    "api_key": "${SEARCH_API_KEY}",
    "timeout": 30,
    "max_results": 10
  },
  "your_task_code_executor": {
    "sandbox_url": "http://sandbox.example.com/execute",
    "timeout": 30,
    "max_output_length": 10000,
    "allowed_imports": ["math", "numpy", "sympy"]
  }
}
```

**加载配置**:

```python
# 在 Tool 初始化时加载
import json
from pathlib import Path

def load_tool_config(tool_name: str, config_path: str = "tools.json"):
    """加载工具配置"""
    with open(config_path) as f:
        all_configs = json.load(f)

    if tool_name not in all_configs:
        raise ValueError(f"Tool {tool_name} not found in {config_path}")

    return all_configs[tool_name]
```

---

## 第五部分：Generation Manager【可选】

### 5.1 自定义 Generation Manager

**文件位置**: `verl/workers/rollout/your_task_generation_manager.py`

**作用**: 实现复杂的 multi-turn 生成逻辑（如上下文管理、终止判定等）

**何时需要**:
- ✅ 需要自定义 multi-turn 流程
- ✅ 需要特殊的上下文管理策略
- ✅ 需要自定义终止条件
- ✅ 需要在生成过程中注入额外逻辑

**参考文件**:
- `.reference_projects/ToolOrchestra/training/lead_agent/llm_agent/generation_quick3.py` (完整实现)
- `docs/verl_api/toolorchestra_multiturn_implementation.md` (详细文档)

**实现示例**:

```python
"""
verl/workers/rollout/your_task_generation_manager.py
"""
from typing import List, Dict, Any
import torch
from verl import DataProto
from verl.utils.model import compute_position_id_with_mask
import verl.utils.torch_functional as verl_F

class YourTaskGenerationManager:
    """
    自定义 Generation Manager

    负责管理 multi-turn 生成流程
    """

    def __init__(
        self,
        tokenizer,
        actor_rollout_wg,
        config,
    ):
        """
        初始化 Generation Manager

        Args:
            tokenizer: Tokenizer 对象
            actor_rollout_wg: Actor Rollout Worker Group
            config: 配置对象
        """
        self.tokenizer = tokenizer
        self.actor_rollout_wg = actor_rollout_wg
        self.config = config

        # Multi-turn 配置
        self.max_turns = config.get('max_turns', 10)
        self.max_prompt_length = config.get('max_prompt_length', 4096)
        self.max_response_length = config.get('max_response_length', 2048)

        # 加载工具
        self.tools = self._load_tools(config.get('tool_config_path'))

    def run_multi_turn_generation(
        self,
        batch: DataProto,
        **kwargs
    ) -> DataProto:
        """
        运行 multi-turn 生成循环

        Args:
            batch: 输入 batch
                - non_tensor_batch:
                    - 'prompt': List[List[dict]]  # 初始对话
                    - 'reward_model': List[dict]   # Reward 信息
                    - 'data_source': List[str]     # 任务标识

        Returns:
            DataProto: 生成结果
                - batch:
                    - 'input_ids': torch.Tensor
                    - 'responses': torch.Tensor
                    - 'rewards': torch.Tensor
                - non_tensor_batch:
                    - ... (保留原始信息)
        """
        batch_size = len(batch.non_tensor_batch['prompt'])

        # ========== 初始化状态 ==========
        # 活跃样本掩码（标记哪些样本还在继续）
        active_mask = torch.ones(batch_size, dtype=torch.bool)

        # 累积的上下文信息
        contexts = [self._init_context(batch, i) for i in range(batch_size)]

        # 记录所有轮次的数据
        all_turn_data = {
            'input_ids': [],
            'responses': [],
            'tools_used': [],
            'rewards': [],
        }

        # ========== Multi-turn 循环 ==========
        for turn in range(self.max_turns):
            # 检查是否所有样本都完成
            if not active_mask.sum():
                break

            # --- Step 1: 构建当前轮的 Prompt ---
            prompts = [
                self._build_prompt(contexts[i])
                for i in range(batch_size)
            ]

            # --- Step 2: Tokenize ---
            input_ids, attention_mask = self._tokenize_prompts(prompts)

            # --- Step 3: 模型生成 ---
            # 只对活跃样本生成
            active_indices = torch.where(active_mask)[0]
            active_input_ids = input_ids[active_indices]
            active_attention_mask = attention_mask[active_indices]

            active_batch = DataProto.from_dict({
                'input_ids': active_input_ids,
                'attention_mask': active_attention_mask,
                'position_ids': compute_position_id_with_mask(active_attention_mask),
            })

            # 调用 Actor 生成
            gen_output = self.actor_rollout_wg.generate_sequences(active_batch)

            # --- Step 4: 解析生成结果 ---
            responses = self.tokenizer.batch_decode(
                gen_output.batch['responses'],
                skip_special_tokens=True
            )

            # --- Step 5: 提取工具调用 ---
            tool_calls = [
                self._extract_tool_calls(resp)
                for resp in responses
            ]

            # --- Step 6: 执行工具 ---
            tool_results = self._execute_tools(tool_calls, contexts, active_indices)

            # --- Step 7: 更新上下文 ---
            for i, active_idx in enumerate(active_indices.tolist()):
                # 将模型响应添加到上下文
                contexts[active_idx]['history'].append({
                    'role': 'assistant',
                    'content': responses[i]
                })

                # 将工具结果添加到上下文
                if tool_results[i]:
                    contexts[active_idx]['history'].append({
                        'role': 'tool',
                        'content': self._format_tool_results(tool_results[i])
                    })

                    # 更新累积信息
                    self._update_context_info(contexts[active_idx], tool_results[i])

            # --- Step 8: 判断终止 ---
            dones = self._check_termination(tool_calls, contexts, active_indices)

            # 更新 active_mask
            for i, active_idx in enumerate(active_indices.tolist()):
                if dones[i]:
                    active_mask[active_idx] = False

            # --- Step 9: 记录本轮数据 ---
            all_turn_data['input_ids'].append(input_ids)
            all_turn_data['responses'].append(self._pad_responses(gen_output.batch['responses'], batch_size, active_indices))
            all_turn_data['tools_used'].append(tool_calls)

        # ========== 计算 Rewards ==========
        rewards = self._compute_final_rewards(contexts, batch)

        # ========== 组装输出 ==========
        return self._assemble_output(all_turn_data, rewards, batch)

    def _init_context(self, batch: DataProto, idx: int) -> Dict:
        """初始化上下文"""
        return {
            'history': batch.non_tensor_batch['prompt'][idx].copy(),
            'documents': [],
            'code_snippets': [],
            'attempts': [],
            'tools_used': [],
        }

    def _build_prompt(self, context: Dict) -> str:
        """
        构建当前轮的 Prompt

        根据累积的上下文信息构建 prompt
        """
        # 1. 格式化历史对话
        messages = context['history'].copy()

        # 2. 添加累积的文档信息
        if context['documents']:
            doc_str = self._format_documents(context['documents'])
            messages.insert(1, {
                'role': 'system',
                'content': f"Relevant documents:\n{doc_str}"
            })

        # 3. 添加代码执行结果
        if context['code_snippets']:
            code_str = self._format_code_snippets(context['code_snippets'])
            messages.append({
                'role': 'system',
                'content': f"Code execution results:\n{code_str}"
            })

        # 4. 应用 chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tools=self.tools,
            tokenize=False
        )

        return prompt

    def _tokenize_prompts(self, prompts: List[str]):
        """Tokenize prompts"""
        input_ids_list = []
        attention_mask_list = []

        for prompt in prompts:
            ids, mask = verl_F.tokenize_and_postprocess_data(
                prompt=prompt,
                tokenizer=self.tokenizer,
                max_length=self.max_prompt_length,
                pad_token_id=self.tokenizer.pad_token_id,
                left_pad=True,
                truncation='middle'
            )
            input_ids_list.append(ids)
            attention_mask_list.append(mask)

        input_ids = torch.stack(input_ids_list)
        attention_mask = torch.stack(attention_mask_list)

        return input_ids, attention_mask

    def _extract_tool_calls(self, response: str) -> List[Dict]:
        """
        从模型响应中提取工具调用

        假设格式: <tool_call>{"name": "search", "arguments": {...}}</tool_call>
        """
        import re
        import json

        tool_calls = []

        # 提取所有 <tool_call>...</tool_call>
        matches = re.findall(r'<tool_call>(.*?)</tool_call>', response, re.DOTALL)

        for match in matches:
            try:
                tool_call = json.loads(match.strip())

                # 验证格式
                if 'name' in tool_call and 'arguments' in tool_call:
                    tool_calls.append(tool_call)
            except json.JSONDecodeError:
                # 解析失败，跳过
                pass

        return tool_calls

    def _execute_tools(
        self,
        tool_calls_batch: List[List[Dict]],
        contexts: List[Dict],
        active_indices: torch.Tensor
    ) -> List[List[Dict]]:
        """
        执行工具调用

        Returns:
            List[List[Dict]]: 每个样本的工具执行结果
        """
        results_batch = []

        for i, active_idx in enumerate(active_indices.tolist()):
            tool_calls = tool_calls_batch[i] if i < len(tool_calls_batch) else []
            results = []

            for tool_call in tool_calls:
                tool_name = tool_call['name']
                arguments = tool_call['arguments']

                # 获取工具实例
                tool = self.tools.get(tool_name)

                if tool:
                    # 执行工具
                    result = tool.execute(arguments)
                    results.append({
                        'tool': tool_name,
                        'arguments': arguments,
                        'result': result
                    })
                else:
                    # 工具不存在
                    results.append({
                        'tool': tool_name,
                        'arguments': arguments,
                        'result': {
                            'success': False,
                            'error': f'Unknown tool: {tool_name}'
                        }
                    })

            results_batch.append(results)

        return results_batch

    def _check_termination(
        self,
        tool_calls_batch: List[List[Dict]],
        contexts: List[Dict],
        active_indices: torch.Tensor
    ) -> List[bool]:
        """
        检查终止条件

        Returns:
            List[bool]: 每个样本是否应该终止
        """
        dones = []

        for i, active_idx in enumerate(active_indices.tolist()):
            tool_calls = tool_calls_batch[i] if i < len(tool_calls_batch) else []

            # 终止条件1: 调用了 answer 工具
            has_answer = any(tc['name'] == 'answer' for tc in tool_calls)

            # 终止条件2: 没有有效的工具调用（可能是格式错误）
            no_valid_tools = len(tool_calls) == 0

            # 终止条件3: 达到最大轮次（在外层循环判断）

            dones.append(has_answer or no_valid_tools)

        return dones

    def _update_context_info(self, context: Dict, tool_results: List[Dict]):
        """更新上下文的累积信息"""
        for result in tool_results:
            tool_name = result['tool']

            if tool_name == 'search' and result['result']['success']:
                # 累积搜索结果
                context['documents'].extend(result['result']['result'])

            elif tool_name == 'execute_code' and result['result']['success']:
                # 累积代码执行结果
                context['code_snippets'].append({
                    'code': result['arguments']['code'],
                    'output': result['result']['result']['stdout']
                })

            elif tool_name == 'answer':
                # 记录答案尝试
                context['attempts'].append(result['arguments'].get('answer', ''))

            # 记录工具使用
            context['tools_used'].append(tool_name)

    def _format_tool_results(self, tool_results: List[Dict]) -> str:
        """格式化工具结果为字符串"""
        formatted = []

        for result in tool_results:
            tool_name = result['tool']
            tool_obj = self.tools.get(tool_name)

            if tool_obj:
                formatted.append(tool_obj.format_result(result['result']))
            else:
                formatted.append(f"{tool_name}: {result['result']}")

        return "\n\n".join(formatted)

    def _compute_final_rewards(
        self,
        contexts: List[Dict],
        batch: DataProto
    ) -> torch.Tensor:
        """
        计算最终 Rewards

        这里可以调用 Reward 函数，或者在 Trainer 中统一计算
        """
        # 通常在这里只是占位，真正的 Reward 计算在 RewardManager 中
        rewards = torch.zeros(len(contexts))
        return rewards

    def _assemble_output(
        self,
        all_turn_data: Dict,
        rewards: torch.Tensor,
        batch: DataProto
    ) -> DataProto:
        """组装最终输出"""
        # 简化实现：只返回最后一轮的数据
        # 完整实现需要拼接所有轮次

        return DataProto.from_dict({
            # Tensor 数据
            'input_ids': all_turn_data['input_ids'][-1],
            'responses': all_turn_data['responses'][-1],
            'rewards': rewards,

            # Non-tensor 数据
            'data_source': batch.non_tensor_batch['data_source'],
            'reward_model': batch.non_tensor_batch['reward_model'],
            'tools_used': all_turn_data['tools_used'],
        })

    def _load_tools(self, tool_config_path: str) -> Dict:
        """加载工具"""
        # TODO: 从配置文件加载工具
        pass

    def _format_documents(self, documents: List[Dict]) -> str:
        """格式化文档"""
        # TODO: 实现文档格式化
        pass

    def _format_code_snippets(self, snippets: List[Dict]) -> str:
        """格式化代码片段"""
        # TODO: 实现代码格式化
        pass

    def _pad_responses(
        self,
        responses: torch.Tensor,
        batch_size: int,
        active_indices: torch.Tensor
    ) -> torch.Tensor:
        """将 responses 填充到完整 batch size"""
        full_responses = torch.zeros(
            batch_size,
            responses.shape[1],
            dtype=responses.dtype
        )
        full_responses[active_indices] = responses
        return full_responses
```

**关键实现要点**:

1. **上下文管理**: 维护累积的文档、代码、答案等信息
2. **工具执行**: 解析工具调用、执行工具、格式化结果
3. **终止判定**: 判断何时结束 multi-turn 循环
4. **Tensor 处理**: 处理 padding、拼接、position_ids 等
5. **活跃样本管理**: 使用 active_mask 跟踪哪些样本还在继续

**注册 Generation Manager**:

```yaml
# config/your_task_grpo.yaml
actor_rollout_ref:
  rollout:
    multi_turn:
      enable: true
      # 指定自定义 Generation Manager
      generation_manager: "verl.workers.rollout.your_task_generation_manager.YourTaskGenerationManager"
```

---

### 5.2 上下文管理逻辑【重点】

**相关文档**: [上下文维护机制](context_maintenance_mechanism.md)

**关键机制**:

1. **三层上下文架构**:
   - **应用层**: 人类可读的数据结构（`contexts[i]['documents']`, `contexts[i]['code_snippets']`）
   - **提示层**: 格式化为 prompt 的字符串
   - **张量层**: PyTorch Tensor（`input_ids`, `attention_mask`）

2. **累积策略**:
   - 只增不减：每轮添加新信息，不删除旧信息
   - 分类存储：文档、代码、答案分别存储
   - 智能合并：新旧文档使用 `merge_documents()` 函数合并

3. **长度控制**:
   - **优先级金字塔**: Problem > Code > Attempts > Documents
   - **分级截断**: 从低优先级开始截断
   - **Token 级控制**: 使用 `cut_seq()` 精确控制长度

4. **实现技巧**:
   - 使用 `cut_middle_turns()` 裁剪对话历史（保留开头和结尾）
   - 使用 `merge_documents()` 智能合并文档
   - 使用 `TensorHelper` 处理 tensor 拼接和 padding

**示例代码**（在 Generation Manager 中）:

```python
def _build_prompt_with_context_control(self, context: Dict) -> str:
    """
    构建 Prompt 并控制长度

    实现优先级截断策略
    """
    # 1. 格式化各部分
    problem = context['history'][0]['content']  # 原始问题
    doc_str = self._format_documents(context['documents'])
    code_str = self._format_code_snippets(context['code_snippets'])
    attempt_str = self._format_attempts(context['attempts'])

    # 2. 分级截断
    # 2.1 先截断 attempts
    attempt_str_cut = self._cut_seq(attempt_str, max_tokens=8000)

    # 2.2 再截断 code + attempts
    code_attempt_str = code_str + attempt_str_cut
    code_attempt_cut = self._cut_seq(code_attempt_str, max_tokens=16000)

    # 2.3 最后截断 documents + code + attempts
    remaining_budget = self.max_prompt_length - len(self.tokenizer.encode(problem)) - 1000

    if remaining_budget > len(self.tokenizer.encode(code_attempt_cut)):
        # 有空间，加入文档
        doc_budget = remaining_budget - len(self.tokenizer.encode(code_attempt_cut))
        doc_str_cut = self._cut_seq(doc_str, max_tokens=doc_budget)
        context_str = doc_str_cut + code_attempt_cut
    else:
        # 没空间，放弃文档
        context_str = code_attempt_cut

    # 3. 构建最终 prompt
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Problem: {problem}\n\n{context_str}\n\nChoose an appropriate tool."}
    ]

    prompt = self.tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tools=self.tools,
        tokenize=False
    )

    return prompt

def _cut_seq(self, text: str, max_tokens: int) -> str:
    """截断文本到指定 token 数"""
    tokens = self.tokenizer.encode(text)

    if len(tokens) <= max_tokens:
        return text

    # 保留最后 max_tokens 个 token
    truncated_tokens = tokens[-max_tokens:]
    return self.tokenizer.decode(truncated_tokens, skip_special_tokens=True)
```

---

## 第六部分：Trainer 定制【高级可选】

### 6.1 自定义 Trainer

**文件位置**: `verl/trainer/ppo/your_task_trainer.py`

**作用**: 实现自定义的训练流程（如 GRPO、DAPO 等变体）

**何时需要**:
- ✅ 需要修改 PPO 算法（如 GRPO、DAPO）
- ✅ 需要自定义数据筛选逻辑
- ✅ 需要特殊的 Reward 归一化策略

**参考文件**:
- `.reference_projects/ToolOrchestra/training/recipe/algo/grpo_ray_trainer_quick3.py`
- `verl/trainer/ppo/ray_trainer.py`

**核心修改点**:

```python
"""
verl/trainer/ppo/your_task_trainer.py
"""
from verl.trainer.ppo.ray_trainer import RayPPOTrainer

class YourTaskTrainer(RayPPOTrainer):
    """
    自定义 Trainer

    基于 RayPPOTrainer 进行扩展
    """

    def __init__(self, config):
        super().__init__(config)

        # 自定义初始化
        self.custom_param = config.get('custom_param', 0.5)

    def _normalize_rewards(self, rollout_batch):
        """
        自定义 Reward 归一化策略

        例如：GRPO 使用组内标准化
        """
        # 提取 Rewards
        rewards = rollout_batch.batch['rewards']

        # 提取分组信息（如果有）
        group_ids = rollout_batch.non_tensor_batch.get('group_id', None)

        if group_ids:
            # 组内标准化（GRPO）
            normalized_rewards = self._group_normalize(rewards, group_ids)
        else:
            # 全局标准化（PPO）
            normalized_rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-8)

        # 更新 batch
        rollout_batch.batch['rewards'] = normalized_rewards

        return rollout_batch

    def _group_normalize(self, rewards, group_ids):
        """组内标准化（GRPO）"""
        import torch
        from collections import defaultdict

        # 按组收集 rewards
        group_rewards = defaultdict(list)
        for i, gid in enumerate(group_ids):
            group_rewards[gid].append(i)

        # 组内标准化
        normalized = rewards.clone()

        for gid, indices in group_rewards.items():
            group_r = rewards[indices]

            if len(group_r) > 1:
                mean = group_r.mean()
                std = group_r.std()

                normalized[indices] = (group_r - mean) / (std + 1e-8)
            else:
                # 单样本组，标准化为 0
                normalized[indices] = 0.0

        # Clip 到 [-3, 3]
        normalized = torch.clamp(normalized, -3.0, 3.0)

        return normalized

    def _filter_training_samples(self, rollout_batch):
        """
        自定义样本筛选逻辑

        例如：只选择 Reward 标准差 > 阈值的组
        """
        # 提取信息
        rewards = rollout_batch.batch['rewards']
        group_ids = rollout_batch.non_tensor_batch.get('group_id', None)

        if group_ids is None:
            # 没有分组，不筛选
            return rollout_batch

        # 计算每组的标准差
        from collections import defaultdict
        import torch

        group_rewards = defaultdict(list)
        for i, gid in enumerate(group_ids):
            group_rewards[gid].append(rewards[i].item())

        # 筛选标准差 > 阈值的组
        threshold = 0.1
        selected_indices = []

        for i, gid in enumerate(group_ids):
            group_r = torch.tensor(group_rewards[gid])

            if len(group_r) > 1 and group_r.std() > threshold:
                selected_indices.append(i)

        if len(selected_indices) == 0:
            # 没有符合条件的样本
            return None

        # 筛选样本
        indices = torch.tensor(selected_indices)

        filtered_batch = {}
        for k, v in rollout_batch.batch.items():
            if isinstance(v, torch.Tensor):
                filtered_batch[k] = v[indices]

        filtered_non_tensor = {}
        for k, v in rollout_batch.non_tensor_batch.items():
            if isinstance(v, list):
                filtered_non_tensor[k] = [v[i] for i in selected_indices]
            else:
                filtered_non_tensor[k] = v

        from verl import DataProto
        return DataProto.from_dict(filtered_batch, non_tensor_batch=filtered_non_tensor)
```

**注册自定义 Trainer**:

```yaml
# config/your_task_grpo.yaml
trainer:
  # 指定自定义 Trainer
  type: "verl.trainer.ppo.your_task_trainer.YourTaskTrainer"

  # 自定义参数
  custom_param: 0.5
```

---

## 第七部分：启动脚本【必需】

### 7.1 训练启动脚本

**文件位置**: `scripts/train_your_task.sh`

**作用**: 启动训练

**示例**:

```bash
#!/bin/bash
# scripts/train_your_task.sh

# ==================== 环境配置 ====================
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export OMP_NUM_THREADS=8

# ==================== 路径配置 ====================
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# ==================== 训练参数 ====================
CONFIG_NAME="your_task_grpo"
EXP_NAME="your_task_$(date +%Y%m%d_%H%M%S)"

# ==================== 启动训练 ====================
python -m verl.trainer.main_ppo \
    --config-name "$CONFIG_NAME" \
    exp_name="$EXP_NAME" \
    trainer.total_epochs=10 \
    data.train_batch_size=512 \
    logger.use_wandb=true \
    logger.wandb.project="your_project" \
    logger.wandb.name="$EXP_NAME"

# ==================== 或使用 Hydra 多重覆盖 ====================
# python -m verl.trainer.main_ppo \
#     --config-name "$CONFIG_NAME" \
#     --multirun \
#     algorithm.kl_ctrl.kl_coef=0.001,0.01,0.1 \
#     trainer.optim.lr=1e-7,5e-7,1e-6
```

**使用方式**:
```bash
# 赋予执行权限
chmod +x scripts/train_your_task.sh

# 启动训练
./scripts/train_your_task.sh
```

---

### 7.2 评估脚本【可选】

**文件位置**: `scripts/eval_your_task.sh`

**作用**: 评估训练好的模型

**示例**:

```bash
#!/bin/bash
# scripts/eval_your_task.sh

# ==================== 环境配置 ====================
export CUDA_VISIBLE_DEVICES=0,1

# ==================== 路径配置 ====================
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# ==================== 评估参数 ====================
CHECKPOINT_PATH="$1"
EVAL_DATA="data/your_task/test.parquet"

if [ -z "$CHECKPOINT_PATH" ]; then
    echo "Usage: $0 <checkpoint_path>"
    exit 1
fi

# ==================== 启动评估 ====================
python -m verl.trainer.main_eval \
    --config-name "your_task_grpo" \
    model.path="$CHECKPOINT_PATH" \
    data.val_files=["$EVAL_DATA"] \
    eval.num_samples=1000 \
    eval.batch_size=32 \
    eval.output_dir="./eval_results"
```

---

## 第八部分：完整 Checklist

### 最小可用版本 (7个文件)

适用于**简单任务**（如单轮问答、不需要复杂工具）

- [ ] **1. 数据预处理脚本** (`examples/data_preprocess/your_task.py`)
- [ ] **2. Parquet 数据文件** (`data/your_task/train.parquet`)
- [ ] **3. Reward 计分函数** (`verl/utils/reward_score/your_task.py`)
- [ ] **4. Reward 注册** (修改 `verl/trainer/ppo/reward.py`)
- [ ] **5. 主配置文件** (`config/your_task_grpo.yaml`)
- [ ] **6. 启动脚本** (`scripts/train_your_task.sh`)
- [ ] **7. 数据验证** (运行验证脚本确保数据格式正确)

### 完整版本 (15-20个文件)

适用于**复杂 multi-turn 任务**（如需要工具调用、代码执行等）

**数据 (3个文件)**:
- [ ] 1. 数据预处理脚本
- [ ] 2. Parquet 数据文件 (train/valid/test)
- [ ] 3. Dataset 配置（在主配置中）

**Reward (2-3个文件)**:
- [ ] 4. Reward 计分函数
- [ ] 5. Reward 注册
- [ ] 6. (可选) 自定义 RewardManager

**配置 (2-3个文件)**:
- [ ] 7. 主配置文件
- [ ] 8. Tool 配置文件
- [ ] 9. (可选) 环境配置

**Tool (2-4个文件)**:
- [ ] 10. Tool 类实现
- [ ] 11. Tool 注册
- [ ] 12. (可选) Tool Schema 定义
- [ ] 13. (可选) Tool 配置 JSON

**Generation Manager (1-2个文件)**:
- [ ] 14. 自定义 Generation Manager
- [ ] 15. (可选) 上下文管理辅助函数

**Trainer (1个文件)**:
- [ ] 16. (可选) 自定义 Trainer

**启动 (1-2个文件)**:
- [ ] 17. 训练启动脚本
- [ ] 18. (可选) 评估脚本

**验证 (测试)**:
- [ ] 19. 数据加载测试
- [ ] 20. Reward 计算测试
- [ ] 21. 端到端训练测试（小 batch）

---

## 第九部分：开发和调试建议

### 9.1 开发顺序

**推荐按以下顺序进行**:

1. **数据准备** (第一部分)
   - 先准备一小批数据（如 10 个样本）
   - 验证数据格式
   - 确保可以加载

2. **Reward 实现** (第二部分)
   - 实现 `compute_score` 函数
   - 使用 `num_examine` 打印详细信息
   - 手动测试几个样本

3. **基础配置** (第三部分 3.1)
   - 创建最简配置文件
   - 先不启用 multi-turn
   - 测试单轮生成

4. **启动脚本** (第七部分)
   - 创建启动脚本
   - 尝试运行训练（即使报错也没关系）
   - 根据报错逐步修复

5. **Tool 实现** (第四部分) - 如果需要 multi-turn
   - 先实现最简单的工具
   - 逐步添加复杂工具
   - 测试工具调用

6. **Generation Manager** (第五部分) - 如果需要自定义
   - 先使用默认实现
   - 确定需要自定义后再实现
   - 逐步添加复杂逻辑

7. **Trainer 定制** (第六部分) - 高级功能
   - 最后考虑
   - 先使用标准 Trainer

### 9.2 调试技巧

#### 数据调试

```python
# 验证数据格式
import pandas as pd

df = pd.read_parquet("data/your_task/train.parquet")

print("字段:", df.columns.tolist())
print("样本数:", len(df))
print("\n第一个样本:")
for k, v in df.iloc[0].items():
    print(f"{k}: {v}")

# 检查必需字段
assert 'prompt' in df.columns
assert 'reward_model' in df.columns
assert 'data_source' in df.columns

# 检查数据类型
assert isinstance(df.iloc[0]['prompt'], list)
assert isinstance(df.iloc[0]['reward_model'], dict)
```

#### Reward 调试

```python
# 测试 Reward 函数
from verl.utils.reward_score.your_task import compute_score

# 测试样本
test_cases = [
    {
        'data_source': 'your_task',
        'solution': '<answer>42</answer>',
        'ground_truth': '42',
        'expected_reward': 1.0
    },
    {
        'data_source': 'your_task',
        'solution': '<answer>41</answer>',
        'ground_truth': '42',
        'expected_reward': 0.0
    },
]

for i, test in enumerate(test_cases):
    reward = compute_score(
        data_source=test['data_source'],
        solution_str=test['solution'],
        ground_truth=test['ground_truth'],
        num_examine=1
    )

    print(f"Test {i+1}: {reward} (expected: {test['expected_reward']})")
    assert abs(reward - test['expected_reward']) < 1e-5
```

#### 配置调试

```bash
# 打印完整配置
python -m verl.trainer.main_ppo \
    --config-name your_task_grpo \
    --cfg job

# 验证配置覆盖
python -m verl.trainer.main_ppo \
    --config-name your_task_grpo \
    trainer.total_epochs=1 \
    --cfg job \
    | grep "total_epochs"
```

#### 端到端调试

```bash
# 使用小数据集和少量步数测试
python -m verl.trainer.main_ppo \
    --config-name your_task_grpo \
    data.train_batch_size=4 \
    trainer.total_training_steps=10 \
    trainer.log_interval=1 \
    reward_manager.num_examine=2
```

### 9.3 常见问题

#### Q1: 数据加载失败

**报错**: `KeyError: 'prompt'`

**解决**:
- 检查 Parquet 文件的字段名
- 使用 `pd.read_parquet()` 验证数据

#### Q2: Reward 始终为 0

**原因**:
- `data_source` 不匹配
- 答案提取失败
- 标准化逻辑错误

**调试**:
- 启用 `num_examine` 打印详细信息
- 手动测试 `compute_score` 函数

#### Q3: Multi-turn 不工作

**原因**:
- `multi_turn.enable` 未设置
- `tool_config_path` 路径错误
- Tool 实现有 bug

**调试**:
- 检查配置文件
- 打印工具调用日志
- 逐个测试工具

#### Q4: 显存不足

**解决**:
- 减少 `train_batch_size`
- 减少 `max_prompt_length`
- 调整 `tensor_model_parallel_size`
- 启用 `gradient_checkpointing`

#### Q5: 训练不收敛

**原因**:
- Reward 设计不合理
- 学习率过大/过小
- 数据质量问题

**调试**:
- 检查 Reward 分布（使用 Wandb）
- 调整学习率
- 增加数据量

---

## 第十部分：总结

### 文件修改汇总表

| 组件 | 文件数 | 必需性 | 文件列表 |
|------|--------|--------|---------|
| **数据** | 3 | ✅ 必需 | 1. 预处理脚本<br>2. Parquet 文件<br>3. 配置 |
| **Reward** | 2-3 | ✅ 必需 | 1. 计分函数<br>2. 注册<br>3. (可选) 自定义 Manager |
| **配置** | 2-3 | ✅ 必需 | 1. 主配置<br>2. Tool 配置<br>3. (可选) 环境配置 |
| **Tool** | 2-4 | ❌ 可选 | 1. Tool 类<br>2. 注册<br>3. (可选) Schema<br>4. (可选) 配置 JSON |
| **Generation** | 1-2 | ❌ 可选 | 1. Generation Manager<br>2. (可选) 辅助函数 |
| **Trainer** | 1 | ❌ 可选 | 1. 自定义 Trainer |
| **启动** | 1-2 | ✅ 必需 | 1. 训练脚本<br>2. (可选) 评估脚本 |

**最少**: 7 个文件
**完整**: 15-20 个文件

### 快速决策树

```
是否需要 multi-turn？
├─ 否 → 最小版本 (7个文件)
│       数据 + Reward + 配置 + 启动脚本
│
└─ 是 → 是否需要复杂工具？
        ├─ 否 → 基础 multi-turn (10个文件)
        │       + Tool 配置文件
        │       + 简单 Tool Schema
        │
        └─ 是 → 完整版本 (15-20个文件)
                + Tool 实现
                + Generation Manager
                + 自定义 Trainer (可选)
```

### 参考时间估算

| 任务 | 预计时间 | 说明 |
|------|---------|------|
| 数据准备 | 2-4 小时 | 包括理解数据、编写脚本、验证 |
| Reward 实现 | 1-2 小时 | 简单任务；复杂任务可能需要 4-8 小时 |
| 配置编写 | 1 小时 | 基于模板修改 |
| Tool 实现 | 2-4 小时/工具 | 简单工具 2 小时，复杂工具 4+ 小时 |
| Generation Manager | 4-8 小时 | 如果需要自定义 |
| 调试和测试 | 4-8 小时 | 端到端测试和调优 |
| **总计** | | |
| 简单任务 | 1-2 天 | 单轮任务，简单 Reward |
| 中等任务 | 3-5 天 | Multi-turn，几个简单工具 |
| 复杂任务 | 1-2 周 | 完整 multi-turn，复杂工具，自定义逻辑 |

---

## 相关文档

- [环境集成指南](environment_integration.md) - 整体集成流程
- [数据接口规范](data_interface.md) - 数据格式详解
- [Reward 接口规范](reward_interface.md) - Reward 函数详解
- [训练配置规范](training_config.md) - 配置参数详解
- [配置与加载机制](config_and_loading.md) - 配置系统架构
- [Multi-Turn 逻辑实现](toolorchestra_multiturn_implementation.md) - Multi-turn 详解
- [上下文维护机制](context_maintenance_mechanism.md) - 上下文管理详解

---

**文档版本**: 1.0
**最后更新**: 2026-01-08
**维护者**: Claude Code

祝你接入顺利！🚀
