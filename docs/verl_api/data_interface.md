# 数据接口规范 (Data Interface)

## 概述

本文档详细说明如何准备和实现符合 verl 训练框架的数据接口。

---

## 1. 数据格式要求

### 1.1 文件格式

**推荐格式**: Parquet (.parquet)
- 支持高效的列式存储和读取
- 自动处理大文件
- 备选格式: JSON (.json)

### 1.2 必需字段

每条数据样本必须包含以下字段:

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `prompt` | List[Dict] | 对话历史 (chat template 格式) | `[{"role": "user", "content": "问题"}]` |
| `reward_model` | Dict | Reward 相关信息 | `{"ground_truth": "42"}` |
| `data_source` | String | 数据集来源标识 (用于路由 reward 函数) | `"openai/gsm8k"` |

### 1.3 可选字段

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `extra_info` | Dict | 额外信息 | `{"index": 0, "tools_kwargs": {...}}` |
| `images` | List | 图片数据 (多模态) | `[<PIL.Image>]` |
| `videos` | List | 视频数据 (多模态) | `[<numpy.array>]` |

### 1.4 数据示例

```python
# Parquet 文件中的一条记录
{
    "prompt": [
        {"role": "user", "content": "What is 25 + 17?"}
    ],
    "reward_model": {
        "ground_truth": "42"
    },
    "data_source": "openai/gsm8k",
    "extra_info": {
        "index": 0,
        "difficulty": "easy",
        "tools_kwargs": {
            "available_tools": ["calculator"]
        }
    }
}
```

---

## 2. Dataset 实现

### 2.1 使用默认 Dataset

verl 提供了 `RLHFDataset`，大多数情况下无需自定义:

```python
from verl.utils.dataset.rl_dataset import RLHFDataset

dataset = RLHFDataset(
    data_files=["path/to/train.parquet"],
    tokenizer=tokenizer,
    config=config,
    processor=None  # 多模态时需要
)
```

**输出格式** (`__getitem__` 返回):
```python
{
    "input_ids": torch.Tensor,        # shape: (max_prompt_length,)
    "attention_mask": torch.Tensor,   # shape: (max_prompt_length,)
    "position_ids": torch.Tensor,     # shape: (max_prompt_length,)
    "raw_prompt_ids": List[int],      # 原始 prompt token ids
    "reward_model": {                 # 传递给 RewardManager
        "ground_truth": str
    },
    "data_source": str,               # 用于路由 reward 函数
    "index": int,                     # 用于 GRPO 分组
    "tools_kwargs": dict,             # 可选: 工具调用参数
}
```

### 2.2 自定义 Dataset

如果需要特殊的数据处理逻辑，可以自定义 Dataset:

```python
from torch.utils.data import Dataset
from verl.utils.dataset.rl_dataset import RLHFDataset

class MyCustomDataset(RLHFDataset):
    """自定义数据集，继承自 RLHFDataset"""

    def __getitem__(self, item):
        # 1. 调用父类方法获取基础数据
        row_dict = super().__getitem__(item)

        # 2. 添加自定义处理
        # 例如: 添加特殊的 metadata
        row_dict["custom_metadata"] = self._process_custom_data(item)

        # 3. 修改字段 (如果需要)
        # 例如: 自定义 ground_truth 格式
        original_gt = row_dict["reward_model"]["ground_truth"]
        row_dict["reward_model"]["ground_truth"] = self._normalize_answer(original_gt)

        return row_dict

    def _process_custom_data(self, item):
        """自定义数据处理逻辑"""
        # 你的处理逻辑
        return {"custom_field": "value"}

    def _normalize_answer(self, answer):
        """归一化答案格式"""
        # 例如: 去除空格、统一大小写等
        return answer.strip().lower()
```

**在配置中使用自定义 Dataset**:

```yaml
data:
  custom_cls:
    path: "path/to/my_dataset.py"  # Python 文件路径
    name: "MyCustomDataset"         # 类名
```

### 2.3 Collate Function

verl 提供了默认的 `collate_fn`，无需自定义:

```python
from verl.utils.dataset.rl_dataset import collate_fn

# 自动将 List[Dict] 转为 batched Dict[str, Tensor/np.ndarray]
batch = collate_fn(data_list)
```

**Collate 行为**:
- Tensor 字段 → `torch.stack()` → `torch.Tensor[batch_size, ...]`
- 非 Tensor 字段 → `np.array(..., dtype=object)` → `np.ndarray[batch_size]`

---

## 3. 数据配置参数

### 3.1 基础配置

```yaml
data:
  # 数据文件路径
  train_files: ~/data/gsm8k/train.parquet  # 可以是列表
  val_files: ~/data/gsm8k/test.parquet

  # 字段映射
  prompt_key: prompt          # prompt 字段名
  reward_fn_key: data_source  # reward 函数路由键

  # 长度限制
  max_prompt_length: 512      # 最大 prompt 长度
  max_response_length: 512    # 最大 response 长度

  # Batch size
  train_batch_size: 1024
  val_batch_size: null        # null 表示使用 train_batch_size

  # 数据处理
  shuffle: True               # 是否打乱训练数据
  validation_shuffle: False   # 是否打乱验证数据
  filter_overlong_prompts: True  # 是否过滤过长 prompt
  truncation: error           # 'error' | 'left' | 'right' | 'middle'
```

### 3.2 高级配置

