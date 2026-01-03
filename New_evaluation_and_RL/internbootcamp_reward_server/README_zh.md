# InternBootcamp Reward 系统使用指南

## 📌 系统概述

InternBootcamp Reward 系统是一个用于生成和评估工作流的强化学习训练系统。它包含三个核心组件：

1. **API代理服务** - 为MetaGPT提供API请求代理和速率控制
2. **Reward计算服务** - 评估生成的工作流并计算奖励分数
3. **训练数据生成器** - 生成VERL格式的训练数据用于强化学习

## 🚀 快速开始

### 1. 启动API代理服务

API代理服务负责处理MetaGPT的API请求，提供速率限制和请求分发功能。

#### Windows系统：
```bash
cd New_evaluation_and_RL\servers_and_proxy
start_api_proxy.bat
```

#### Linux/Mac系统：
```bash
cd New_evaluation_and_RL/servers_and_proxy
bash start_api_proxy.sh
```

服务启动后会显示：
- 端口：默认5009（可在config.yaml中配置）
- 速率限制：默认3 req/s
- 运行模式：正常模式或调试模式

### 2. 启动Reward计算服务

Reward服务负责执行工作流并计算奖励分数。

#### Windows系统：
```bash
cd New_evaluation_and_RL\internbootcamp_reward_server
start_server.bat
```

#### Linux/Mac系统：
```bash
cd New_evaluation_and_RL/internbootcamp_reward_server
bash start_server.sh

# 后台运行模式
bash start_server.sh background
```

服务启动后会监听：
- 端口：默认8900
- 健康检查：http://localhost:8900/health

### 3. 生成训练数据

使用训练数据生成器创建VERL格式的数据集。

#### 基本用法：
```bash
cd New_evaluation_and_RL\generate_parquet_and_jsonl
python internbootcamp_generate_verl_training_data.py
```

#### 高级用法示例：

```bash
# 指定每个任务的条目数量
python internbootcamp_generate_verl_training_data.py --entries-per-task 10

# 指定处理的任务数量
python internbootcamp_generate_verl_training_data.py --max-tasks 5

# 自定义输出目录
python internbootcamp_generate_verl_training_data.py --output-dir custom_output

# 使用分析文件过滤任务
python internbootcamp_generate_verl_training_data.py --analysis-file analysis.jsonl

# 指定特定任务
python internbootcamp_generate_verl_training_data.py --tasks task1 task2 task3

# 自定义训练/测试分割比例
python internbootcamp_generate_verl_training_data.py --train-ratio 0.9

# 完整示例
python internbootcamp_generate_verl_training_data.py \
    --config ../config.yaml \
    --entries-per-task 20 \
    --max-tasks 10 \
    --output-dir production_data \
    --train-ratio 0.85 \
    --timeout-per-task 10.0
```

## 📁 系统架构

```
New_evaluation_and_RL/
├── config.yaml                           # 统一配置文件
├── servers_and_proxy/                    # API代理服务
│   ├── start_api_proxy.bat              # Windows启动脚本
│   └── start_api_proxy.sh               # Linux/Mac启动脚本
├── internbootcamp_reward_server/         # Reward计算服务
│   ├── internbootcamp_reward_utils.py   # 核心计算逻辑
│   ├── internbootcamp_reward_server.py  # REST API服务
│   ├── start_server.bat                 # Windows启动脚本
│   └── start_server.sh                  # Linux/Mac启动脚本
├── generate_parquet_and_jsonl/          # 数据生成器
│   └── internbootcamp_generate_verl_training_data.py
├── workspace/                            # 工作流执行日志
├── logs/                                 # 系统日志
└── parquet_and_jsonl_data/             # 生成的训练数据
    └── internbootcamp/
        ├── train.parquet                 # 训练集（Parquet格式）
        ├── train.jsonl                   # 训练集（JSONL格式）
        ├── test.parquet                  # 测试集（Parquet格式）
        ├── test.jsonl                    # 测试集（JSONL格式）
        └── generation_stats.json         # 生成统计信息
```

## ⚙️ 配置说明

所有服务共享统一的配置文件 `config.yaml`：

```yaml
# 项目根目录
project_root: "D:/temp/Flow_RL"

# 服务配置
services:
  # MetaGPT API代理配置
  metagpt_api_proxy:
    enabled: true
    host: "localhost"
    port: 5009
    target_url: "https://idealab.alibaba-inc.com/api/openai/v1"
    target_api_key: "your_api_key"
    rate_per_second: 3      # 速率限制
    max_concurrency: 20     # 最大并发数
    debug: false           # 调试模式
    
  # InternBootcamp Reward服务配置
  internbootcamp_reward:
    enabled: true
    host: "0.0.0.0"
    port: 8900
    timeout: 300           # 超时时间（秒）
    debug: false
    workspace: "New_evaluation_and_RL/workspace/internbootcamp"
    max_concurrent: 5      # 并发任务数

# 数据生成配置
data_generation:
  output_dir: "New_evaluation_and_RL/parquet_and_jsonl_data"
  default_test_cases_per_entry: 5
  default_train_proportion: 0.8
```

