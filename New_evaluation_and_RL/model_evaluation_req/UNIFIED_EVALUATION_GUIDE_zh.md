# 统一模型评估系统 - 完整指南

## 概述

统一模型评估系统允许您在一次运行中评估本地模型和API模型，具有自动资源管理、连接池和配置验证功能。

## 核心特性

### 1. 资源管理
- **自动清理**：使用上下文管理器确保即使出现异常也能清理模型
- **全局资源跟踪**：跟踪所有活动模型并确保清理
- **GPU内存管理**：每个模型评估后自动清理CUDA缓存

### 2. API连接池
- **连接复用**：为API调用维护持久HTTP会话
- **按服务分池**：不同API服务使用独立的连接池
- **自动恢复**：自动重建已关闭的连接

### 3. 配置验证
- **JSON Schema验证**：根据严格的模式验证配置
- **路径检查**：验证模型和数据路径是否存在
- **类型检查**：确保所有参数类型正确
- **重复检测**：警告重复的模型名称

## 安装

```bash
# 必需的包
pip install torch transformers aiohttp peft bitsandbytes jsonschema

# 可选的性能增强包
pip install accelerate scipy matplotlib seaborn pandas
```

## 配置

### 完整配置示例

```yaml
# models_config.yaml

# 测试数据配置
test_data:
  path: "../generate_parquet_and_jsonl/test_data.jsonl"
  max_samples: 100  # null表示使用所有样本

# Reward服务器
reward_server:
  url: "http://localhost:8899"

# 评估设置
evaluation:
  batch_size: 8
  output_dir: "./evaluation_reports"
  save_intermediate: true  # 保存中间结果

# 待评估的模型
models:
  # API模型示例
  - name: "GPT-4"
    type: "api"
    api_endpoints: ["https://api.openai.com"]
    api_keys: ["${OPENAI_API_KEY}"]  # 支持环境变量
    model: "gpt-4"
    api_type: "openai"
    timeout: 60
    generation_params:
      max_new_tokens: 4096
      temperature: 0.7

  # 本地模型示例
  - name: "Qwen-7B"
    type: "local"
    base_model_path: "/models/Qwen2.5-7B-Instruct"
    device_map: "auto"
    torch_dtype: "bfloat16"
    generation_params:
      max_new_tokens: 4096
      temperature: 0.7

  # LoRA模型示例
  - name: "Qwen-LoRA"
    type: "local_with_lora"
    base_model_path: "/models/Qwen2.5-7B-Instruct"
    lora_path: "/lora/math_adapter"
    device_map: "auto"
    generation_params:
      temperature: 0.6

  # 量化模型示例
  - name: "Llama-4bit"
    type: "local_with_lora"
    base_model_path: "meta-llama/Llama-3.1-8B"
    lora_path: "./lora_weights"
    load_in_4bit: true  # 4位量化
    device_map: "auto"
```

### 模型类型

| 类型 | 描述 | 必需字段 |
|------|------|----------|
| `api` | 基于API的模型 | `api_endpoints`, `model` |
| `local` | 本地模型文件 | `base_model_path` 或 `path` |
| `huggingface` | HuggingFace Hub模型 | `path` |
| `checkpoint` | 训练检查点 | `path` |
| `local_with_lora` | 带LoRA适配器的模型 | `base_model_path`, `lora_path` |

### 生成参数

```yaml
generation_params:
  max_new_tokens: 4096    # 最大生成token数
  temperature: 0.7        # 采样温度 (0.0-2.0)
  top_p: 0.9             # 核采样阈值
  top_k: 50              # Top-k采样
  repetition_penalty: 1.0 # 重复惩罚
  do_sample: true        # 使用采样（vs贪婪）
```

## 使用方法

### 基本使用

```bash
# 使用默认配置运行
bash evaluate_all_models.sh

# 快速测试10个样本
bash evaluate_all_models.sh -n 10 -y

# 仅评估API模型
bash evaluate_all_models.sh -f api

# 仅评估本地模型
bash evaluate_all_models.sh -f local

# 使用自定义配置
bash evaluate_all_models.sh -c custom_config.yaml
```

### Python API

```python
import asyncio
from model_evaluation import UnifiedBatchEvaluator

# 配置
config = {
    'test_data_path': 'test_data.jsonl',
    'reward_server_url': 'http://localhost:8899',
    'output_dir': 'results',
    'eval_batch_size': 8,
    'max_samples': 100
}

# 模型配置
models = [
    {
        'name': 'GPT-4',
        'type': 'api',
        'api_endpoints': ['https://api.openai.com'],
        'api_keys': ['sk-...'],
        'model': 'gpt-4'
    },
    {
        'name': 'Local-Model',
        'type': 'local',
        'base_model_path': '/path/to/model',
        'device_map': 'auto'
    }
]

# 运行评估
async def main():
    evaluator = UnifiedBatchEvaluator(config)
    results = await evaluator.evaluate_models(models)
    print(f"结果保存至: {results['output_dir']}")

asyncio.run(main())
```

### 高级用法与资源管理

```python
from model_evaluation import ModelFactory, ModelResourceManager

async def evaluate_with_management():
    # 创建模型
    model_config = {
        'name': 'Test-Model',
        'type': 'local',
        'base_model_path': '/path/to/model'
    }
    
    model_interface = ModelFactory.create_model(model_config)
    
    # 使用资源管理器自动清理
    async with ModelResourceManager(model_interface) as model:
        # 模型在这里初始化
        result = await model.generate("测试提示词")
        # 模型将自动清理
    
    return result
```

## 资源管理详情

### 自动清理流程