```yaml
data:
  # 返回额外信息
  return_raw_chat: True        # 返回原始 chat 格式
  return_full_prompt: True     # 返回完整 prompt 字符串
  return_raw_input_ids: False  # 返回未应用 chat template 的 input_ids

  # 多模态
  image_key: images            # 图片字段名
  video_key: videos            # 视频字段名

  # 工具调用
  need_tools_kwargs: True      # 是否需要 tools_kwargs

  # 性能优化
  use_shm: False               # 是否使用共享内存加速
  filter_overlong_prompts_workers: 4  # 过滤时的并行进程数

  # 安全性
  trust_remote_code: False     # 是否信任远程代码

  # 自定义 Dataset
  custom_cls:
    path: null
    name: null
```

---

## 4. 数据准备流程

### 4.1 准备 Parquet 文件

```python
import pandas as pd

# 示例: 准备 GSM8K 数据
data = []
for item in original_dataset:
    data.append({
        "prompt": [
            {"role": "user", "content": item["question"]}
        ],
        "reward_model": {
            "ground_truth": item["answer"].split("#### ")[-1]
        },
        "data_source": "openai/gsm8k",
        "extra_info": {
            "index": item["idx"],
        }
    })

# 保存为 Parquet
df = pd.DataFrame(data)
df.to_parquet("train.parquet", index=False)
```

### 4.2 验证数据格式

```python
import pandas as pd

# 读取并检查
df = pd.read_parquet("train.parquet")
print(df.head())
print(df.columns)

# 检查必需字段
required_fields = ["prompt", "reward_model", "data_source"]
for field in required_fields:
    assert field in df.columns, f"Missing field: {field}"

# 检查 prompt 格式
sample_prompt = df.iloc[0]["prompt"]
assert isinstance(sample_prompt, list), "prompt must be a list"
assert all("role" in msg and "content" in msg for msg in sample_prompt), \
    "Each message must have 'role' and 'content'"
```

### 4.3 测试 Dataset 加载

```python
from transformers import AutoTokenizer
from verl.utils.dataset.rl_dataset import RLHFDataset
from omegaconf import DictConfig

# 初始化 tokenizer
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")

# 配置
config = DictConfig({
    "max_prompt_length": 512,
    "max_response_length": 512,
    "prompt_key": "prompt",
    "filter_overlong_prompts": True,
    "truncation": "error",
})

# 加载 Dataset
dataset = RLHFDataset(
    data_files=["train.parquet"],
    tokenizer=tokenizer,
    config=config,
)

# 测试
sample = dataset[0]
print("Sample keys:", sample.keys())
print("Input shape:", sample["input_ids"].shape)
print("Data source:", sample["data_source"])
print("Ground truth:", sample["reward_model"]["ground_truth"])
```

---

## 5. 常见问题

### Q1: 如何处理多轮对话?

```python
# prompt 中包含多轮历史
{
    "prompt": [
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "4"},
        {"role": "user", "content": "What about 3+3?"}
    ],
    ...
}
```

启用 multi-turn 配置:
```yaml
actor_rollout_ref:
  rollout:
    multi_turn:
      enable: True
      max_turns: 5
```

### Q2: 如何处理多个 ground_truth?

```python
# 在 reward_model 中存储多个答案
{
    "reward_model": {
        "ground_truth": ["42", "forty-two", "forty two"]
    },
    ...
}
```

在自定义 `compute_score` 中处理:
```python
def compute_score(data_source, solution_str, ground_truth, extra_info=None):
    # ground_truth 可以是 list
    if isinstance(ground_truth, list):
        return any(solution_str == gt for gt in ground_truth)
    else:
        return solution_str == ground_truth
```

### Q3: 如何支持不同的数据集混合训练?

```python
# 方式1: 多个 Parquet 文件
data:
  train_files:
    - ~/data/gsm8k/train.parquet
    - ~/data/math/train.parquet
    - ~/data/code/train.parquet

# 方式2: 合并到一个 Parquet，使用 data_source 区分
data = []
for item in gsm8k_dataset:
    data.append({..., "data_source": "openai/gsm8k"})
for item in math_dataset:
    data.append({..., "data_source": "lighteval/MATH"})
```

### Q4: 如何处理多模态数据?

```python
from PIL import Image

# 在 Parquet 中存储图片路径或 bytes
{
    "prompt": [
        {"role": "user", "content": "Describe this image <image>"}
    ],
    "images": ["/path/to/image.jpg"],  # 或者 PIL.Image 对象
    ...
}
```

在配置中:
```yaml
data:
  image_key: images
  video_key: videos
```

---

## 6. 最佳实践

1. **数据验证**: 训练前使用脚本验证所有字段完整性
2. **长度控制**:
   - 设置合理的 `max_prompt_length` 和 `max_response_length`
   - 使用 `filter_overlong_prompts=True` 过滤异常数据
3. **Ground Truth 格式**: 保持一致的格式（大小写、空格、符号）
4. **Data Source**: 使用标准的数据集名称便于复用 reward 函数
5. **索引字段**: 为 GRPO/RLOO 等算法添加 `index` 字段用于分组
6. **缓存策略**: 大数据集使用 `cache_dir` 避免重复下载

---

## 7. 参考实现

完整的数据准备示例: `.reference_projects/ToolOrchestra/data_synthesis/`

默认 Dataset 实现: `.reference_projects/ToolOrchestra/training/verl/utils/dataset/rl_dataset.py`