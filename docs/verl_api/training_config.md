# 训练配置规范 (Training Configuration)

## 概述

本文档详细说明 verl 训练框架的配置系统，包括所有配置项的含义、默认值和最佳实践。

---

## 1. 配置系统架构

### 1.1 Hydra 配置管理

verl 使用 **Hydra** 进行配置管理，支持:
- ✅ **分层配置**: 基础配置 + 任务配置 + 命令行覆盖
- ✅ **配置继承**: 通过 `defaults` 继承其他配置
- ✅ **变量插值**: 使用 `${var}` 引用其他配置项
- ✅ **配置验证**: 启动前验证配置完整性

### 1.2 配置文件组织

```
training/verl/trainer/config/
├── ppo_trainer.yaml           # 基础 PPO 配置
├── ppo_megatron_trainer.yaml  # Megatron 后端配置
├── sft_trainer.yaml           # SFT 配置
└── generation.yaml            # Generation 配置

your_project/config/
├── your_task.yaml             # 任务特定配置
└── tool_config/
    └── your_tool_config.yaml  # 工具配置
```

### 1.3 配置优先级

```
命令行参数 (最高优先级)
    ↓
任务配置 (your_task.yaml)
    ↓
基础配置 (ppo_trainer.yaml)
    ↓
默认值 (最低优先级)
```

---

## 2. 完整配置结构

### 2.1 配置文件模板

```yaml
# your_task.yaml
hydra:
  searchpath:
    - file://verl/trainer/config  # 搜索路径

defaults:
  - ppo_trainer  # 继承基础配置
  - _self_       # 当前配置优先级最高

# ==================== 数据配置 ====================
data:
  # 数据文件
  train_files: ~/data/your_task/train.parquet
  val_files: ~/data/your_task/test.parquet

  # 字段映射
  prompt_key: prompt
  reward_fn_key: data_source

  # 长度限制
  max_prompt_length: 512
  max_response_length: 512

  # Batch size
  train_batch_size: 1024
  val_batch_size: null

  # 数据处理
  shuffle: True
  filter_overlong_prompts: True
  truncation: error

# ==================== Reward 配置 ====================
reward_manager:
  type: prime
  num_examine: 5
  use_remote_reward: False
  max_concurrency: 1024

# ==================== 模型和训练配置 ====================
actor_rollout_ref:
  hybrid_engine: true

  # 模型配置
  model:
    path: ~/models/Qwen/Qwen2.5-7B-Instruct
    use_shm: false
    enable_gradient_checkpointing: true
    lora_rank: 0

  # Actor 配置
  actor:
    strategy: fsdp
    optim:
      lr: 1e-6
    ppo_mini_batch_size: 256
    ppo_micro_batch_size_per_gpu: 32
    use_kl_loss: True
    kl_loss_coef: 0.001

  # Rollout 配置
  rollout:
    name: sglang
    n: 16
    temperature: 0.7
    top_p: 0.95

  # Reference Policy 配置
  ref:
    log_prob_micro_batch_size_per_gpu: 32

# ==================== 算法配置 ====================
algorithm:
  adv_estimator: grpo
  gamma: 1.0
  lam: 0.95
  use_kl_in_reward: False

# ==================== 训练器配置 ====================
trainer:
  total_epochs: 15
  save_freq: 100
  test_freq: 20
  n_gpus_per_node: 8
  nnodes: 1
  logger: ['console', 'wandb']
  project_name: 'your_project'
  experiment_name: 'your_experiment'

# ==================== Critic 配置 (可选) ====================
critic:
  strategy: fsdp
  optim:
    lr: 1e-5

# ==================== Reward Model 配置 (可选) ====================
reward_model:
  enable: False
  strategy: fsdp
  path: ~/models/reward_model
```

---

## 3. 配置项详解

### 3.1 数据配置 (data)

#### 基础配置

