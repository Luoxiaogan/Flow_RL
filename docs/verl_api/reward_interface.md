# Reward 接口规范 (Reward Interface)

## 概述

本文档详细说明如何实现符合 verl 训练框架的 Reward 计算接口。

---

## 1. Reward 系统架构

### 1.1 两层架构

verl 的 Reward 系统采用两层设计:

```
RewardManager (管理层)
    ↓
compute_score (计算层)
```

**职责分工**:
- **RewardManager**: 负责批量处理、并行化、后处理（如 length penalty）
- **compute_score**: 负责单个样本的 reward 计算逻辑

### 1.2 调用流程

```
训练循环
  → reward_fn(data: DataProto)  # RewardManager.__call__
    → 遍历 batch 中每个样本
      → compute_score(data_source, solution_str, ground_truth)
        → 根据 data_source 路由到具体的评分函数
          → 返回 score (float)
    → 组装成 reward_tensor
  → 返回 reward_tensor
```

---

## 2. compute_score 接口

### 2.1 函数签名

```python
def compute_score(
    data_source: str,
    solution_str: str,
    ground_truth: str,
    extra_info: Optional[dict] = None,
    sandbox_fusion_url: Optional[str] = None,
    concurrent_semaphore: Optional[object] = None,
    **kwargs
) -> Union[float, dict]:
    """
    计算单个样本的 reward score

    Args:
        data_source: 数据集来源标识，用于路由到不同的评分逻辑
                     例如: "openai/gsm8k", "lighteval/MATH", "codecontests"
        solution_str: 模型生成的解答文本
        ground_truth: 标准答案
        extra_info: 额外信息，如测试用例、工具调用记录等
        sandbox_fusion_url: 代码执行沙箱的 URL (用于代码任务)
        concurrent_semaphore: 并发控制信号量
        **kwargs: 其他自定义参数

    Returns:
        float: 单个 score 值 (0.0 ~ 1.0)
        或
        dict: 包含 'score' 及其他 metrics 的字典
              例如: {"score": 1.0, "format_correct": True, "exact_match": True}
    """
    pass
```

### 2.2 返回值规范

#### 方式 1: 返回 float

```python
def compute_score(data_source, solution_str, ground_truth, **kwargs):
    if is_correct(solution_str, ground_truth):
        return 1.0  # 正确
    else:
        return 0.0  # 错误
```

#### 方式 2: 返回 dict (推荐)

```python
def compute_score(data_source, solution_str, ground_truth, **kwargs):
    result = {
        "score": 0.0,           # 必需: 最终 reward 值
        "exact_match": False,   # 可选: 额外 metrics
        "format_correct": False,
        "partial_score": 0.0,
    }

    # 评分逻辑
    if is_correct(solution_str, ground_truth):
        result["score"] = 1.0
        result["exact_match"] = True
    elif has_correct_format(solution_str):
        result["score"] = 0.1  # 格式分
        result["format_correct"] = True

    return result
```

**返回 dict 的优势**:
- 可以记录更多诊断信息
- 便于分析模型行为
- 支持多维度 reward 设计

---

## 3. 实现 compute_score

### 3.1 简单实现: 精确匹配

```python
def compute_score(data_source, solution_str, ground_truth, **kwargs):
    """最简单的实现: 精确字符串匹配"""
    if solution_str.strip() == ground_truth.strip():
        return 1.0
    else:
        return 0.0
```

### 3.2 数学题实现: GSM8K

```python
import re

def extract_answer(solution_str):
    """从解答中提取最终答案"""
    # 方式1: 严格格式 (要求 #### 分隔符)
    match = re.search(r"####\s*([-]?[0-9\.\,]+)", solution_str)
    if match:
        answer = match.group(1).replace(",", "")
        return answer

    # 方式2: 灵活格式 (提取最后一个数字)
    numbers = re.findall(r"([-]?[0-9\.\,]+)", solution_str)
    if numbers:
        return numbers[-1].replace(",", "")

    return None

def compute_score(data_source, solution_str, ground_truth, **kwargs):
    """GSM8K 评分函数"""
    if data_source != "openai/gsm8k":
        return 0.0

    answer = extract_answer(solution_str)

    if answer is None:
        return 0.0  # 无法提取答案
    elif answer == ground_truth:
        return 1.0  # 正确
    else:
        return 0.0  # 错误
```

