# InternBootcamp 拒绝采样（Rejection Sampling）支持

本模块为InternBootcamp数据集提供拒绝采样功能，用于生成高质量的SFT（Supervised Fine-Tuning）训练数据。

## 功能概述

- 从VERL格式数据中加载prompts
- 每个prompt调用API生成多个响应（默认8个）
- 使用InternBootcamp reward函数计算每个响应的分数
- 选择reward超过阈值且最高的响应
- 将prompt、response、reward等信息保存为JSONL格式

## 目录结构

```
SFT_support/
├── rejection_sampling.py   # 主要的拒绝采样实现
├── test/
│   ├── test_rejection.py   # 完整流程测试
│   └── quick_test.py       # 快速测试（单prompt）
├── output/                 # 生成的数据集输出目录
└── README.md              # 本文档
```

## 使用方法

### 1. 基本使用

```bash
cd Test_FILE/verl_internbootcamp/SFT_support
python rejection_sampling.py --input ../flexible_all/train.parquet --output ./output/rejection_sampled.jsonl --limit 100 --batch-size 2
```

### 2. 参数说明

- `--input`: 输入的VERL数据文件（支持parquet或json格式）
- `--output`: 输出的JSONL文件路径
- `--limit`: 限制处理的数据条目数（用于测试）
- `--batch-size`: 批处理大小（默认5）
- `--config`: 配置文件路径（默认使用../config.json）

### 3. 快速测试

运行单个prompt的快速测试：
```bash
cd test
python quick_test.py
```

运行完整流程测试（3个prompts）：
```bash
cd test
python test_rejection.py
```

## 输出格式

生成的JSONL文件每行包含一个JSON对象，格式如下：

```json
{
    "prompt": [...],           // HuggingFace chat格式的prompt
    "response": "...",         // 选中的最佳响应
    "reward": 0.85,           // reward分数（0-1）
    "task_name": "sudoku_4x4", // 任务名称
    "attempts": 8,            // 尝试生成的响应数
    "generation_time": 45.2,  // 生成耗时（秒）
    "timestamp": "...",       // 时间戳
    "data_source": "...",     // 数据来源
    "above_threshold": true   // 是否超过阈值
}
```

## 配置说明

系统使用`../config.json`中的配置，主要包括：

- **LLM配置**：API地址、密钥、模型等
- **采样配置**（在代码中硬编码）：
  - `num_samples`: 8（每个prompt采样次数）
  - `reward_threshold`: 0.5（reward阈值）
  - `max_concurrent_api_calls`: 5（最大并发API调用数）
  - `timeout`: 60（API调用超时时间，秒）

## 注意事项

1. 确保API配置正确且网络连接正常
2. 处理大量数据时建议使用批处理模式
3. 生成的数据会自动append到输出文件，避免数据丢失
4. 如遇到API限流，可调整batch_size和并发数

## 统计信息

运行结束后会显示统计信息：
- 总处理prompt数
- 成功/失败数
- API调用次数
- 平均reward分数
- 超过阈值的比例
- 成功率