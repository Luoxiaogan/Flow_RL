# InternBootcamp VERL训练支持系统实施计划

## 1. 项目背景

InternBootcamp与传统benchmark（如GSM8K、MBPP）有本质区别：
- **动态数据生成**：通过`case_generator()`实时生成任务，而非使用固定数据集
- **任务多样性**：包含1000+种不同任务类型（逻辑谜题、算法、游戏等）
- **统一接口**：所有任务继承自`Basebootcamp`，提供标准化的接口

## 2. 核心目标

创建一个VERL格式的训练数据生成系统，包括：
1. **VERL数据生成器**：生成符合VERL格式的训练数据
2. **工作流奖励计算器**：评估生成的工作流质量
3. **不依赖ScoreFlow Handler**：直接使用InternBootcamp的原生接口

## 3. 系统架构设计

### 3.1 文件结构
```
Test_FILE/verl_support_internbootcamp/
├── plan.md                          # 本计划文档
├── README.md                        # 系统说明文档
├── config.json                      # 配置文件
├── generate_verl_data.py            # VERL数据生成主程序
├── workflow_reward.py               # 工作流奖励计算
├── internbootcamp_utils.py          # InternBootcamp工具函数
├── workflow_generator_intern.py     # 工作流生成器（参考workflow_test_v2）
├── workflow_executor_intern.py      # 工作流执行器（参考workflow_test_v2）
├── test_system.py                   # 系统测试脚本
└── data/                           # 生成的数据
    ├── internbootcamp_verl_train.parquet
    └── internbootcamp_verl_test.parquet
```

### 3.2 核心组件设计

#### 3.2.1 InternBootcamp工具模块（internbootcamp_utils.py）
```python
class InternBootcampManager:
    def __init__(self):
        self.bootcamp_registry = self._discover_bootcamps()
    
    def _discover_bootcamps(self):
        """动态发现所有可用的bootcamp类"""
        
    def get_bootcamp_class(self, task_name):
        """获取指定的bootcamp类"""
        
    def generate_task_examples(self, task_name, n_examples=2):
        """生成n个任务示例"""
        bootcamp_class = self.get_bootcamp_class(task_name)
        bootcamp = bootcamp_class()
        
        examples = []
        for _ in range(n_examples):
            identity = bootcamp.case_generator()
            prompt = bootcamp.prompt_func(identity)
            examples.append({
                "identity": identity,
                "prompt": prompt
            })
        return examples
    
    def get_task_description(self, task_name):
        """从源代码中提取任务描述"""
```

#### 3.2.2 VERL数据生成器（generate_verl_data.py）
```python
def generate_verl_prompt(task_name, task_examples, task_description):
    """构建VERL格式的prompt"""
    system_prompt = "You are designing a general problem-solving workflow..."
    
    # 包含任务描述和多个示例
    user_prompt = f"""
Task Type: {task_name}

Task Description:
{task_description}

Example Problems:
{format_examples(task_examples)}

Please create a workflow to solve this type of problem.
"""
    
    return format_verl_prompt(system_prompt, user_prompt)

def generate_verl_data():
    """生成VERL训练数据"""
    manager = InternBootcampManager()
    verl_data = []
    
    for task_name in selected_tasks:
        # 生成任务示例
        examples = manager.generate_task_examples(task_name, n_examples=2)
        description = manager.get_task_description(task_name)
        
        # 构建VERL格式数据
        verl_entry = {
            "data_source": f"internbootcamp_{task_name}",
            "prompt": generate_verl_prompt(task_name, examples, description),
            "ability": classify_ability(task_name),
            "reward_model": {
                "task_name": task_name,
                "test_cases": [ex["identity"] for ex in examples]
            },
            "extra_info": {
                "task_type": get_task_type(task_name),
                "num_examples": len(examples)
            }
        }
        verl_data.append(verl_entry)
    
    return verl_data
```

#### 3.2.3 工作流生成器（workflow_generator_intern.py）
参考`workflow_test_v2`的设计，生成通用的工作流：
```python
async def generate_workflow(task_name, examples, description):
    """生成解决特定任务的工作流"""
    # 使用上游模型生成system_prompt
    system_prompt = await generate_system_prompt(task_name, examples, description)
    
    # 构建工作流代码
    workflow_code = f"""
class InternBootcampWorkflow:
    def __init__(self):
        self.system_prompt = '''{system_prompt}'''
    
    async def solve(self, problem):
        # 使用下游模型解决问题
        response = await llm_call(self.system_prompt, problem)
        return response
"""
    return workflow_code
```