```yaml
data:
  # ========== 数据文件 ==========
  train_files: ~/data/gsm8k/train.parquet
    # 类型: str | List[str]
    # 说明: 训练数据文件路径，支持本地路径或 HDFS 路径
    # 示例: [~/data/gsm8k/train.parquet, ~/data/math/train.parquet]

  val_files: ~/data/gsm8k/test.parquet
    # 类型: str | List[str]
    # 说明: 验证数据文件路径

  # ========== 字段映射 ==========
  prompt_key: prompt
    # 类型: str
    # 说明: prompt 字段名
    # 默认: 'prompt'

  reward_fn_key: data_source
    # 类型: str
    # 说明: 用于路由 reward 函数的字段名
    # 默认: 'data_source'

  image_key: images
    # 类型: str
    # 说明: 多模态图片字段名
    # 默认: 'images'

  video_key: videos
    # 类型: str
    # 说明: 多模态视频字段名
    # 默认: 'videos'

  # ========== 长度限制 ==========
  max_prompt_length: 512
    # 类型: int
    # 说明: 最大 prompt 长度（tokens）
    # 建议: 根据任务设置，通常 512-2048

  max_response_length: 512
    # 类型: int
    # 说明: 最大 response 长度（tokens）
    # 建议: GSM8K=512, Code=2048, Long-form QA=4096

  # ========== Batch Size ==========
  train_batch_size: 1024
    # 类型: int
    # 说明: 训练时的 global batch size
    # 计算: train_batch_size = n_gpus * n_responses_per_prompt
    # 示例: 8 GPUs * 16 responses = 128 (实际数据样本数)

  val_batch_size: null
    # 类型: int | null
    # 说明: 验证时的 batch size，null 表示使用 train_batch_size

  # ========== 数据处理 ==========
  shuffle: True
    # 类型: bool
    # 说明: 是否打乱训练数据

  validation_shuffle: False
    # 类型: bool
    # 说明: 是否打乱验证数据

  filter_overlong_prompts: True
    # 类型: bool
    # 说明: 是否过滤超过 max_prompt_length 的样本

  filter_overlong_prompts_workers: 4
    # 类型: int
    # 说明: 过滤时的并行进程数
    # 建议: max(1, os.cpu_count() // 4)

  truncation: error
    # 类型: str
    # 选项: 'error' | 'left' | 'right' | 'middle'
    # 说明: prompt 超长时的处理策略
    #   - error: 抛出异常
    #   - left: 截断左侧（保留最新对话）
    #   - right: 截断右侧
    #   - middle: 截断中间部分

  # ========== 返回额外信息 ==========
  return_raw_chat: False
    # 类型: bool
    # 说明: 是否返回原始 chat 格式（未应用 chat template）

  return_full_prompt: False
    # 类型: bool
    # 说明: 是否返回完整 prompt 字符串

  return_raw_input_ids: False
    # 类型: bool
    # 说明: 是否返回未应用 chat template 的 input_ids
    # 用途: 当 reward model 使用不同 chat template 时

  # ========== 工具调用 ==========
  need_tools_kwargs: False
    # 类型: bool
    # 说明: 是否需要 tools_kwargs 字段

  # ========== 性能优化 ==========
  use_shm: False
    # 类型: bool
    # 说明: 是否使用共享内存加速数据加载

  # ========== 安全性 ==========
  trust_remote_code: False
    # 类型: bool
    # 说明: 是否信任远程代码（tokenizer 中的 Python 文件）

  # ========== 自定义 Dataset ==========
  custom_cls:
    path: null
      # 类型: str | null
      # 说明: 自定义 Dataset 类的文件路径
      # 示例: "path/to/my_dataset.py"

    name: null
      # 类型: str | null
      # 说明: 自定义 Dataset 类名
      # 示例: "MyCustomDataset"
```

---

### 3.2 Reward Manager 配置 (reward_manager)

