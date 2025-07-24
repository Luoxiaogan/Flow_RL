# InternBootcamp VERL训练支持系统

这是一个专为InternBootcamp设计的VERL格式训练数据生成系统，支持1000+种动态生成的任务类型。

## 🎯 系统特点

- **动态任务生成**：使用`case_generator()`实时生成任务，无需固定数据集
- **任务多样性**：支持逻辑谜题、数学、算法、游戏等1000+种任务
- **灵活配置**：支持选择单个、多个或全部任务进行处理
- **HF Chat格式**：生成符合HuggingFace标准的对话格式数据
- **完善的错误处理**：自动跳过损坏的bootcamp任务

## 📁 文件结构

```
verl_support_internbootcamp/
├── README.md                        # 本文档
├── plan.md                          # 详细实施计划
├── config.json                      # 系统配置
├── internbootcamp_utils.py          # InternBootcamp工具函数
├── generate_verl_data.py            # VERL数据生成主程序
├── workflow_reward.py               # 工作流奖励计算
├── test_system.py                   # 系统测试脚本
└── data/                           # 生成的数据
    ├── internbootcamp_verl_train.parquet
    └── internbootcamp_verl_test.parquet
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install pandas pyarrow openai asyncio

# 确保InternBootcamp在Python路径中
export PYTHONPATH=$PYTHONPATH:/path/to/InternBootcamp
```

### 2. 配置设置

编辑`config.json`配置LLM和生成参数：

```json
{
    "llm_config": {
        "upstream": {
            "model": "qwen-turbo",
            "api_key": "your-api-key"
        }
    },
    "generation_config": {
        "examples_per_task": 2,      # 每个prompt包含的示例数
        "prompts_per_task": 5,        # 每个任务生成的prompt数
        "task_selection": {
            "mode": "manual",         # manual/random/auto
            "manual_tasks": ["game24", "sudoku"]
        }
    }
}
```

### 3. 生成VERL数据

#### 处理特定任务
```bash
python generate_verl_data.py --tasks game24 sudoku minesweeper
```

#### 处理所有任务
```bash
python generate_verl_data.py --all
```

#### 使用配置文件中的任务
```bash
python generate_verl_data.py
```

#### 其他选项
```bash
# 设置每个任务的prompt数量
python generate_verl_data.py --prompts-per-task 10

# 设置每个prompt的示例数量
python generate_verl_data.py --examples-per-prompt 3

# 测试运行（不保存数据）
python generate_verl_data.py --dry-run --tasks game24
```

## 📊 VERL数据格式

生成的数据使用HuggingFace chat格式：

```json
{
    "data_source": "internbootcamp_sudoku",
    "prompt": [
        {
            "role": "system",
            "content": "You are an expert at designing problem-solving workflows..."
        },
        {
            "role": "user", 
            "content": "Task Type: sudoku\n\nTask Description:...\n\nExample Problems:..."
        }
    ],
    "ability": "logic_reasoning",
    "reward_model": {
        "task_name": "sudoku",
        "test_cases": [
            {"puzzle": [[...]], "size": 9},
            {"puzzle": [[...]], "size": 9}
        ]
    },
    "extra_info": {
        "task_type": "logic_puzzle",
        "num_examples": 2,
        "timestamp": "2024-01-20T10:30:00"
    }
}
```

## 🎁 奖励计算使用

### 简单接口

```python
from workflow_reward import compute_score
import asyncio

# 工作流代码
workflow_code = '''
class InternBootcampWorkflow:
    def __init__(self):
        self.system_prompt = "You are an expert problem solver..."
    
    async def solve(self, problem):
        response = await llm_call(self.system_prompt, problem)
        return response
'''

# 计算奖励
score = asyncio.run(compute_score(workflow_code, "sudoku"))
print(f"Reward score: {score:.3f}")
```

### 批量计算

```python
from workflow_reward import batch_compute_rewards
import asyncio

workflow_codes = [code1, code2, code3]
task_names = ["sudoku", "game24", "minesweeper"]

scores = asyncio.run(batch_compute_rewards(workflow_codes, task_names))
```

## 🔧 高级功能

### 自定义任务选择

在`config.json`中配置任务选择模式：

```json
{
    "task_selection": {
        "mode": "manual",      # 手动选择
        "manual_tasks": ["task1", "task2"]
    }
}
```

或

```json
{
    "task_selection": {
        "mode": "random",      # 随机选择
        "auto_select_count": 50
    }
}
```

### 查看可用任务

```python
from internbootcamp_utils import InternBootcampManager

manager = InternBootcampManager()
print(f"Available tasks: {manager.get_available_tasks()}")
print(f"Failed tasks: {manager.get_failed_tasks()}")
```

## ⚠️ 注意事项

1. **任务兼容性**：部分bootcamp可能存在bug，系统会自动跳过
2. **生成时间**：处理大量任务可能需要较长时间
3. **API限制**：注意LLM API的调用频率限制
4. **内存使用**：生成大量数据时注意内存使用

## 🧪 测试系统

```bash
# 运行完整测试
python test_system.py

# 测试特定任务
python test_system.py --task sudoku
```

## 📈 统计信息

生成数据后，查看`data/metadata.json`获取详细统计：
- 总生成条目数
- 成功/失败的任务
- 训练/测试集分割信息

## 🤝 贡献

欢迎提交Issue和PR来改进系统！