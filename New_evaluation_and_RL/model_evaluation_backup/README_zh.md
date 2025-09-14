# 模型评估框架

用于评估本地和API语言模型在各种基准测试上性能的综合框架。

**📁 重构目录组织**: 该模块已重新组织，清晰分离配置、脚本和核心功能，提升可维护性。

## 📁 目录结构

```
model_evaluation/
├── configs/                    # 配置文件
│   ├── evaluation_config.yaml  # 单模型评估配置  
│   ├── example_config.yaml     # 示例配置模板
│   └── models_config.yaml      # 批量评估模型配置
├── scripts/                    # 可执行脚本和入口点
│   ├── evaluate_all_models.sh  # 统一模型评估脚本 (Linux/macOS)
│   ├── evaluate_all_models.bat # 统一模型评估脚本 (Windows)
│   ├── evaluate_models.sh      # 传统批量评估脚本 (Linux/macOS) 
│   ├── evaluate_models.bat     # 传统批量评估脚本 (Windows)
│   ├── run_evaluation.py       # 单模型评估入口
│   └── run_unified_evaluation.py # 统一评估入口
├── core/                       # 按组件类型分类的核心功能
│   ├── __init__.py
│   ├── interfaces/             # 模型接口抽象
│   │   ├── __init__.py
│   │   ├── model_interface.py      # 所有模型的基础接口
│   │   ├── local_model_interface.py # 本地模型实现
│   │   └── api_model_interface.py   # API模型实现  
│   ├── evaluators/             # 批量和统一评估逻辑
│   │   ├── __init__.py
│   │   ├── model_evaluator.py      # 核心评估逻辑
│   │   ├── batch_evaluator.py      # 批量评估编排
│   │   └── unified_batch_evaluator.py # 高级统一评估
│   └── utils/                  # 支撑工具和助手
│       ├── __init__.py
│       ├── api_connection_pool.py  # API连接管理
│       ├── config_validator.py     # 配置验证
│       ├── model_factory.py        # 模型创建工厂
│       ├── report_generator.py     # 结果报告和可视化
│       ├── resource_manager.py     # GPU资源管理
│       ├── reward_server_checker.py # Reward服务器健康检查
│       └── score_collector.py      # 分数收集和处理
└── __init__.py                 # 主模块入口 (向后兼容)
```

## 🚀 快速开始

### 前置条件

1. **环境设置**
   ```bash
   # Linux/macOS
   source /opt/anaconda3/etc/profile.d/conda.sh
   conda activate workflow
   
   # Windows
   conda activate workflow
   ```

2. **所需依赖**
   ```bash
   pip install torch transformers aiohttp peft bitsandbytes pandas matplotlib seaborn tqdm pyyaml
   ```

3. **启动Reward服务器** (必需)
   ```bash
   # Linux/macOS/WSL
   bash ../servers_and_proxy/start_scoreflow_reward.sh
   
   # Windows
   ..\servers_and_proxy\start_scoreflow_reward.bat
   ```

### 使用示例

#### 1. 统一模型评估 (推荐)

**Linux/macOS:**
```bash
cd scripts/
./evaluate_all_models.sh
```

**Windows:**
```batch
cd scripts
evaluate_all_models.bat
```

**带参数使用:**
```bash
# Linux/macOS
./evaluate_all_models.sh -c ../configs/models_config.yaml -n 100 -o ../results -f api

# Windows  
evaluate_all_models.bat -c ..\configs\models_config.yaml -n 100 -o ..\results -f api
```

#### 2. 单模型评估

```bash
cd scripts/
python run_evaluation.py --config ../configs/evaluation_config.yaml --max-samples 50
```

#### 3. 自定义统一评估

```bash
cd scripts/
python run_unified_evaluation.py --config ../configs/models_config.yaml --batch-size 4
```

## ⚙️ 配置说明

### 统一模型配置 (`configs/models_config.yaml`)

```yaml
models:
  # 本地模型
  - name: "llama-3-8b-instruct" 
    type: "local"
    model_path: "/path/to/model"
    load_in_4bit: true
    generation_params:
      max_new_tokens: 4096
      temperature: 0.7
    
  # API模型  
  - name: "gpt-4"
    type: "api"
    api_base: "https://api.openai.com/v1"
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
    generation_params:
      max_new_tokens: 4096
      temperature: 0.8

evaluation:
  benchmark: "gsm8k"          # gsm8k, mbpp, hotpotqa, 等
  max_samples: 100            # 测试样本数量 
  batch_size: 4               # 处理批次大小
  timeout: 180                # 每次评估超时时间 (秒)
  
output:
  save_results: true
  output_dir: "./evaluation_results"
  generate_report: true
  save_detailed_csv: true
```

### 单模型配置 (`configs/evaluation_config.yaml`)

```yaml
model:
  name: "test-model"
  type: "local"              # 或 "api"
  model_path: "/path/to/model"
  generation_params:
    max_new_tokens: 4096
    temperature: 0.7
    
evaluation:
  benchmark: "gsm8k" 
  max_samples: 50
  batch_size: 2
  
output:
  output_dir: "./results"
  generate_charts: true
```

## 📊 命令行选项

### 统一评估脚本选项