```yaml
reward_manager:
  # ========== 基础配置 ==========
  type: prime
    # 类型: str
    # 选项: 'naive' | 'prime' | 'batch' | 'dapo'
    # 说明: RewardManager 类型
    #   - naive: 简单实现，逐样本计算
    #   - prime: 高级实现，支持异步并行
    #   - batch: 批量计算
    #   - dapo: DAPO 算法专用

  num_examine: 5
    # 类型: int
    # 说明: 打印前 N 个样本用于调试
    # 建议: 训练时设为 0-5，调试时设为 10-20

  reward_fn_key: data_source
    # 类型: str
    # 说明: 路由 reward 函数的字段名（应与 data.reward_fn_key 一致）

  # ========== 远程 Reward Server (PrimeRewardManager) ==========
  use_remote_reward: False
    # 类型: bool
    # 说明: 是否使用远程 reward server

  server_ip: localhost
    # 类型: str | List[str]
    # 说明: Reward server 的 IP 地址列表

  max_concurrency: 1024
    # 类型: int
    # 说明: 最大并发请求数
    # 建议: >= 64 per node

  # ========== 自定义 Reward 函数 ==========
  custom_reward_function:
    path: null
      # 类型: str | null
      # 说明: 自定义 compute_score 函数的文件路径
      # 示例: "path/to/my_reward.py"

    name: null
      # 类型: str | null
      # 说明: 自定义 compute_score 函数名
      # 示例: "my_compute_score"

    reward_kwargs:
      # 类型: dict
      # 说明: 传递给 compute_score 的额外参数
      # 示例:
      #   threshold: 0.8
      #   use_fuzzy_match: True

  # ========== 代码沙箱 (用于代码任务) ==========
  sandbox_fusion:
    url: null
      # 类型: str | null
      # 说明: 代码执行沙箱的 URL
      # 示例: "http://localhost:8000/execute"

    max_concurrent: 64
      # 类型: int
      # 说明: 最大并发执行数

  # ========== 后处理 (PrimeRewardManager) ==========
  binary_score: False
    # 类型: bool
    # 说明: 是否将 score 二值化（0 或 1）

  length_penalty:
    enable: False
      # 类型: bool
      # 说明: 是否启用长度惩罚

    min_length: 10
      # 类型: int
      # 说明: 最小响应长度

    max_length: 512
      # 类型: int
      # 说明: 最大响应长度

    penalty_coef: 0.5
      # 类型: float
      # 说明: 惩罚系数（超出范围时 reward *= penalty_coef）

  stop_properly_penalty:
    enable: False
      # 类型: bool
      # 说明: 是否惩罚未正确停止的生成（没有 EOS）

    penalty_coef: 0.1
      # 类型: float
      # 说明: 惩罚系数
```

---

### 3.3 模型配置 (actor_rollout_ref)