## 🔌 API接口说明

### Reward计算服务API

#### 1. 健康检查
```
GET /health
```

#### 2. 计算单个工作流分数
```
POST /compute_score
Content-Type: application/json

{
    "solution_str": "<workflow code>",
    "ground_truth": "default",
    "extra_info": {
        "task_name": "task_id",
        "test_cases": [0, 1, 2]
    }
}
```

响应：
```json
{
    "success": true,
    "score": 0.85,
    "message": "Score computed successfully"
}
```

#### 3. 批量计算分数
```
POST /batch_compute
Content-Type: application/json

{
    "tasks": [
        {
            "task_id": "task_1",
            "solution_str": "<workflow code>",
            "ground_truth": "default",
            "extra_info": {...}
        }
    ]
}
```

#### 4. 获取配置信息
```
GET /config
```

## 📊 数据格式说明

### VERL训练数据格式

生成的数据包含以下字段：

```json
{
    "data_source": "internbootcamp",
    "prompt": [
        {"role": "system", "content": "系统提示"},
        {"role": "user", "content": "用户提示"}
    ],
    "ability": "任务能力分类",
    "reward_model": {
        "ground_truth": "default"
    },
    "extra_info": {
        "score": 1.0,
        "task_name": "任务名称",
        "test_cases": ["测试用例列表"],
        "entry_id": 0,
        "task_type": "任务类型",
        "num_examples": 5,
        "timestamp": "2024-01-01T00:00:00",
        "generation_time": 1.23
    }
}
```

## 🐛 故障排查

### 常见问题

1. **端口被占用**
   - Windows：脚本会自动终止占用端口的进程
   - Linux/Mac：使用 `lsof -i :端口号` 查找并终止进程

2. **配置文件找不到**
   - 确保在正确的目录下运行脚本
   - 检查 `config.yaml` 是否存在于 `New_evaluation_and_RL/` 目录

3. **API请求失败**
   - 检查API代理服务是否正常运行
   - 验证API密钥是否正确
   - 查看日志文件获取详细错误信息

4. **数据生成超时**
   - 使用 `--timeout-per-task` 参数调整超时时间
   - 减少 `--entries-per-task` 数量
   - 检查网络连接是否稳定

### 日志位置

- API代理日志：`New_evaluation_and_RL/logs/api_proxy_*.log`
- Reward服务日志：控制台输出或 `server.log`（后台模式）
- 工作流执行日志：`New_evaluation_and_RL/workspace/internbootcamp/`
- 数据生成统计：`parquet_and_jsonl_data/internbootcamp/generation_stats.json`

## 📝 注意事项

1. **环境要求**
   - Python 3.8+
   - 已安装MetaGPT和相关依赖
   - 配置正确的conda环境（workflow）

2. **服务启动顺序**
   - 先启动API代理服务
   - 再启动Reward计算服务
   - 最后运行数据生成器

3. **资源限制**
   - 合理设置并发数和速率限制
   - 监控内存和CPU使用情况
   - 定期清理日志和临时文件

4. **安全考虑**
   - 不要在配置文件中硬编码敏感信息
   - 使用环境变量管理API密钥
   - 限制服务的网络访问范围

## 🔧 高级配置

### 自定义任务过滤

使用分析文件过滤高质量任务：

1. 创建分析文件（JSONL格式）
2. 包含任务质量评估信息
3. 使用 `--analysis-file` 参数指定文件

### 批量处理优化

对于大规模数据生成：

1. 增加 `max_concurrent` 配置
2. 调整 `rate_per_second` 限制
3. 使用多个服务实例并行处理

### 调试模式

启用调试模式获取详细信息：

1. 在 `config.yaml` 中设置 `debug: true`
2. 查看详细的请求和响应日志
3. 分析性能瓶颈和错误原因

## 📚 相关文档

- [VERL框架文档](https://github.com/verl-ai/verl)
- [MetaGPT使用指南](https://github.com/geekan/MetaGPT)
- [InternBootcamp任务说明](../InternBootcamp/README.md)

## 🤝 支持与反馈

如遇到问题或有改进建议，请：

1. 查看日志文件获取详细错误信息
2. 检查配置文件是否正确
3. 确认所有依赖服务正常运行
4. 联系系统管理员获取帮助

---

*最后更新：2024年*