### 3.3 代码任务实现: 带测试用例

```python
import subprocess
import json

def execute_code_with_tests(code: str, test_cases: list, timeout: int = 5):
    """在沙箱中执行代码并运行测试用例"""
    passed = 0
    total = len(test_cases)

    for test in test_cases:
        try:
            # 构造测试代码
            test_code = f"{code}\n\n{test['test_code']}"

            # 执行 (需要沙箱环境)
            result = subprocess.run(
                ["python", "-c", test_code],
                capture_output=True,
                timeout=timeout,
                text=True
            )

            # 检查结果
            if result.returncode == 0:
                passed += 1
        except subprocess.TimeoutExpired:
            continue  # 超时视为失败
        except Exception as e:
            continue  # 其他错误视为失败

    return passed / total if total > 0 else 0.0

def compute_score(data_source, solution_str, ground_truth, extra_info=None, **kwargs):
    """代码任务评分函数"""
    if data_source not in ["codecontests", "apps"]:
        return 0.0

    # ground_truth 包含测试用例
    test_cases = json.loads(ground_truth)

    # 从 solution 中提取代码
    code = extract_code_block(solution_str)
    if not code:
        return 0.0

    # 执行测试
    score = execute_code_with_tests(code, test_cases)

    return {
        "score": score,
        "passed_tests": int(score * len(test_cases)),
        "total_tests": len(test_cases),
    }

def extract_code_block(solution_str):
    """从 markdown 中提取代码块"""
    match = re.search(r"```python\n(.*?)\n```", solution_str, re.DOTALL)
    if match:
        return match.group(1)
    return None
```

### 3.4 多路由实现: default_compute_score

```python
def default_compute_score(data_source, solution_str, ground_truth, extra_info=None, **kwargs):
    """
    根据 data_source 路由到不同的评分函数
    这是 verl 默认提供的实现
    """
    # 数学题
    if data_source == "openai/gsm8k":
        from verl.utils.reward_score import gsm8k
        return gsm8k.compute_score(solution_str, ground_truth)

    elif data_source in ["lighteval/MATH", "DigitalLearningGmbH/MATH-lighteval"]:
        from verl.utils.reward_score import math
        return math.compute_score(solution_str, ground_truth)

    # 代码题
    elif data_source in ["codecontests", "apps", "codeforces"]:
        from verl.utils.reward_score import sandbox_fusion
        sandbox_url = kwargs.get("sandbox_fusion_url")
        semaphore = kwargs.get("concurrent_semaphore")
        return sandbox_fusion.compute_score(sandbox_url, semaphore, solution_str, ground_truth)

    # QA 任务
    elif data_source.startswith("searchR1_"):
        from verl.utils.reward_score import search_r1_like_qa_em
        return search_r1_like_qa_em.compute_score(solution_str, ground_truth)

    else:
        raise NotImplementedError(f"Reward function not implemented for {data_source=}")
```

---

## 4. RewardManager 接口

### 4.1 使用默认 RewardManager

大多数情况下使用 `NaiveRewardManager`:

```python
from verl.workers.reward_manager import NaiveRewardManager

reward_manager = NaiveRewardManager(
    tokenizer=tokenizer,
    num_examine=5,  # 打印前 5 个样本用于调试
    compute_score=my_compute_score,  # 自定义 compute_score
    reward_fn_key="data_source",
)
```

### 4.2 自定义 RewardManager