```yaml
actor_rollout_ref:
  # ========== 引擎模式 ==========
  hybrid_engine: true
    # 类型: bool
    # 说明: 是否使用混合引擎（Actor + Rollout 共享）
    # 当前仅支持 true

  # ==================== 模型配置 ====================
  model:
    # ========== 模型路径 ==========
    path: ~/models/Qwen/Qwen2.5-7B-Instruct
      # 类型: str
      # 说明: HuggingFace 模型路径（本地或 HDFS）

    use_shm: false
      # 类型: bool
      # 说明: 是否使用共享内存加载模型权重

    external_lib: null
      # 类型: str | null
      # 说明: 外部库路径（用于注册自定义模型）

    # ========== 模型配置覆盖 ==========
    override_config: {}
      # 类型: dict
      # 说明: 覆盖模型的原始配置
      # 示例:
      #   attention_dropout: 0.0
      #   hidden_dropout: 0.0

    # ========== 优化配置 ==========
    enable_gradient_checkpointing: true
      # 类型: bool
      # 说明: 是否启用梯度检查点（节省显存）

    enable_activation_offload: false
      # 类型: bool
      # 说明: 是否启用激活值 offload（进一步节省显存）

    use_remove_padding: false
      # 类型: bool
      # 说明: 是否移除 padding tokens（提升效率）

    # ========== LoRA 配置 ==========
    lora_rank: 0
      # 类型: int
      # 说明: LoRA rank，0 表示不使用 LoRA
      # 建议: 8, 16, 32, 64

    lora_alpha: 16
      # 类型: int
      # 说明: LoRA scaling factor

    target_modules: all-linear
      # 类型: str | List[str]
      # 选项: 'all-linear' | ['q_proj', 'k_proj', 'v_proj', ...]
      # 说明: 应用 LoRA 的模块

    # ========== Kernel 优化 ==========
    use_liger: false
      # 类型: bool
      # 说明: 是否使用 Liger 融合 kernel

    use_fused_kernels: false
      # 类型: bool
      # 说明: 是否使用融合 kernel（FlashAttention, 融合 MLP）

    # ========== 安全性 ==========
    trust_remote_code: false
      # 类型: bool
      # 说明: 是否信任远程模型代码

  # ==================== Actor 配置 ====================
  actor:
    # ========== 并行策略 ==========
    strategy: fsdp
      # 类型: str
      # 选项: 'fsdp' | 'fsdp2' | 'megatron'
      # 说明: 分布式训练策略

    # ========== 优化器配置 ==========
    optim:
      lr: 1e-6
        # 类型: float
        # 说明: 学习率
        # 建议: 1e-6 ~ 1e-5 for full fine-tuning
        #       1e-5 ~ 1e-4 for LoRA

      weight_decay: 0.0
        # 类型: float
        # 说明: 权重衰减

      betas: [0.9, 0.999]
        # 类型: List[float]
        # 说明: Adam beta 参数

      eps: 1e-8
        # 类型: float
        # 说明: Adam epsilon

    # ========== PPO 训练配置 ==========
    ppo_epochs: 1
      # 类型: int
      # 说明: 每个 batch 的 PPO epoch 数

    ppo_mini_batch_size: 256
      # 类型: int
      # 说明: PPO mini-batch size

    ppo_micro_batch_size_per_gpu: 32
      # 类型: int
      # 说明: 每个 GPU 的 micro-batch size
      # 计算: ppo_mini_batch_size = n_gpus * ppo_micro_batch_size_per_gpu * gradient_accumulation_steps

    # ========== PPO 算法参数 ==========
    cliprange: 0.2
      # 类型: float
      # 说明: PPO clip 范围

    cliprange_low: null
      # 类型: float | null
      # 说明: Dual-clip 下限（null 表示使用 cliprange）

    cliprange_high: null
      # 类型: float | null
      # 说明: Dual-clip 上限

    clip_ratio_c: 3.0
      # 类型: float
      # 说明: Dual-clip 的下界 ratio

    entropy_coeff: 0.0
      # 类型: float
      # 说明: Entropy loss 系数

    # ========== KL Loss (替代 KL Reward) ==========
    use_kl_loss: True
      # 类型: bool
      # 说明: 是否在 actor loss 中添加 KL loss

    kl_loss_coef: 0.001
      # 类型: float
      # 说明: KL loss 系数

    kl_loss_type: low_var_kl
      # 类型: str
      # 选项: 'kl' | 'k1' | 'k2' | 'k3' | 'low_var_kl'
      # 说明: KL loss 类型

    # ========== Loss 聚合方式 ==========
    loss_agg_mode: token-mean
      # 类型: str
      # 选项: 'token-mean' | 'seq-mean-token-sum' | 'seq-mean-token-mean'
      # 说明: Loss 聚合方式

    # ========== FSDP 配置 ==========
    fsdp_config:
      param_offload: False
        # 类型: bool
        # 说明: 是否 offload 参数到 CPU

      optimizer_offload: False
        # 类型: bool
        # 说明: 是否 offload 优化器状态到 CPU

      grad_offload: False
        # 类型: bool
        # 说明: 是否 offload 梯度到 CPU

  # ==================== Rollout 配置 ====================
  rollout:
    # ========== 推理引擎 ==========
    name: sglang
      # 类型: str
      # 选项: 'vllm' | 'sglang'
      # 说明: 推理引擎

    mode: async
      # 类型: str
      # 选项: 'sync' | 'async'
      # 说明: 同步或异步推理模式

    # ========== 采样参数 ==========
    n: 16
      # 类型: int
      # 说明: 每个 prompt 生成的 response 数量
      # 建议: GRPO=16, GAE=1-4

    temperature: 0.7
      # 类型: float
      # 说明: 采样温度

    top_p: 0.95
      # 类型: float
      # 说明: Nucleus sampling 参数

    top_k: -1
      # 类型: int
      # 说明: Top-k sampling 参数（-1 表示不使用）

    # ========== 生成配置 ==========
    max_new_tokens: null
      # 类型: int | null
      # 说明: 最大生成 tokens（null 表示使用 data.max_response_length）

    do_sample: True
      # 类型: bool
      # 说明: 是否使用采样（False 表示贪心解码）

    # ========== 引擎配置 ==========
    tensor_model_parallel_size: 2
      # 类型: int
      # 说明: Tensor 并行大小

    gpu_memory_utilization: 0.5
      # 类型: float
      # 说明: GPU 显存利用率 (0.0 ~ 1.0)

    log_prob_micro_batch_size_per_gpu: 32
      # 类型: int
      # 说明: 计算 log_prob 时的 micro-batch size

    # ========== Multi-turn 配置 ==========
    multi_turn:
      enable: False
        # 类型: bool
        # 说明: 是否启用多轮对话模式

      max_turns: 5
        # 类型: int
        # 说明: 最大对话轮数

      format: qwen
        # 类型: str
        # 选项: 'qwen' | 'llama' | ...
        # 说明: 多轮格式

      tool_config_path: null
        # 类型: str | null
        # 说明: 工具配置文件路径

  # ==================== Reference Policy 配置 ====================
  ref:
    log_prob_micro_batch_size_per_gpu: 32
      # 类型: int
      # 说明: Reference policy 计算 log_prob 的 micro-batch size

    fsdp_config:
      param_offload: True
        # 类型: bool
        # 说明: Reference policy 通常 offload 参数节省显存
```

