# VERL RL训练系统使用指南

## 🎯 概述

本系统将VERL强化学习框架与ScoreFlow奖励计算服务集成，实现了基于配置文件的统一管理。所有配置集中在 `New_evaluation_and_RL/config.yaml` 中，便于在不同环境间切换。

## 📁 文件结构

```
RL_part/
├── scoreflow_reward_client.py  # 统一客户端（VERL接口 + 独立CLI）
├── start_rl_training.sh        # 智能启动脚本
└── README_RL_Training.md        # 本文档
```

## 🚀 快速开始

### 1. 启动ScoreFlow奖励服务器

```bash
cd ../servers_and_proxy
bash start_scoreflow_reward.sh
```

### 2. 准备训练数据

确保已生成parquet格式的训练数据：
```bash
cd ../generate_parquet_and_jsonl
python generate_verl_training_data.py --benchmarks all
```

### 3. 启动RL训练

```bash
cd RL_part
bash start_rl_training.sh
```

## 📋 配置说明

所有配置位于 `New_evaluation_and_RL/config.yaml`：

### 关键配置项

```yaml
# 项目根目录（切换环境只需修改这里）
project_root: "/nas/ganluo/Flow_RL"  # 服务器
# project_root: "/Users/luogan/Code/workflow_generation/Flow_RL"  # 本地

# ScoreFlow服务配置（RL训练会使用相同的服务端点）
services:
  scoreflow_reward:
    host: "0.0.0.0"
    port: 8899

# RL训练配置
rl_training:
  data:
    train_files: "..."  # 训练数据路径
  model:
    base_model_path: "..."  # 基础模型路径
  # ... 更多配置
```

## 🔧 组件说明

### 1. scoreflow_reward_client.py
- **作用**：统一的ScoreFlow客户端，支持多种使用场景
- **功能**：
  - VERL框架集成：提供`compute_score`函数供VERL调用
  - 独立CLI工具：支持命令行测试和调用
  - Python库：可被其他Python代码导入使用
- **配置**：自动从config.yaml读取服务器地址，支持环境变量覆盖

### 2. start_rl_training.sh
- **作用**：智能启动脚本
- **功能**：
  - 从config.yaml读取所有训练参数
  - 检查必要的服务是否运行
  - 动态构建训练命令
  - 设置环境变量

## 🔍 测试功能

### 测试ScoreFlow连接和计算
```bash
# 基本测试（使用config.yaml中的配置）
python scoreflow_reward_client.py --test

# 指定服务器地址测试
python scoreflow_reward_client.py --test --server http://localhost:8899

# 计算特定workflow的分数
python scoreflow_reward_client.py --benchmark gsm8k --solution "<workflow code>"
```

## 📝 环境切换

切换本地和服务器环境只需修改 `config.yaml` 中的 `project_root`：

**本地环境：**
```yaml
project_root: "/Users/luogan/Code/workflow_generation/Flow_RL"
```

**服务器环境：**
```yaml
project_root: "/nas/ganluo/Flow_RL"
```

## 🛠️ 故障排除

### ScoreFlow服务器连接失败
1. 检查服务器是否运行：`lsof -i :8899`
2. 检查config.yaml中的host和port配置
3. 如果host是0.0.0.0，客户端会自动转换为localhost
4. 使用测试命令验证连接：`python scoreflow_reward_client.py --test`

### 训练数据找不到
1. 检查config.yaml中的data路径配置
2. 确保路径相对于project_root正确
3. 运行数据生成脚本生成训练数据

### VERL主脚本找不到
1. 确保VERL框架已正确安装
2. 检查verl目录结构是否完整
3. 手动指定main_ppo.py的路径

## 📊 监控训练

训练日志会输出到控制台，可以通过以下方式监控：
- 查看实时输出
- 检查checkpoint目录中的保存的模型
- 使用tensorboard查看训练曲线（如果配置了）

## 🔄 修改训练参数

所有训练参数都在 `config.yaml` 的 `rl_training` 部分：
- `data`: 数据相关配置
- `model`: 模型配置
- `actor`: Actor网络配置
- `rollout`: 推理配置
- `trainer`: 训练器配置
- `algorithm`: 算法配置
- `reward`: 奖励函数配置

修改后重新运行 `start_rl_training.sh` 即可应用新配置。