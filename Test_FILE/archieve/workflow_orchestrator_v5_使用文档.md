# Workflow Orchestrator V5 使用文档

## 概述

Workflow Orchestrator V5 是一个单文件的AI工作流编排器，支持通过命令行参数配置所有选项。您可以通过一个shell脚本硬编码配置并直接运行。

## 文件结构

```
Test_FILE/
├── workflow_orchestrator_v5.py          # 主程序文件（唯一必需）
├── run_workflow_argparse.sh             # 执行脚本（推荐使用）
└── workflow_orchestrator_v5_使用文档.md  # 本文档
```

## 快速开始

### 1. 设置环境变量

```bash
# 设置API密钥（至少一个）
export DASHSCOPE_API_KEY="your-dashscope-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

### 2. 使用预配置脚本运行

```bash
# 直接运行（最简单的方式）
bash run_workflow_argparse.sh
```

### 3. 自定义运行

```bash
python3 workflow_orchestrator_v5.py \
    --api-pool '[{"provider":"openai","model":"gpt-4o-mini","api_key":"your-key","base_url":"https://api.openai.com/v1"}]' \
    --exec-llm '{"provider":"openai","model":"gpt-4o-mini","api_key":"your-key","base_url":"https://api.openai.com/v1"}' \
    --generation-tasks "GSM8K:0,5,10-11" \
    --log-level INFO
```

## 参数详解

### 必需参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `--api-pool` | JSON字符串 | API配置池，支持多个API并行 | 见下方示例 |
| `--exec-llm` | JSON字符串 | 执行LLM配置 | 见下方示例 |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--generation-tasks` | 字符串 | `GSM8K:0,5,10-11` | 任务配置 |
| `--workspace-path` | 路径 | `./workspace_v5` | 工作空间路径 |
| `--dataset-base-path` | 路径 | `./ScoreFlow/benchmark/datasets` | 数据集基础路径 |
| `--gsm8k-dataset-path` | 路径 | 自动推导 | GSM8K数据集路径 |
| `--log-level` | 枚举 | `INFO` | 日志级别：DEBUG/INFO/WARNING/ERROR |
| `--max-concurrent-tasks` | 整数 | `10` | 最大并发任务数 |
| `--workflow-timeout` | 整数 | `120` | 工作流超时时间（秒） |

## 配置示例

### API池配置

```json
[
    {
        "provider": "dashscope",
        "model": "qwen-max-latest",
        "api_key": "your-dashscope-key",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    },
    {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "api_key": "your-openai-key",
        "base_url": "https://api.openai.com/v1"
    }
]
```

### 执行LLM配置

```json
{
    "provider": "openai",
    "model": "gpt-4o-mini",
    "api_key": "your-openai-key",
    "base_url": "https://api.openai.com/v1"
}
```

### 任务配置格式

```
# 格式：BENCHMARK1:task1,task2,range1-range2;BENCHMARK2:task1,task2
GSM8K:0,5,10-11          # GSM8K基准：任务0，任务5，任务10到11
GSM8K:0,5;MATH:1,2-4     # 多个基准
```

## 自定义配置

### 修改run_workflow_argparse.sh

编辑脚本中的配置区域：

```bash
# === 配置区域 - 在这里修改你的参数 ===

# 修改API池
API_POOL='[
    {
        "provider": "your_provider",
        "model": "your_model",
        "api_key": "'$YOUR_API_KEY'",
        "base_url": "your_base_url"
    }
]'

# 修改任务
GENERATION_TASKS="GSM8K:0-5;MATH:1,3,5-7"

# 修改并发数
MAX_CONCURRENT_TASKS=5
```

## 输出说明

### 工作空间结构

```
workspace_v5/
└── generated_workflows/
    ├── GSM8K/
    │   ├── gsm8k_0.py
    │   ├── gsm8k_1.py
    │   └── ...
    └── MATH/
        ├── math_0.py
        └── ...
```

### 日志信息

程序会输出：
- 当前配置信息
- API调用状态
- 工作流生成进度
- 执行和验证结果
- 总耗时统计

## 故障排除

### 常见错误

1. **API密钥未设置**
   ```
   错误: 没有设置任何API密钥环境变量
   ```
   解决：设置环境变量 `DASHSCOPE_API_KEY` 或 `OPENAI_API_KEY`

2. **JSON格式错误**
   ```
   API池配置解析失败: Expecting ',' delimiter
   ```
   解决：检查JSON格式，确保引号正确

3. **模块导入失败**
   ```
   无法导入 metagpt 模块
   ```
   解决：确保在正确目录运行，ScoreFlow路径正确

### 调试技巧

1. 使用DEBUG日志级别：
   ```bash
   --log-level DEBUG
   ```

2. 减少并发数测试：
   ```bash
   --max-concurrent-tasks 1
   ```

3. 测试单个任务：
   ```bash
   --generation-tasks "GSM8K:0"
   ```

## 扩展支持

### 添加新的基准测试

1. 在 `ScoreFlow/scripts/` 下创建新目录
2. 实现必需的模块文件
3. 在 `ScoreFlow/benchmark/` 下添加基准类
4. 更新任务配置

### 添加新的API提供商

修改API池配置，添加新的provider配置即可，只要兼容OpenAI格式。

## 性能优化

- **并发调优**：根据API限制调整 `max-concurrent-tasks`
- **超时设置**：复杂工作流可增加 `workflow-timeout`
- **API轮询**：多个API可提高并发处理能力

## 版本历史

- **V5**: 单文件架构，argparse参数化
- **V4**: 外部配置模块
- **V3**: 基础工作流编排
- **V2**: 初始版本