---

### 3.4 算法配置 (algorithm)

```yaml
algorithm:
  # ========== Advantage Estimator ==========
  adv_estimator: grpo
    # 类型: str
    # 选项: 'gae' | 'grpo' | 'grpo_passk' | 'reinforce_plus_plus' |
    #       'reinforce_plus_plus_baseline' | 'rloo' | 'opo' | 'remax'
    # 说明: Advantage 估计算法

  # ========== GAE 参数 ==========
  gamma: 1.0
    # 类型: float
    # 说明: Discount factor
    # 适用: GAE, REINFORCE++

  lam: 0.95
    # 类型: float
    # 说明: GAE lambda 参数
    # 适用: GAE

  # ========== GRPO 参数 ==========
  norm_adv_by_std_in_grpo: True
    # 类型: bool
    # 说明: 是否在 GRPO 中对 advantage 进行标准差归一化
    # 适用: GRPO, GRPO_PASSK

  # ========== KL Penalty (在 Reward 中) ==========
  use_kl_in_reward: False
    # 类型: bool
    # 说明: 是否在 reward 中添加 KL penalty
    # 注意: 与 actor.use_kl_loss 二选一

  kl_penalty: kl
    # 类型: str
    # 选项: 'kl' | 'k1' | 'k2' | 'k3' | 'low_var_kl' | 'mse' | 'abs'
    # 说明: KL penalty 类型

  kl_ctrl:
    type: fixed
      # 类型: str
      # 选项: 'fixed' | 'adaptive'
      # 说明: KL 系数控制方式

    kl_coef: 0.001
      # 类型: float
      # 说明: KL 系数（固定或初始值）

    target_kl: 0.01
      # 类型: float
      # 说明: 目标 KL 值（adaptive 模式）

    horizon: 10000
      # 类型: int
      # 说明: Adaptive 调整的时间跨度

  # ========== PF-PPO (可选) ==========
  use_pf_ppo: False
    # 类型: bool
    # 说明: 是否使用 PF-PPO（Preference-Free PPO）

  pf_ppo_reweight_method: pow
    # 类型: str
    # 选项: 'pow' | 'max_min' | 'max_random'
    # 说明: PF-PPO 重采样方法

  pf_ppo_weight_pow: 2.0
    # 类型: float
    # 说明: PF-PPO 权重指数
```

---

### 3.5 训练器配置 (trainer)