1. **模型创建**：工厂创建适当的接口
2. **资源管理器**：将模型包装在上下文管理器中
3. **初始化**：模型加载权重/连接API
4. **使用**：生成预测
5. **清理**：退出或异常时自动清理

### 全局资源跟踪

```python
from model_evaluation import GlobalResourceTracker

# 检查活动模型
active_count = GlobalResourceTracker.get_active_count()
print(f"活动模型数: {active_count}")

# 强制清理所有模型
await GlobalResourceTracker.cleanup_all()
```

### API连接池

```python
from model_evaluation import APIConnectionPool

# 获取连接统计
stats = APIConnectionPool.get_stats()
print(f"活动会话数: {stats['total_sessions']}")

# 手动清理（通常是自动的）
await APIConnectionPool.cleanup()
```

## 配置验证

### Schema验证

系统使用JSON Schema验证配置：

```python
from model_evaluation import ConfigValidator

# 验证配置
config = {...}  # 您的配置字典
errors = ConfigValidator.validate_config(config, strict=False)

if errors:
    for error in errors:
        print(f"警告: {error}")

# 获取schema供参考
schema = ConfigValidator.get_schema()
```

### 常见验证错误

1. **缺少必需字段**
   - 解决方案：添加必需字段到配置

2. **无效的模型类型**
   - 解决方案：使用以下之一：api, local, huggingface, checkpoint, local_with_lora

3. **路径未找到**
   - 解决方案：验证模型路径存在

4. **重复的模型名称**
   - 解决方案：为每个模型使用唯一名称

## 性能优化

### 内存管理

1. **量化**：大模型使用4位或8位
   ```yaml
   load_in_4bit: true  # 减少约75%内存
   ```

2. **批次大小**：根据GPU内存调整
   ```yaml
   evaluation:
     batch_size: 4  # 如果OOM则减小
   ```

3. **顺序处理**：模型逐个评估

### API优化

1. **连接池**：复用HTTP连接
2. **负载均衡**：API多端点
   ```yaml
   api_endpoints:
     - "http://server1:5000"
     - "http://server2:5000"
   ```

3. **超时设置**：根据模型响应时间调整
   ```yaml
   timeout: 120  # 为慢模型增加
   ```

## 输出结构

```
evaluation_reports/
├── model_*.json           # 单个模型报告
├── model_*.md             # Markdown报告
├── model_comparison.json  # 对比数据
├── model_comparison.md    # 对比报告
├── detailed_results.csv   # CSV格式的所有结果
├── charts/
│   ├── overall_scores.png      # 总体分数图表
│   └── benchmark_heatmap.png   # 基准测试热力图
├── intermediate_*.json    # 中间保存
└── evaluation_*.log       # 执行日志
```

## 故障排除

### 常见问题

1. **OOM（内存不足）**
   - 减小batch_size
   - 使用量化
   - 手动清理GPU缓存

2. **API连接错误**
   - 检查API密钥
   - 验证端点
   - 检查网络/代理设置

3. **模型加载错误**
   - 验证路径存在
   - 检查PyTorch/Transformers版本
   - 确保为LoRA安装了PEFT

4. **配置验证错误**
   - 检查必需字段
   - 验证数据类型
   - 使用schema作为参考

### 调试模式

```bash
# 使用调试日志运行
python run_unified_evaluation.py --log-level DEBUG
```

### 手动资源清理

```python
# 如果需要强制清理
from model_evaluation import GlobalResourceTracker, APIConnectionPool

await GlobalResourceTracker.cleanup_all()
await APIConnectionPool.cleanup()

# 清理CUDA缓存
import torch
torch.cuda.empty_cache()
```

## 最佳实践

1. **从小开始**：先用少量样本测试
   ```bash
   bash evaluate_all_models.sh -n 10
   ```

2. **验证配置**：运行前检查配置
   ```python
   errors = ConfigValidator.validate_config(config)
   ```

3. **监控资源**：观察GPU内存使用
   ```bash
   nvidia-smi -l 1
   ```

4. **保存中间结果**：长时间运行时启用
   ```yaml
   save_intermediate: true
   ```

5. **使用适当类型**：选择正确的模型类型
   - `api`：云服务
   - `local`：下载的模型
   - `local_with_lora`：LoRA适配器

## 重要改进说明

### 资源管理改进

1. **上下文管理器**：所有模型使用 `async with` 确保清理
2. **全局跟踪器**：跟踪所有活动模型，防止泄漏
3. **紧急清理**：即使正常清理失败也会强制清理

### API连接池改进

1. **单例模式**：全局共享连接池
2. **按服务分池**：不同API服务独立管理
3. **自动重连**：检测并重建关闭的连接

### 配置验证改进

1. **JSON Schema**：严格的模式验证
2. **路径验证**：检查文件和目录存在性
3. **类型安全**：确保参数类型正确
4. **早期失败**：在运行前发现配置问题

## API参考

### 核心类

- `UnifiedBatchEvaluator`：主评估编排器
- `BaseModelInterface`：所有模型的抽象接口
- `LocalModelInterface`：本地模型实现
- `APIModelInterface`：API模型实现
- `ModelFactory`：创建适当的模型接口
- `ModelResourceManager`：管理模型生命周期
- `APIConnectionPool`：管理HTTP连接
- `ConfigValidator`：验证配置

### 关键方法

```python
# 评估模型
evaluator = UnifiedBatchEvaluator(config)
results = await evaluator.evaluate_models(model_configs)

# 创建模型
model = ModelFactory.create_model(config)

# 验证配置
errors = ConfigValidator.validate_config(config)
```

## 许可证

Flow_RL项目的一部分。