```python
from verl.workers.reward_manager import register
from verl import DataProto
import torch

@register("my_custom_rm")
class MyCustomRewardManager:
    """自定义 RewardManager"""

    def __init__(self, tokenizer, num_examine, compute_score=None, reward_fn_key="data_source"):
        self.tokenizer = tokenizer
        self.num_examine = num_examine
        self.compute_score = compute_score or default_compute_score
        self.reward_fn_key = reward_fn_key

    def __call__(self, data: DataProto, return_dict=False):
        """
        核心方法: 计算整个 batch 的 reward

        Args:
            data: DataProto 对象，包含:
                - data.batch: Dict[str, Tensor], 包含 prompts, responses, attention_mask 等
                - data.non_tensor_batch: Dict[str, np.ndarray], 包含 reward_model, data_source 等

        Returns:
            reward_tensor: shape (batch_size, response_length)
                          reward 只放在序列的最后一个有效 token 位置
        """
        # 1. 初始化 reward tensor
        reward_tensor = torch.zeros_like(data.batch["responses"], dtype=torch.float32)
        reward_extra_info = {}

        # 2. 遍历 batch 中每个样本
        for i in range(len(data)):
            data_item = data[i]  # 获取单个样本

            # 3. 解码 prompt 和 response
            prompt_ids = data_item.batch["prompts"]
            response_ids = data_item.batch["responses"]
            attention_mask = data_item.batch["attention_mask"]

            # 获取有效长度
            prompt_length = prompt_ids.shape[-1]
            valid_response_length = attention_mask[prompt_length:].sum()
            valid_response_ids = response_ids[:valid_response_length]

            # 解码
            response_str = self.tokenizer.decode(valid_response_ids, skip_special_tokens=True)

            # 4. 获取 ground_truth 和 data_source
            ground_truth = data_item.non_tensor_batch["reward_model"]["ground_truth"]
            data_source = data_item.non_tensor_batch[self.reward_fn_key]
            extra_info = data_item.non_tensor_batch.get("extra_info", None)

            # 5. 计算 score
            score_result = self.compute_score(
                data_source=data_source,
                solution_str=response_str,
                ground_truth=ground_truth,
                extra_info=extra_info,
            )

            # 6. 提取 reward 值
            if isinstance(score_result, dict):
                reward = score_result["score"]
                # 存储额外信息
                for key, value in score_result.items():
                    if key not in reward_extra_info:
                        reward_extra_info[key] = []
                    reward_extra_info[key].append(value)
            else:
                reward = score_result

            # 7. 将 reward 放在最后一个有效 token 位置
            reward_tensor[i, valid_response_length - 1] = reward

        # 8. 返回结果
        if return_dict:
            return {
                "reward_tensor": reward_tensor,
                "reward_extra_info": reward_extra_info,
            }
        else:
            return reward_tensor
```

### 4.3 高级 RewardManager: PrimeRewardManager

支持异步并行计算和后处理:

```python
from verl.nvidia.reward_manager import PrimeRewardManager

@ray.remote
class PrimeRewardManager:
    def __init__(self, tokenizer, config, compute_score=None):
        self.tokenizer = tokenizer
        self.compute_score = compute_score
        self.use_remote_reward = config.use_remote_reward
        self.max_concurrency = config.max_concurrency

        # 后处理组件
        self.length_penalty = None
        self.stop_properly_penalty = None

    def __call__(self, data: DataProto):
        # 1. 批量解码
        completions = [self.tokenizer.decode(...) for _ in data]
        references = [item["reward_model"]["ground_truth"] for item in data.non_tensor_batch]
        tasks = [item["data_source"] for item in data.non_tensor_batch]

        # 2. 异步并行计算 (使用 asyncio + ProcessPoolExecutor)
        if self.use_remote_reward:
            # 远程 reward server
            scores = asyncio.run(
                parallel_remote_score_async(completions, references, tasks, self.max_concurrency)
            )
        else:
            # 本地并行计算
            scores = asyncio.run(
                parallel_compute_score_async(self.compute_score, completions, references, tasks, num_processes=64)
            )

        # 3. 组装 reward_tensor
        reward_tensor = torch.zeros_like(data.batch["responses"], dtype=torch.float32)
        for i, score in enumerate(scores):
            valid_length = data.batch["attention_mask"][i].sum()
            reward_tensor[i, valid_length - 1] = score

        # 4. 应用后处理
        if self.length_penalty:
            reward_tensor = self._apply_length_penalty(reward_tensor, data)

        if self.stop_properly_penalty:
            reward_tensor = self._apply_stop_properly_penalty(reward_tensor, data)

        return reward_tensor

    def _apply_length_penalty(self, reward_tensor, data):
        """惩罚过长或过短的回答"""
        lengths = data.batch["attention_mask"].sum(dim=-1)
        penalty = self.length_penalty.compute_penalty(lengths)
        return reward_tensor * penalty.unsqueeze(-1)
```