```yaml
trainer:
  # ========== 训练轮数 ==========
  total_epochs: 15
    # 类型: int
    # 说明: 总训练轮数

  total_training_steps: null
    # 类型: int | null
    # 说明: 总训练步数（null 表示使用 total_epochs）

  # ========== 检查点保存 ==========
  save_freq: 100
    # 类型: int
    # 说明: 每 N 步保存一次检查点（-1 表示不保存）

  max_actor_ckpt_to_keep: null
    # 类型: int | null
    # 说明: 最多保留 N 个 actor 检查点（null 表示保留所有）

  max_critic_ckpt_to_keep: null
    # 类型: int | null
    # 说明: 最多保留 N 个 critic 检查点

  default_local_dir: ./checkpoints
    # 类型: str
    # 说明: 本地检查点保存目录

  default_hdfs_dir: null
    # 类型: str | null
    # 说明: HDFS 检查点保存目录

  del_local_ckpt_after_load: False
    # 类型: bool
    # 说明: 加载检查点后是否删除本地文件

  # ========== 恢复训练 ==========
  resume_mode: auto
    # 类型: str
    # 选项: 'auto' | 'resume_path' | 'disable'
    # 说明: 恢复训练模式
    #   - auto: 自动从最新检查点恢复
    #   - resume_path: 从指定路径恢复
    #   - disable: 不恢复

  resume_from_path: null
    # 类型: str | null
    # 说明: 指定恢复的检查点路径（resume_mode=resume_path 时）

  # ========== 验证 ==========
  test_freq: 20
    # 类型: int
    # 说明: 每 N 步进行一次验证（-1 表示不验证）

  val_before_train: True
    # 类型: bool
    # 说明: 训练前是否进行验证

  val_only: False
    # 类型: bool
    # 说明: 是否只运行验证（不训练）

  # ========== 日志 ==========
  logger: ['console', 'wandb']
    # 类型: List[str]
    # 选项: 'console' | 'wandb' | 'tensorboard'
    # 说明: 日志后端

  project_name: 'your_project'
    # 类型: str
    # 说明: 项目名称（wandb/tensorboard）

  experiment_name: 'your_experiment'
    # 类型: str
    # 说明: 实验名称

  # ========== 数据输出 ==========
  rollout_data_dir: null
    # 类型: str | null
    # 说明: Rollout 数据保存目录（用于分析）

  val_data_dir: null
    # 类型: str | null
    # 说明: 验证数据保存目录

  # ========== 分布式配置 ==========
  n_gpus_per_node: 8
    # 类型: int
    # 说明: 每个节点的 GPU 数量

  nnodes: 1
    # 类型: int
    # 说明: 节点数量

  device: cuda
    # 类型: str
    # 选项: 'cuda' | 'npu'
    # 说明: 设备类型

  # ========== Critic Warmup ==========
  critic_warmup: 0
    # 类型: int
    # 说明: Critic warmup 步数（在此之前不更新 actor）

  # ========== 性能优化 ==========
  balance_batch: True
    # 类型: bool
    # 说明: 是否平衡 batch 中的序列长度分布

  ray_wait_register_center_timeout: null
    # 类型: int | null
    # 说明: Ray 注册中心等待超时（秒）
```

---

### 3.6 Critic 配置 (critic, 可选)

```yaml
critic:
  # ========== 并行策略 ==========
  strategy: fsdp
    # 类型: str
    # 选项: 'fsdp' | 'fsdp2' | 'megatron'
    # 说明: 必须与 actor.strategy 一致

  # ========== 优化器配置 ==========
  optim:
    lr: 1e-5
      # 类型: float
      # 说明: Critic 学习率（通常高于 actor）

  # ========== 训练配置 ==========
  ppo_epochs: 1
    # 类型: int
    # 说明: Critic 的 PPO epochs

  ppo_mini_batch_size: 256
    # 类型: int
    # 说明: Critic 的 mini-batch size

  ppo_micro_batch_size_per_gpu: 32
    # 类型: int
    # 说明: Critic 的 micro-batch size

  # ========== Value Loss 参数 ==========
  cliprange_value: 0.2
    # 类型: float
    # 说明: Value function clip 范围

  loss_agg_mode: token-mean
    # 类型: str
    # 说明: Value loss 聚合方式

  # ========== FSDP 配置 ==========
  fsdp_config:
    param_offload: False
    optimizer_offload: False
```

---

### 3.7 Reward Model 配置 (reward_model, 可选)

