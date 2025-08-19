# InternBootcamp 迁移方案详细设计

## 1. 迁移目标

将InternBootcamp功能从`Test_FILE/verl_internbootcamp/`迁移到`New_evaluation_and_RL/`，复用ScoreFlow的架构和代码，实现统一的管理和执行。

## 2. 现状分析

### 2.1 InternBootcamp原有组件
```
Test_FILE/verl_internbootcamp/
├── filter_and_generate_verl.py    # 过滤和生成入口
├── generate_verl_data.py          # VERL数据生成器
├── internbootcamp_reward_utils.py # Reward计算器
├── internbootcamp_reward_server.py # REST API服务器
└── internbootcamp_utils.py        # 工具类（InternBootcampManager）
```

### 2.2 与ScoreFlow的差异

| 方面 | InternBootcamp | ScoreFlow |
|------|---------------|-----------|
| 数据源 | InternBootcamp任务 | 多种benchmark |
| Handler | bootcamp类 | BenchmarkHandler |
| 配置 | config.json | config.yaml |
| 验证方法 | verify_score | judge |
| 执行方式 | MetaGPT | MetaGPT |
| 数据过滤 | 有（quality_evaluation） | 无 |

## 3. 迁移策略

### 3.1 核心原则
1. **最大化复用ScoreFlow代码**
2. **最小化修改，仅处理差异部分**
3. **保持接口兼容性**
4. **使用配置驱动，避免硬编码**

### 3.2 架构设计

```
New_evaluation_and_RL/
├── config.yaml                        # 添加internbootcamp配置
├── generate_parquet_and_jsonl/
│   └── internbootcamp_generate_verl_training_data.py  # 新建
├── internbootcamp_reward_server/      # 新建目录
│   ├── internbootcamp_reward_utils.py # 复用ScoreFlow，仅修改关键函数
│   ├── internbootcamp_reward_server.py # 复用ScoreFlow，改端口
│   └── internbootcamp_adapter.py      # 新建适配器
└── docs/
    └── internbootcamp_migration.md    # 迁移文档
```

## 4. 详细实现方案

### 4.1 Step 1: 更新config.yaml

```yaml
# 在config.yaml中添加
services:
  internbootcamp_reward:
    enabled: true
    host: "0.0.0.0"
    port: 8900          # 使用不同端口
    timeout: 300
    debug: true
    workspace: "New_evaluation_and_RL/internbootcamp_workspace"

# 添加internbootcamp相关路径
paths:
  internbootcamp_bootcamp: "internbootcamp/bootcamp"  # bootcamp类路径
  internbootcamp_analysis: "bootcamp_analysis_filtered.jsonl"  # 分析文件路径
```

### 4.2 Step 2: 创建InternBootcamp适配器

**文件**: `internbootcamp_adapter.py`

```python
"""
InternBootcamp到ScoreFlow的适配器
将bootcamp类适配为BenchmarkHandler接口
"""
import importlib
from typing import Dict, Any, List
from pathlib import Path
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class InternBootcampAdapter(BenchmarkHandler):
    """将InternBootcamp的bootcamp类适配为BenchmarkHandler"""
    
    def __init__(self, task_name: str, dataset_path: str = None, config=None):
        super().__init__(dataset_path, config)
        self.task_name = task_name
        self.bootcamp_class = self._load_bootcamp_class(task_name)
    
    def _load_bootcamp_class(self, task_name: str):
        """动态加载bootcamp类"""
        module_path = f"internbootcamp.bootcamp.{task_name}.{task_name}"
        module = importlib.import_module(module_path)
        class_name = f"{task_name.capitalize()}bootcamp"
        return getattr(module, class_name)
    
    def get_prompt_text(self, data_indices: List[int]) -> str:
        """获取prompt文本"""
        if hasattr(self.bootcamp_class, 'prompt_func'):
            # 获取测试数据
            test_data = self._get_test_data(data_indices[0])
            return self.bootcamp_class.prompt_func(test_data)
        return ""
    
    def judge(self, result: str, verification_data: Dict) -> bool:
        """验证结果（适配verify_score）"""
        if hasattr(self.bootcamp_class, 'verify_score'):
            score = self.bootcamp_class.verify_score(
                model_output=result,
                identity=verification_data,
                format_score=0.1,
                short_penalty=False,
                format_penalty=False
            )
            return score > 0.5  # 转换为布尔值
        return False
    
    def get_verification_data(self, index: int) -> Dict:
        """获取验证数据"""
        return self._get_test_data(index)
    
    def _get_test_data(self, index: int) -> Dict:
        """获取测试数据（从InternBootcampManager）"""
        from internbootcamp_utils import InternBootcampManager
        manager = InternBootcampManager()
        examples = manager.generate_task_examples(self.task_name, n_examples=index+1)
        if examples and len(examples) > index:
            return examples[index]
        return {}
```