---

## 5. Reward 配置

### 5.1 基础配置

```yaml
reward_manager:
  type: naive  # naive | prime | batch | dapo
  num_examine: 5  # 打印调试样本数
  reward_fn_key: data_source  # 路由键
```

### 5.2 使用自定义 compute_score

```yaml
reward_manager:
  type: naive
  custom_reward_function:
    path: "path/to/my_reward.py"
    name: "my_compute_score"
    reward_kwargs:  # 传递给 compute_score 的额外参数
      threshold: 0.8
      use_fuzzy_match: True
```

对应的实现:

```python
# my_reward.py
def my_compute_score(data_source, solution_str, ground_truth, extra_info=None, threshold=0.8, use_fuzzy_match=False):
    """自定义 compute_score，支持额外参数"""
    # 你的评分逻辑
    if use_fuzzy_match:
        similarity = compute_similarity(solution_str, ground_truth)
        return 1.0 if similarity >= threshold else 0.0
    else:
        return 1.0 if solution_str == ground_truth else 0.0
```

### 5.3 代码沙箱配置

```yaml
reward_manager:
  type: prime
  sandbox_fusion:
    url: "http://localhost:8000/execute"
    max_concurrent: 64  # 并发执行数
```

### 5.4 高级后处理

```yaml
reward_manager:
  type: prime
  use_remote_reward: False
  max_concurrency: 1024
  binary_score: False  # 是否二值化 score

  # Length Penalty
  length_penalty:
    enable: True
    min_length: 10
    max_length: 512
    penalty_coef: 0.5

  # Stop Properly Penalty (惩罚未正确结束的生成)
  stop_properly_penalty:
    enable: True
    penalty_coef: 0.1
```

---

## 6. Reward 后处理

### 6.1 Length Penalty

```python
from verl.nvidia.reward_manager.length_penalty import LengthPenalty

length_penalty = LengthPenalty(
    min_length=10,
    max_length=512,
    penalty_coef=0.5
)

# 应用 penalty
penalty_scale = length_penalty.compute_penalty(response_lengths)
reward_tensor = reward_tensor * penalty_scale.unsqueeze(-1)
```

**效果**:
- 响应长度在 `[min_length, max_length]` 区间内: penalty = 1.0 (无惩罚)
- 超出范围: penalty = penalty_coef (例如 0.5)

### 6.2 Stop Properly Penalty

```python
def _apply_stop_properly_penalty(self, reward_tensor, batch):
    """惩罚未正确停止的生成 (没有生成 EOS token)"""
    stop_properly = batch.batch['stop_properly']  # shape: (bs,)

    # stop_properly == 1.0 表示正确停止
    # stop_properly == 0.0 表示未正确停止
    penalty_scale = (1.0 - stop_properly) * self.stop_penalty_coef + stop_properly

    return reward_tensor * penalty_scale.unsqueeze(-1)
```

### 6.3 KL Penalty (在 Advantage 阶段)

```python
# 在 ray_trainer.py 的 apply_kl_penalty 中
kld = old_log_prob - ref_log_prob
token_level_rewards = token_level_scores - beta * kld
```

---

## 7. 调试和测试

### 7.1 单独测试 compute_score

```python
def test_compute_score():
    # 测试正确答案
    score = compute_score(
        data_source="openai/gsm8k",
        solution_str="The answer is 42\n#### 42",
        ground_truth="42"
    )
    assert score == 1.0, f"Expected 1.0, got {score}"

    # 测试错误答案
    score = compute_score(
        data_source="openai/gsm8k",
        solution_str="The answer is 100\n#### 100",
        ground_truth="42"
    )
    assert score == 0.0, f"Expected 0.0, got {score}"

    # 测试格式错误
    score = compute_score(
        data_source="openai/gsm8k",
        solution_str="I don't know",
        ground_truth="42"
    )
    assert score == 0.0, f"Expected 0.0, got {score}"

    print("All tests passed!")

test_compute_score()
```

### 7.2 测试 RewardManager