```yaml
reward_model:
  # ========== 基础配置 ==========
  enable: False
    # 类型: bool
    # 说明: 是否启用学习型 Reward Model

  # ========== 模型配置 ==========
  strategy: fsdp
    # 类型: str
    # 说明: 并行策略

  path: ~/models/reward_model
    # 类型: str
    # 说明: Reward Model 路径

  # ========== 推理配置 ==========
  micro_batch_size_per_gpu: 32
    # 类型: int
    # 说明: 推理时的 micro-batch size
```

---

## 4. Ray 初始化配置 (ray_init)

```yaml
ray_init:
  num_cpus: 64
    # 类型: int
    # 说明: Ray 使用的 CPU 核心数

  timeline_json_file: null
    # 类型: str | null
    # 说明: Ray timeline 输出文件（用于性能分析）
```

---

## 5. 配置示例

### 5.1 小规模实验（单机 8 卡）

```yaml
# config/small_scale_gsm8k.yaml
defaults:
  - ppo_trainer
  - _self_

data:
  train_batch_size: 128  # 8 GPUs * 16 responses = 实际 8 prompts
  max_prompt_length: 512
  max_response_length: 512

actor_rollout_ref:
  model:
    path: Qwen/Qwen2.5-3B-Instruct
    lora_rank: 32  # 使用 LoRA 节省显存
    enable_gradient_checkpointing: true

  actor:
    optim:
      lr: 1e-5
    ppo_mini_batch_size: 128
    ppo_micro_batch_size_per_gpu: 16
    fsdp_config:
      param_offload: False

  rollout:
    name: vllm
    n: 16
    tensor_model_parallel_size: 1
    gpu_memory_utilization: 0.4

algorithm:
  adv_estimator: grpo

trainer:
  n_gpus_per_node: 8
  nnodes: 1
  total_epochs: 10
  save_freq: 50
  test_freq: 10
```

### 5.2 大规模训练（多机）

```yaml
# config/large_scale_math.yaml
defaults:
  - ppo_trainer
  - _self_

data:
  train_batch_size: 1024
  max_prompt_length: 2048
  max_response_length: 2048

actor_rollout_ref:
  model:
    path: ~/models/Qwen/Qwen2.5-70B-Instruct
    lora_rank: 0  # Full fine-tuning
    enable_gradient_checkpointing: true
    enable_activation_offload: true

  actor:
    optim:
      lr: 1e-6
    ppo_mini_batch_size: 512
    ppo_micro_batch_size_per_gpu: 8
    fsdp_config:
      param_offload: True
      optimizer_offload: True

  rollout:
    name: sglang
    n: 32
    tensor_model_parallel_size: 8
    gpu_memory_utilization: 0.7

algorithm:
  adv_estimator: gae

critic:
  optim:
    lr: 1e-5

trainer:
  n_gpus_per_node: 8
  nnodes: 4  # 32 GPUs 总计
  total_epochs: 20
  save_freq: 100
```

### 5.3 代码生成任务

```yaml
# config/code_generation.yaml
defaults:
  - ppo_trainer
  - _self_

data:
  train_files: ~/data/apps/train.parquet
  max_response_length: 2048  # 代码通常较长

reward_manager:
  type: prime
  max_concurrency: 128
  sandbox_fusion:
    url: "http://localhost:8000/execute"
    max_concurrent: 64

actor_rollout_ref:
  rollout:
    n: 8  # Pass@8
    temperature: 0.8

algorithm:
  adv_estimator: grpo_passk  # Pass@k reward
```

---

## 6. 命令行覆盖

### 6.1 基础用法

```bash
python -m verl.trainer.main_ppo \
    --config-path="./config" \
    --config-name="your_task" \
    data.train_batch_size=512 \
    algorithm.adv_estimator=grpo \
    trainer.total_epochs=20
```

### 6.2 覆盖嵌套配置

```bash
# 覆盖优化器学习率
python -m verl.trainer.main_ppo \
    --config-name="your_task" \
    actor_rollout_ref.actor.optim.lr=1e-5

# 覆盖 FSDP 配置
python -m verl.trainer.main_ppo \
    --config-name="your_task" \
    actor_rollout_ref.actor.fsdp_config.param_offload=True
```

### 6.3 覆盖列表配置

