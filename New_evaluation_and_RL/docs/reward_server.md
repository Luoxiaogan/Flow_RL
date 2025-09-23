# ScoreFlow Reward服务使用指南

## 概述

ScoreFlow Reward服务是一个基于REST API的workflow评分系统，用于评估生成的workflow代码在各种benchmark上的性能表现。服务提供了简洁的HTTP接口，外部系统可以轻松地集成workflow评分功能。

## 服务配置

### 启动服务

```bash
cd /Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/services
bash start_scoreflow_reward.sh
```

### 默认配置

- **服务地址**: `http://0.0.0.0:8899`
- **配置文件**: `config.yaml` 中的 `services.scoreflow_reward` 部分
- **支持的benchmark**: gsm8k, mbpp, humaneval, hotpotqa, drop, high_level_math

## API接口详解

### 1. 健康检查 `/health`

检查服务运行状态。

**请求方法**: `GET`  
**请求URL**: `http://localhost:8899/health`

**响应示例**:
```json
{
    "status": "healthy",
    "service": "scoreflow_reward_server",
    "version": "1.0.0"
}
```

**使用示例**:
```bash
curl http://localhost:8899/health
```

---

### 2. 单次评分 `/compute_score`

评估单个workflow的性能得分。

**请求方法**: `POST`  
**请求URL**: `http://localhost:8899/compute_score`

**请求参数**:
- `data_source` (必需): benchmark名称，如 "gsm8k", "mbpp"
- `solution_str` (必需): 要评估的workflow Python代码
- `ground_truth` (必需): 通常使用 "default"
- `extra_info` (必需): 包含测试用例和数据路径的额外信息

**请求格式**:
```json
{
    "data_source": "gsm8k",
    "solution_str": "class Workflow:\n    def __init__(self, config, problem):\n        self.config = config\n        self.problem = problem\n    \n    async def run(self):\n        # workflow实现代码\n        return result",
    "ground_truth": "default",
    "extra_info": {
        "test_cases": [0, 1, 2],
        "data_path": "path/to/data.jsonl"
    }
}
```

**响应格式**:
```json
{
    "success": true,
    "score": 0.85,
    "message": "Score computed successfully"
}
```

**使用示例**:
```bash
curl -X POST http://localhost:8899/compute_score \
  -H "Content-Type: application/json" \
  -d '{
    "data_source": "gsm8k",
    "solution_str": "class Workflow:\n    def __init__(self, config, problem):\n        self.config = config\n        self.problem = problem\n    \n    async def run(self):\n        return \"42\"",
    "ground_truth": "default",
    "extra_info": {
      "test_cases": [0, 1, 2]
    }
  }'
```

---

### 3. 批量评分 `/batch_compute`

同时评估多个workflow的性能。

**请求方法**: `POST`  
**请求URL**: `http://localhost:8899/batch_compute`

**请求格式**:
```json
{
    "tasks": [
        {
            "task_id": "workflow_1",
            "data_source": "gsm8k",
            "solution_str": "<workflow代码1>",
            "ground_truth": "default",
            "extra_info": {
                "test_cases": [0, 1, 2]
            }
        },
        {
            "task_id": "workflow_2",
            "data_source": "mbpp",
            "solution_str": "<workflow代码2>",
            "ground_truth": "default",
            "extra_info": {
                "test_cases": [0, 1, 2]
            }
        }
    ]
}
```

**响应格式**:
```json
{
    "success": true,
    "results": [
        {
            "task_id": "workflow_1",
            "score": 0.85,
            "success": true
        },
        {
            "task_id": "workflow_2",
            "score": 0.92,
            "success": true
        }
    ]
}
```

**使用示例**:
```bash
curl -X POST http://localhost:8899/batch_compute \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {
        "task_id": "test_1",
        "data_source": "gsm8k",
        "solution_str": "class Workflow:\n    def run(self):\n        return 42",
        "ground_truth": "default",
        "extra_info": {"test_cases": [0, 1]}
      }
    ]
  }'
```

---

### 4. 配置查询 `/config`

获取服务配置信息和支持的benchmark列表。