```bash
选项:
  -c, --config FILE      模型配置文件 (默认: ../configs/models_config.yaml)
  -n, --max-samples N    最大评估样本数
  -o, --output-dir DIR   输出目录
  -b, --batch-size N     批处理大小  
  -f, --filter TYPE      过滤模型类型 (api/local/等)
  -l, --limit N          限制评估的模型数量
  -y, --yes              跳过确认提示
  -h, --help             显示帮助信息
```

### 单模型评估选项

```bash
选项:
  --config, -c           配置文件路径
  --test-data, -t        测试数据文件路径  
  --max-samples, -n      最大样本数量
  --output-dir, -o       输出目录
  --batch-size, -b       处理批次大小
  --log-level, -l        日志级别 (DEBUG/INFO/WARNING/ERROR)
  --yes, -y              跳过确认提示
```

## 🔧 架构特性

### 核心设计原则

1. **关注点分离**: 配置、脚本和核心逻辑清晰分离
2. **统一接口**: 本地和API模型的单一接口
3. **资源管理**: 本地模型的智能GPU内存管理  
4. **异步处理**: 高效并发评估与连接池
5. **健康监控**: 自动Reward服务器健康检查
6. **丰富报告**: 带可视化的综合评估报告

### 关键组件

- **Interfaces**: 支持本地和API模型的抽象模型接口
- **Evaluators**: 具有高级资源管理的批处理逻辑
- **Utils**: 用于验证、报告和基础设施的支撑工具

### 导入使用 (向后兼容)

```python
# 主要导入 - 完全向后兼容
from model_evaluation import (
    BatchModelEvaluator,
    UnifiedBatchEvaluator, 
    BaseModelInterface,
    LocalModelInterface,
    APIModelInterface,
    ModelFactory,
    RewardServerChecker,
    ScoreCollector
)

# 从组织结构直接导入
from model_evaluation.core.interfaces import LocalModelInterface
from model_evaluation.core.evaluators import UnifiedBatchEvaluator  
from model_evaluation.core.utils import ModelFactory, ReportGenerator
```

## 📈 输出结构

```
evaluation_results/
├── model_*.json                # 单个模型详细报告
├── model_*.md                  # 人类可读的markdown报告  
├── model_comparison.json       # 模型间对比数据
├── model_comparison.md         # 对比总结报告
├── detailed_results.csv        # CSV格式完整结果
├── charts/                     # 生成的可视化图表
│   ├── overall_scores.png      # 分数对比柱状图
│   ├── benchmark_heatmap.png   # 性能热力图  
│   └── model_rankings.png      # 排名可视化
└── logs/
    ├── evaluation_*.log        # 详细执行日志
    └── error_*.log             # 错误跟踪日志
```

## 🛠️ 开发与扩展

### 添加新模型类型

1. 在 `core/interfaces/` 中创建新接口
2. 扩展 `BaseModelInterface` 
3. 更新 `core/utils/model_factory.py` 中的 `ModelFactory`
4. 添加配置示例和测试

### 添加新基准测试

1. 更新 `core/evaluators/` 中的评估逻辑
2. 添加基准特定的配置模式
3. 根据需要更新Reward服务器集成
4. 添加验证和错误处理

### 自定义评估指标

1. 在 `core/utils/score_collector.py` 中扩展 `ScoreCollector`  
2. 在 `ReportGenerator` 中更新报告生成
3. 根据需要添加新的可视化类型

## 🐛 问题排查

### 常见问题

1. **重构后导入错误**
   ```bash
   # 确保正确的PYTHONPATH
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   
   # 测试导入
   python -c "from model_evaluation import BatchModelEvaluator; print('OK')"
   ```

2. **Reward服务器连接问题**  
   ```bash
   # 检查健康状态
   curl -s http://localhost:8899/health
   
   # 如需要重启
   bash ../servers_and_proxy/start_scoreflow_reward.sh
   ```

3. **找不到配置文件**
   ```bash
   # 确保从正确目录运行
   cd scripts/  
   ls ../configs/  # 应显示yaml文件
   ```

4. **GPU内存问题**
   - 在配置中减小 `batch_size`
   - 使用更小的 `max_samples` 进行测试  
   - 为本地模型启用4位量化

5. **Windows批处理脚本编码问题**
   ```batch
   # 测试编码显示
   cd scripts
   test_encoding.bat
   
   # 如果中文字符显示不正常：
   # - 确保终端支持UTF-8 (推荐使用Windows Terminal)
   # - 脚本会自动设置UTF-8代码页 (chcp 65001)
   # - 状态信息使用 [OK]、[WARNING]、[ERROR] 而不是特殊符号
   ```

### 健康检查

```bash
# 验证目录结构
ls -la configs/ scripts/ core/

# 测试Python模块结构  
cd model_evaluation
python -c "from core.utils import RewardServerChecker; print('模块结构正常')"

# 验证配置
cd scripts/
python -c "import yaml; print(yaml.safe_load(open('../configs/example_config.yaml')))"
```

## 📄 从旧结构迁移

重构保持完全向后兼容性:

- 所有现有导入语句继续工作
- 配置文件路径在脚本中自动更新
- 旧的脚本名称和参数保持功能  
- API接口保持不变

**新结构优势:**
- 更好的代码组织和可维护性
- 更清晰的关注点分离
- 更容易测试和调试
- 改进的IDE支持和导航

## 📝 许可证  

Flow_RL项目的一部分 - 许可证详情请参见主项目文档。