```python
from verl import DataProto
from verl.workers.reward_manager import NaiveRewardManager

# 构造测试数据
test_data = DataProto()
test_data.batch = {
    "prompts": torch.randint(0, 1000, (2, 10)),
    "responses": torch.randint(0, 1000, (2, 20)),
    "attention_mask": torch.ones(2, 30),
}
test_data.non_tensor_batch = {
    "reward_model": np.array([
        {"ground_truth": "42"},
        {"ground_truth": "100"}
    ], dtype=object),
    "data_source": np.array(["openai/gsm8k", "openai/gsm8k"], dtype=object),
}

# 初始化 RewardManager
reward_manager = NaiveRewardManager(
    tokenizer=tokenizer,
    num_examine=2,
    compute_score=my_compute_score,
)

# 计算 reward
reward_tensor = reward_manager(test_data)
print("Reward tensor shape:", reward_tensor.shape)
print("Reward values:", reward_tensor)
```

### 7.3 启用调试输出

```yaml
reward_manager:
  num_examine: 10  # 打印前 10 个样本的详细信息
```

输出示例:
```
[prompt] What is 25 + 17?
[response] Let me calculate: 25 + 17 = 42\n#### 42
[ground_truth] 42
[score] 1.0
[exact_match] True
[format_correct] True
```

---

## 8. 常见问题

### Q1: 如何支持多种评分标准?

```python
def compute_score(data_source, solution_str, ground_truth, extra_info=None, **kwargs):
    result = {
        "score": 0.0,
        "exact_match": 0.0,
        "fuzzy_match": 0.0,
    }

    # 精确匹配
    if solution_str.strip() == ground_truth.strip():
        result["exact_match"] = 1.0
        result["score"] = 1.0

    # 模糊匹配
    elif fuzzy_compare(solution_str, ground_truth):
        result["fuzzy_match"] = 1.0
        result["score"] = 0.8

    return result
```

### Q2: 如何实现分层 reward?

```python
def compute_score(data_source, solution_str, ground_truth, **kwargs):
    score = 0.0

    # 格式分 (0.1)
    if has_correct_format(solution_str):
        score += 0.1

    # 中间步骤分 (0.4)
    if has_reasoning_steps(solution_str):
        score += 0.4

    # 最终答案分 (0.5)
    if extract_answer(solution_str) == ground_truth:
        score += 0.5

    return score
```

### Q3: 如何处理超时任务?

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutError()

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def compute_score(data_source, solution_str, ground_truth, **kwargs):
    try:
        with timeout(5):  # 5 秒超时
            return expensive_evaluation(solution_str, ground_truth)
    except TimeoutError:
        return 0.0  # 超时视为失败
```

### Q4: 如何实现 Pass@k reward?

```python
# 需要配合 GRPO_PASSK advantage estimator
def compute_score(data_source, solution_str, ground_truth, **kwargs):
    # 执行测试，返回通过率
    passed, total = run_tests(solution_str, ground_truth)
    return passed / total if total > 0 else 0.0
```

在配置中:
```yaml
algorithm:
  adv_estimator: grpo_passk

actor_rollout_ref:
  rollout:
    n: 16  # 每个 prompt 生成 16 个 solutions
```

---

## 9. 最佳实践

1. **返回 dict**: 使用 dict 返回值以便记录更多 metrics
2. **异常处理**: compute_score 应该捕获所有异常，避免训练中断
3. **归一化**: 确保 score 在合理范围内 (通常 0.0 ~ 1.0)
4. **格式鲁棒**: 对不同的答案格式保持容错性
5. **可复现**: 避免在 compute_score 中使用随机性
6. **性能优化**: 对于慢速评分（如代码执行），使用 PrimeRewardManager 的并行化
7. **分层设计**: 格式分 + 内容分，鼓励模型学习正确格式

---

## 10. 参考实现

完整的 reward 实现示例:
- GSM8K: `.reference_projects/ToolOrchestra/training/verl/utils/reward_score/gsm8k.py`
- MATH: `.reference_projects/ToolOrchestra/training/verl/utils/reward_score/math.py`
- Code: `.reference_projects/ToolOrchestra/training/verl/utils/reward_score/sandbox_fusion/`
- Prime: `.reference_projects/ToolOrchestra/training/verl/nvidia/reward_manager/prime.py`
