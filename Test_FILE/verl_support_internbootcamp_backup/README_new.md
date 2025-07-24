# VERL Support for InternBootcamp

这是重写后的VERL数据生成和奖励计算系统，符合VERL接口要求。

## 主要文件

### 1. generate_verl_data.py
VERL数据生成器，结合了`verl_complete_generator.py`的workflow执行流程和prompt格式。

**主要功能：**
- 生成符合VERL格式的训练数据（HuggingFace chat格式）
- 支持workflow代码生成（使用LLM API）
- 输出parquet格式数据文件
- 自动分割训练集和测试集

**使用示例：**
```bash
python generate_verl_data.py --tasks sudoku_4x4_easy minesweeper_5x5 --entries-per-task 5 --output-dir verl_data
```

### 2. workflow_reward.py
工作流奖励计算模块，提供`compute_score`等VERL兼容接口。

**主要接口：**
- `compute_score(workflow_code, task_name, test_cases=None)` - 计算单个workflow的奖励
- `batch_compute_scores(workflow_codes, task_names, test_cases_list=None)` - 批量计算奖励
- `compute_verl_entry_reward(verl_entry)` - 计算VERL数据条目的奖励

**特点：**
- 支持真实MetaGPT执行（如果可用）
- 提供模拟执行模式（用于测试）
- 异步执行，支持并发处理

### 3. test_verl_complete.py
完整的测试脚本，测试整个系统的功能。

**测试内容：**
- 数据生成测试
- 奖励计算测试
- 数据格式验证
- 端到端集成测试

**使用示例：**
```bash
python test_verl_complete.py --clean --test-dir test_output
```

## 配置文件

系统使用`config.json`配置文件，包含以下主要配置：

```json
{
    "generation_config": {
        "examples_per_task": 3,
        "prompts_per_task": 2
    },
    "llm_config": {
        "generation": {
            "model": "deepseek-chat",
            "base_url": "https://api.deepseek.com",
            "api_key": "sk-xxx"
        },
        "downstream": {
            "model": "deepseek-chat",
            "base_url": "https://api.deepseek.com",
            "api_key": "sk-xxx"
        }
    },
    "reward_config": {
        "timeout": 180,
        "test_cases_per_task": 3
    }
}
```

## 数据格式

生成的VERL数据条目格式：

```json
{
    "data_source": "internbootcamp_sudoku_4x4_easy",
    "prompt": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "workflow code..."}
    ],
    "ability": "logical_reasoning",
    "reward_model": {
        "task_name": "sudoku_4x4_easy",
        "test_cases": ["case1", "case2", "case3"],
        "workflow_code": "..."
    },
    "extra_info": {
        "entry_id": 0,
        "task_type": "puzzle",
        "workflow_type": "predefined",
        "timestamp": "2024-01-01T00:00:00"
    }
}
```

## 环境要求

- Python 3.8+
- 必需包：pandas, pyarrow, openai
- 可选包：metagpt（用于真实workflow执行）

## 备份文件

原始文件已备份为：
- `generate_verl_data.py.backup`
- `workflow_reward.py.backup`
- `verl_complete_generator.py.backup`