```bash
# 覆盖多个训练文件
python -m verl.trainer.main_ppo \
    --config-name="your_task" \
    'data.train_files=[~/data/gsm8k/train.parquet,~/data/math/train.parquet]'

# 覆盖 logger
python -m verl.trainer.main_ppo \
    --config-name="your_task" \
    'trainer.logger=[console]'
```

---

## 7. 最佳实践

### 7.1 显存优化

```yaml
# 显存不足时的配置策略
actor_rollout_ref:
  model:
    enable_gradient_checkpointing: true  # 节省 ~50% 显存
    enable_activation_offload: true      # 进一步节省（降低速度）
    lora_rank: 32                        # 使用 LoRA
    use_remove_padding: true             # 移除 padding

  actor:
    ppo_micro_batch_size_per_gpu: 8     # 减小 micro-batch
    fsdp_config:
      param_offload: True                # Offload 到 CPU
      optimizer_offload: True

  rollout:
    tensor_model_parallel_size: 2        # 使用 TP
    gpu_memory_utilization: 0.4          # 降低显存利用率
```

### 7.2 训练速度优化

```yaml
# 加速训练的配置策略
actor_rollout_ref:
  model:
    use_remove_padding: true
    use_fused_kernels: true
    use_liger: true

  rollout:
    name: sglang  # SGLang 通常比 vLLM 快
    mode: async   # 异步推理

trainer:
  balance_batch: True  # 平衡序列长度
```

### 7.3 算法选择

```yaml
# GAE: 适合需要 value function 的场景
algorithm:
  adv_estimator: gae
  gamma: 0.99
  lam: 0.95

critic:
  enable: True

# GRPO: 适合 outcome-based reward（每个序列一个总分）
algorithm:
  adv_estimator: grpo

critic:
  enable: False  # GRPO 不需要 critic

# Pass@k: 适合代码生成等需要多样性的任务
algorithm:
  adv_estimator: grpo_passk

actor_rollout_ref:
  rollout:
    n: 16  # 生成多个候选
```

---

## 8. 常见问题

### Q1: 如何计算实际的 batch size?

```
实际 prompt 数 = train_batch_size / rollout.n
例如: train_batch_size=256, n=16 → 实际处理 16 个 prompts
```

### Q2: FSDP vs Megatron?

- **FSDP**: 易用，适合大多数场景
- **Megatron**: 性能更高，但需要更多配置

### Q3: 何时使用 KL loss vs KL reward?

- **KL loss** (`actor.use_kl_loss=True`): 更稳定，推荐
- **KL reward** (`algorithm.use_kl_in_reward=True`): 传统方法

两者不要同时使用。

### Q4: 如何调试配置?

```bash
# 1. 打印完整配置
python -m verl.trainer.main_ppo \
    --config-name="your_task" \
    --cfg job

# 2. 使用小数据集快速迭代
data.train_batch_size=16
trainer.total_epochs=1
trainer.save_freq=-1
```

---

## 9. 配置验证 Checklist

训练前检查:

- [ ] `data.train_files` 和 `data.val_files` 路径正确
- [ ] `data.max_prompt_length` 和 `data.max_response_length` 合理
- [ ] `data.train_batch_size` 能被 `n_gpus * rollout.n` 整除
- [ ] `actor_rollout_ref.model.path` 模型路径正确
- [ ] `reward_manager.type` 和 `data.reward_fn_key` 匹配
- [ ] `algorithm.adv_estimator` 与 `critic.enable` 一致
- [ ] `trainer.n_gpus_per_node * trainer.nnodes` 与集群匹配
- [ ] 显存配置合理（gradient checkpointing, offload, LoRA）

---

## 10. 参考配置

完整配置示例:
- 基础 PPO: `.reference_projects/ToolOrchestra/training/verl/trainer/config/ppo_trainer.yaml`
- GSM8K: `.reference_projects/ToolOrchestra/training/examples/sglang_multiturn/config/gsm8k_multiturn_grpo.yaml`
- 启动脚本: `.reference_projects/ToolOrchestra/training/examples/sglang_multiturn/run_qwen2.5-3b_gsm8k_multiturn.sh`