### 4.3 Step 3: 数据生成器（复用ScoreFlow）

**文件**: `internbootcamp_generate_verl_training_data.py`

```python
"""
InternBootcamp VERL数据生成器
复用ScoreFlow的VerlTrainingDataGenerator，仅修改必要部分
"""
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加路径
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# 导入ScoreFlow的生成器
from generate_verl_training_data import VerlTrainingDataGenerator

class InternBootcampVerlGenerator(VerlTrainingDataGenerator):
    """InternBootcamp特化的VERL生成器"""
    
    def __init__(self, output_dir: str = None):
        super().__init__(output_dir)
        self.filtered_tasks = []  # 过滤后的任务
        self.task_display_names = {}  # 任务显示名称映射
    
    def load_filtered_tasks(self, analysis_file: str) -> List[Dict]:
        """加载并过滤任务（来自filter_and_generate_verl.py）"""
        filtered_tasks = []
        
        with open(analysis_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    task_data = json.loads(line)
                    
                    # 过滤条件
                    english_detailed = task_data.get('english_detailed', '')
                    quality_eval = task_data.get('quality_evaluation', {})
                    
                    if english_detailed.startswith('Error'):
                        continue
                    if quality_eval.get('correctness') == 'incorrect':
                        continue
                    
                    # 保存任务信息
                    filtered_task = {
                        'task_name': task_data['task_name'],
                        'display_name': english_detailed,
                        'quality_score': quality_eval.get('quality_score', 0)
                    }
                    filtered_tasks.append(filtered_task)
                    self.task_display_names[task_data['task_name']] = english_detailed
                    
                except Exception as e:
                    logging.warning(f"Error processing task: {e}")
                    continue
        
        self.filtered_tasks = filtered_tasks
        logging.info(f"Loaded {len(filtered_tasks)} filtered tasks")
        return filtered_tasks
    
    def _construct_prompt(self, handler, data_indices: List[int], 
                         benchmark_name: str) -> tuple:
        """构建prompt（覆盖父类方法以支持InternBootcamp）"""
        # 对于InternBootcamp，使用task_name作为benchmark_name
        if benchmark_name.startswith('internbootcamp_'):
            task_name = benchmark_name.replace('internbootcamp_', '')
            
            # 使用InternBootcamp的prompt模板
            from ScoreFlow.scripts.internbootcamp.conditions import (
                START_PROMPT, END_PROMPT, SYSTEM_PROMPT
            )
            
            # 获取任务描述
            display_name = self.task_display_names.get(task_name, task_name)
            problem_text = handler.get_prompt_text(data_indices)
            
            # 构建用户指令
            user_content = START_PROMPT.format(prompt_text=f"Task: {display_name}\n{problem_text}")
            user_content += END_PROMPT
            
            messages = [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_content}
            ]
            
            return messages, problem_text
        else:
            # 非InternBootcamp任务，使用父类方法
            return super()._construct_prompt(handler, data_indices, benchmark_name)
    
    def generate_for_internbootcamp_task(self, task_name: str, 
                                        num_entries: int = 5) -> Dict[str, pd.DataFrame]:
        """为InternBootcamp任务生成数据"""
        # 使用特殊的benchmark名称前缀
        benchmark_name = f"internbootcamp_{task_name}"
        
        # 创建临时的benchmark映射
        self.benchmark_mapping[benchmark_name] = {
            'benchmark': benchmark_name,
            'handler_class': 'InternBootcampAdapter',
            'handler_dir': 'internbootcamp_adapter',
            'data_train_dir': '',  # InternBootcamp不使用文件数据集
            'data_test_dir': ''
        }
        
        # 生成数据（复用父类方法）
        return self.generate_for_benchmark(
            benchmark_name,
            dataset_type='both',
            num_train_entries=num_entries,
            num_test_entries=num_entries // 5,  # 20%作为测试集
            test_cases_per_entry=3
        )
```