**请求方法**: `GET`  
**请求URL**: `http://localhost:8899/config`

**响应格式**:
```json
{
    "server_config": {
        "host": "0.0.0.0",
        "port": 8899,
        "debug": false,
        "timeout": 300
    },
    "llm_config": {
        "provider": "openai",
        "model": "qwen-turbo",
        "api_key": "***",
        "base_url": "http://localhost:5009"
    },
    "reward_config": {
        "timeout": 300,
        "test_cases_per_task": 3,
        "max_concurrent": 5
    },
    "benchmarks": ["gsm8k", "mbpp", "humaneval", "hotpotqa", "drop", "high_level_math"]
}
```

**使用示例**:
```bash
curl http://localhost:8899/config
```

## 错误处理

### 常见错误码

- **400 Bad Request**: 请求参数错误或缺少必需字段
- **500 Internal Server Error**: 服务内部错误（如workflow执行失败）

### 错误响应格式

```json
{
    "success": false,
    "error": "错误描述",
    "traceback": "详细错误堆栈（仅在debug模式下显示）"
}
```

### 常见错误示例

1. **缺少必需字段**:
```json
{
    "success": false,
    "error": "Missing required field: data_source"
}
```

2. **workflow执行失败**:
```json
{
    "success": false,
    "error": "MetaGPT workflow execution failed: 1 validation error for Config",
    "traceback": "..."
}
```

## 使用最佳实践

### 1. 健康检查
在发送评分请求前，建议先检查服务状态：
```bash
curl http://localhost:8899/health
```

### 2. Workflow代码格式
确保workflow代码格式正确：
```python
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
    
    async def run(self):
        # 实现您的workflow逻辑
        return result
```

### 3. 测试用例配置
在`extra_info`中正确配置测试用例：
```json
{
    "extra_info": {
        "test_cases": [0, 1, 2],  // 要测试的样本索引
        "data_path": "path/to/test/data.jsonl"  // 可选：自定义数据路径
    }
}
```

### 4. 批量处理
对于大量workflow评估，使用批量接口可以提高效率：
- 建议每批处理10-50个workflow
- 为每个任务设置唯一的`task_id`
- 检查响应中每个任务的`success`状态

## 集成示例

### Python客户端示例

```python
import requests
import json

class ScoreFlowClient:
    def __init__(self, base_url="http://localhost:8899"):
        self.base_url = base_url
    
    def health_check(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def compute_score(self, data_source, workflow_code, test_cases=None):
        payload = {
            "data_source": data_source,
            "solution_str": workflow_code,
            "ground_truth": "default",
            "extra_info": {
                "test_cases": test_cases or [0, 1, 2]
            }
        }
        
        response = requests.post(
            f"{self.base_url}/compute_score",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        return response.json()

# 使用示例
client = ScoreFlowClient()

# 健康检查
print(client.health_check())

# 评分workflow
workflow_code = '''
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
    
    async def run(self):
        return "42"
'''

result = client.compute_score("gsm8k", workflow_code)
print(f"评分结果: {result}")
```

## 故障排查

### 1. 服务无法启动
- 检查端口8899是否被占用：`lsof -i:8899`
- 检查config.yaml配置是否正确
- 查看启动日志中的错误信息

### 2. API请求失败
- 确认服务正在运行：`curl http://localhost:8899/health`
- 检查请求JSON格式是否正确
- 查看服务日志了解详细错误信息

### 3. 评分结果异常
- 检查workflow代码语法是否正确
- 确认benchmark名称是否支持
- 查看服务配置中的benchmark映射是否正确

## 服务监控

### 查看服务状态
```bash
# 检查进程是否运行
ps aux | grep scoreflow_reward_server

# 检查端口监听
lsof -i:8899

# 查看服务日志
tail -f /Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/logs/scoreflow_reward_*.log
```

### 停止服务
```bash
# 找到进程ID并终止
kill $(lsof -t -i:8899)
```

---

## 相关文档

- [系统架构说明](./architecture.md)
- [Benchmark配置指南](./benchmark_config.md)
- [API集成示例](./api_examples.md)