# ScoreFlow Reward 远程执行解决方案

## 问题描述
`scoreflow_reward.py` 脚本依赖于 MetaGPT 框架，但调用环境无法安装 MetaGPT。需要将 MetaGPT 相关的工作外包给可以安装 MetaGPT 的环境。

## 解决方案架构
采用客户端-服务器架构，将计算工作分离：

```
┌─────────────────────┐         HTTP/REST API        ┌─────────────────────┐
│                     │ ──────────────────────────► │                     │
│   客户端环境         │                              │   服务器环境         │
│  (无 MetaGPT)       │ ◄────────────────────────── │  (有 MetaGPT)       │
│                     │         JSON Response        │                     │
└─────────────────────┘                              └─────────────────────┘
```

## 组件说明

### 1. 服务器端 (`scoreflow_reward_server.py`)
- **功能**: 封装原始的 `scoreflow_reward.py`，提供 REST API 接口
- **运行环境**: 需要安装 MetaGPT 和所有依赖
- **主要端点**:
  - `/health` - 健康检查
  - `/compute_score` - 计算单个 workflow 的分数
  - `/batch_compute` - 批量计算多个 workflows
  - `/config` - 获取服务器配置

### 2. 客户端 (`scoreflow_reward_client.py`)
- **功能**: 提供与原始 `scoreflow_reward.py` 相同的接口
- **运行环境**: 无需 MetaGPT，只需要 `requests` 库
- **特点**: 
  - 完全兼容原始 API
  - 支持批量处理
  - 自动重试和错误处理

### 3. 配置文件 (`server_config.json`)
- 服务器配置
- LLM 配置
- 数据路径配置
- 日志和安全设置

### 4. 测试脚本 (`test_remote_setup.py`)
- 验证环境设置
- 测试服务器启动
- 测试客户端连接
- 功能测试

## 使用步骤

### 步骤 1: 在有 MetaGPT 的环境中启动服务器

```bash
# 激活包含 MetaGPT 的 conda 环境
conda activate workflow

# 进入 verl_support 目录
cd Test_FILE/verl_support/

# 启动服务器（使用默认配置）
python scoreflow_reward_server.py

# 或使用自定义配置
python scoreflow_reward_server.py --config server_config.json --port 8899
```

### 步骤 2: 在无 MetaGPT 的环境中使用客户端

```python
# 方式 1: 直接替换导入
from scoreflow_reward_client import compute_score

# 使用方式与原始版本完全相同
score = compute_score(
    data_source="gsm8k",
    solution_str=workflow_code,
    ground_truth="default",
    extra_info={
        "test_cases": [0, 1, 2],
        "data_path": "path/to/data.jsonl"
    }
)
```

```python
# 方式 2: 使用客户端类（更多控制）
from scoreflow_reward_client import ScoreFlowRewardClient

client = ScoreFlowRewardClient("http://server_address:8899")
score = client.compute_score(data_source, solution_str, ground_truth, extra_info)
```

### 步骤 3: 配置环境变量（可选）

```bash
# 设置服务器地址环境变量
export SCOREFLOW_SERVER_URL=http://192.168.1.100:8899

# 然后在 Python 中直接使用
from scoreflow_reward_client import compute_score
# 会自动使用环境变量中的服务器地址
```

## 高级功能

### 批量处理
```python
from scoreflow_reward_client import ScoreFlowRewardClient

client = ScoreFlowRewardClient("http://server:8899")

tasks = [
    {
        "task_id": "task_1",
        "data_source": "gsm8k",
        "solution_str": workflow_1,
        "ground_truth": "default",
        "extra_info": {...}
    },
    {
        "task_id": "task_2",
        "data_source": "mbpp",
        "solution_str": workflow_2,
        "ground_truth": "default",
        "extra_info": {...}
    }
]

results = client.batch_compute(tasks)
for result in results:
    print(f"{result['task_id']}: {result['score']}")
```

### 服务器监控
```python
from scoreflow_reward_client import ScoreFlowRewardClient

client = ScoreFlowRewardClient("http://server:8899")
config = client.get_server_config()
print(f"支持的 benchmarks: {config['benchmarks']}")
print(f"LLM 配置: {config['llm_config']}")
```

## 性能优化

1. **并发处理**: 服务器支持多个并发请求
2. **批量 API**: 减少网络开销
3. **连接池**: 客户端使用 session 复用连接
4. **超时控制**: 可配置的超时设置

## 错误处理

客户端会自动处理以下情况：
- 网络连接失败
- 服务器超时
- JSON 解析错误
- 服务器内部错误

所有错误情况下都会返回分数 0.0，并记录详细日志。

## 安全建议

1. **网络安全**:
   - 使用防火墙限制访问
   - 考虑使用 HTTPS（需要配置证书）
   - 可以启用 API 密钥认证

2. **资源限制**:
   - 配置最大并发数
   - 设置请求超时
   - 限制请求大小

3. **日志记录**:
   - 记录所有请求
   - 监控异常情况
   - 定期清理日志文件

## 故障排除

### 问题 1: 服务器无法启动
```bash
# 检查 MetaGPT 是否安装
python -c "import metagpt; print('MetaGPT installed')"

# 检查端口是否被占用
netstat -an | grep 8899
```

### 问题 2: 客户端连接失败
```bash
# 测试网络连接
ping server_address
curl http://server_address:8899/health

# 检查防火墙设置
```

### 问题 3: 计算超时
```python
# 增加超时时间
client = ScoreFlowRewardClient("http://server:8899", timeout=600)
```

## 测试

运行测试脚本验证设置：
```bash
python test_remote_setup.py
```

测试脚本会：
1. 检查本地环境
2. 尝试启动服务器（如果有 MetaGPT）
3. 测试客户端连接
4. 验证计算功能
5. 提供部署建议

## 总结

这个解决方案实现了：
- ✅ 完全兼容原始 API
- ✅ 无需在客户端安装 MetaGPT
- ✅ 支持批量处理
- ✅ 错误处理和日志记录
- ✅ 可扩展和可配置

通过这种架构，可以在任何环境中使用 ScoreFlow Reward 功能，只需要确保有一个可访问的服务器运行在有 MetaGPT 的环境中即可。