### 4.4 Step 4: Reward计算器（最大化复用）

**文件**: `internbootcamp_reward_utils.py`

```python
"""
InternBootcamp Reward计算器
最大化复用ScoreFlow的代码，仅修改必要部分
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加路径
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# 导入ScoreFlow的Reward计算器
from reward_server.scoreflow_reward_utils import (
    ScoreFlowRewardCalculator,
    compute_score as scoreflow_compute_score,
    _compute_score_async as scoreflow_compute_async
)

# 导入适配器
from internbootcamp_adapter import InternBootcampAdapter

class InternBootcampRewardCalculator(ScoreFlowRewardCalculator):
    """InternBootcamp特化的Reward计算器"""
    
    def _load_benchmark_handler(self, benchmark_name: str, dataset_path: str):
        """覆盖父类方法，支持InternBootcamp"""
        # 检查是否是InternBootcamp任务
        if benchmark_name.startswith('internbootcamp_'):
            task_name = benchmark_name.replace('internbootcamp_', '')
            return InternBootcampAdapter(task_name, dataset_path, self.llm_config)
        else:
            # 非InternBootcamp，使用父类方法
            return super()._load_benchmark_handler(benchmark_name, dataset_path)

# 全局计算器实例
_global_calculator = None

def get_calculator():
    """获取全局计算器实例"""
    global _global_calculator
    if _global_calculator is None:
        _global_calculator = InternBootcampRewardCalculator()
    return _global_calculator

def compute_score(data_source: str, solution_str: str, 
                 ground_truth: str, extra_info: Dict) -> float:
    """
    计算分数（兼容VERL接口）
    直接调用ScoreFlow的compute_score，数据格式已兼容
    """
    # 如果是InternBootcamp任务，添加前缀
    if 'task_name' in extra_info:
        data_source = f"internbootcamp_{extra_info['task_name']}"
    
    return scoreflow_compute_score(data_source, solution_str, ground_truth, extra_info)
```

### 4.5 Step 5: REST API服务器（最小修改）

**文件**: `internbootcamp_reward_server.py`

```python
"""
InternBootcamp Reward服务器
复用ScoreFlow的服务器代码，仅修改端口和服务名
"""
import sys
from pathlib import Path

# 添加路径
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# 导入ScoreFlow的服务器代码
from reward_server.scoreflow_reward_server import (
    app, logger, SERVER_CONFIG,
    health_check, compute_score_endpoint, 
    batch_compute_endpoint, get_config
)

# 导入InternBootcamp的compute_score
from internbootcamp_reward_utils import compute_score, get_calculator

# 修改服务配置
SERVER_CONFIG['port'] = 8900  # 使用不同端口
SERVER_CONFIG['service_name'] = 'internbootcamp_reward_server'

# 覆盖健康检查以返回正确的服务名
@app.route('/health', methods=['GET'])
def health_check_internbootcamp():
    return jsonify({
        'status': 'healthy',
        'service': 'internbootcamp_reward_server',
        'version': '2.0.0'
    })

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='InternBootcamp Reward Server')
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8900)
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    
    logger.info(f"Starting InternBootcamp Reward Server on {args.host}:{args.port}")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )
```

## 5. 执行步骤