#### 3.2.4 工作流奖励计算（workflow_reward.py）
```python
class WorkflowRewardCalculator:
    def __init__(self):
        self.manager = InternBootcampManager()
    
    async def compute_workflow_reward(self, workflow_code, task_name, test_indices=None):
        """计算工作流的奖励分数"""
        bootcamp_class = self.manager.get_bootcamp_class(task_name)
        bootcamp = bootcamp_class()
        
        # 生成测试用例
        if test_indices is None:
            test_cases = [bootcamp.case_generator() for _ in range(3)]
        
        # 执行工作流
        results = await execute_workflow(workflow_code, test_cases, bootcamp)
        
        # 计算奖励
        total_score = 0
        for result, test_case in zip(results, test_cases):
            score = bootcamp.verify_score(result, test_case)
            total_score += score
        
        return total_score / len(test_cases)

# 简化接口
async def compute_score(workflow_code, task_name):
    """简化的奖励计算接口"""
    calculator = WorkflowRewardCalculator()
    return await calculator.compute_workflow_reward(workflow_code, task_name)
```

### 3.3 数据流程

1. **任务选择**：从InternBootcamp中选择代表性任务
2. **示例生成**：每个任务生成2个示例（通过case_generator）
3. **描述提取**：从源代码提取任务描述
4. **VERL数据构建**：组合成VERL格式的训练数据
5. **工作流生成**：基于任务信息生成解题工作流
6. **奖励计算**：执行工作流并验证结果

## 4. 实施步骤

### 第一阶段：基础设施搭建
1. 创建目录结构
2. 实现InternBootcamp工具模块
3. 编写配置文件

### 第二阶段：核心功能实现
1. 实现VERL数据生成器
2. 实现工作流生成器（参考workflow_test_v2）
3. 实现奖励计算器

### 第三阶段：系统集成
1. 编写主程序入口
2. 实现批量处理功能
3. 添加错误处理和日志

### 第四阶段：测试与优化
1. 编写测试脚本
2. 验证数据格式
3. 性能优化

## 5. 关键技术点

### 5.1 动态任务加载
- 使用Python反射机制动态发现bootcamp类
- 处理导入错误和兼容性问题

### 5.2 任务描述提取
- 从源代码注释中提取描述
- 处理格式不一致的情况

### 5.3 通用工作流设计
- 生成能适应不同任务类型的工作流
- 使用system_prompt指导下游模型

### 5.4 并行处理
- 支持多任务并行生成
- 异步执行工作流验证

## 6. 预期输出

### 6.1 VERL训练数据格式
```json
{
    "data_source": "internbootcamp_sudoku",
    "prompt": "<|system|>\nYou are designing...<|user|>\nTask Type: sudoku\n...<|end|>",
    "ability": "logic_reasoning",
    "reward_model": {
        "task_name": "sudoku",
        "test_cases": [{"puzzle": [...], "size": 9}, ...]
    },
    "extra_info": {
        "task_type": "logic_puzzle",
        "num_examples": 2,
        "difficulty": "medium"
    }
}
```

### 6.2 简化的奖励计算接口
```python
from workflow_reward import compute_score

# 单行调用
score = await compute_score(workflow_code, "sudoku")
```

## 7. 与现有系统的差异

| 特性 | 传统VERL支持 | InternBootcamp VERL支持 |
|-----|------------|----------------------|
| 数据来源 | 固定数据集文件 | 动态生成（case_generator） |
| 任务类型 | 单一（如数学） | 1000+种任务 |
| Handler依赖 | 需要ScoreFlow Handler | 直接使用Basebootcamp接口 |
| 验证方式 | 简单答案比对 | 任务特定的verify_score |
| 扩展性 | 需要修改代码 | 自动发现新任务 |

## 8. 风险与挑战

1. **任务兼容性**：部分bootcamp可能存在bug或不完整
2. **性能问题**：动态加载和执行可能较慢
3. **错误处理**：需要优雅处理各种异常情况

## 9. 成功标准

1. 成功生成至少50种不同任务的VERL数据
2. 奖励计算功能正常工作
3. 提供简洁的API接口
4. 系统稳定可靠

这个计划充分考虑了InternBootcamp的特殊性，设计了一个灵活、可扩展的VERL训练支持系统。