### 5.1 准备阶段
1. ✅ 阅读并理解现有代码
2. ✅ 创建架构文档
3. ✅ 设计迁移方案

### 5.2 实施阶段（待用户批准）
1. [ ] 更新config.yaml，添加InternBootcamp配置
2. [ ] 创建internbootcamp_adapter.py
3. [ ] 创建internbootcamp_generate_verl_training_data.py
4. [ ] 创建internbootcamp_reward_utils.py
5. [ ] 创建internbootcamp_reward_server.py
6. [ ] 测试数据生成功能
7. [ ] 测试Reward计算功能
8. [ ] 测试REST API服务

## 6. 关键修改点总结

### 6.1 最小化修改原则
1. **复用ScoreFlow所有基础设施**（日志、并行执行、配置管理）
2. **仅创建适配器处理差异**（bootcamp类 → BenchmarkHandler）
3. **保持接口兼容**（VERL数据格式、REST API）

### 6.2 主要差异处理

| 差异点 | 解决方案 |
|--------|---------|
| bootcamp类 vs Handler | 创建InternBootcampAdapter适配器 |
| verify_score vs judge | 在适配器中转换 |
| 任务过滤 | 在生成器中保留过滤逻辑 |
| prompt模板 | 使用InternBootcamp的conditions |
| 数据源 | 添加internbootcamp_前缀区分 |

### 6.3 代码复用统计
- **ScoreFlow代码复用率**: ~90%
- **新增代码量**: ~200行（主要是适配器）
- **修改代码量**: ~50行（覆盖方法）

## 7. 测试计划

### 7.1 单元测试
```python
# 测试适配器
adapter = InternBootcampAdapter('sudoku_4x4_easy')
assert adapter.get_prompt_text([0]) != ""
assert adapter.judge("correct answer", {}) == True

# 测试数据生成
generator = InternBootcampVerlGenerator()
generator.load_filtered_tasks('bootcamp_analysis_filtered.jsonl')
assert len(generator.filtered_tasks) > 0

# 测试Reward计算
score = compute_score('internbootcamp_sudoku', workflow_code, 'default', extra_info)
assert 0 <= score <= 1
```

### 7.2 集成测试
1. 启动InternBootcamp Reward服务器
2. 发送测试请求到/compute_score
3. 验证返回分数合理
4. 测试批量计算功能

### 7.3 端到端测试
1. 生成InternBootcamp VERL数据
2. 使用数据训练模型（模拟）
3. 计算训练后模型的Reward
4. 验证整个流程正常

## 8. 风险评估

### 8.1 低风险
- 端口冲突（使用不同端口）
- 配置错误（有默认值）
- 日志混淆（独立日志目录）

### 8.2 中风险
- bootcamp类加载失败（需要正确的Python路径）
- 数据格式不兼容（通过适配器处理）

### 8.3 高风险
- MetaGPT执行环境问题（复用ScoreFlow已验证的代码）

## 9. 优势分析

### 9.1 代码复用
- 复用ScoreFlow的所有基础设施
- 减少代码维护成本
- 统一的错误处理和日志

### 9.2 性能提升
- 继承并行执行优化
- All-Reduce汇总模式
- 独立日志避免I/O冲突

### 9.3 可维护性
- 统一配置管理
- 模块化设计
- 清晰的适配器模式

### 9.4 扩展性
- 易于添加新的InternBootcamp任务
- 可以同时支持ScoreFlow和InternBootcamp
- 未来可以添加更多数据源

## 10. 总结

本迁移方案通过**适配器模式**和**最大化代码复用**，以最小的工作量将InternBootcamp功能迁移到新架构。主要创新点：

1. **InternBootcampAdapter**：优雅地将bootcamp类适配为BenchmarkHandler
2. **统一配置管理**：使用config.yaml管理所有配置
3. **代码复用率90%+**：最大化利用ScoreFlow的成熟代码
4. **保持兼容性**：完全兼容VERL数据格式和REST API

迁移后，InternBootcamp将获得ScoreFlow的所有优化特性，包括并行执行、独立日志、结构化输出等。