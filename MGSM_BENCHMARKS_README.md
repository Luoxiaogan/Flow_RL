# MGSM Benchmarks 实施说明

## 📌 概述

成功添加了两个新的MGSM (Multilingual Grade School Math) benchmark:
- **mgsmbn**: 孟加拉语版本的GSM8K数学问题（注意：benchmark名称无下划线）
- **mgsmde**: 德语版本的GSM8K数学问题（注意：benchmark名称无下划线）

这些是GSM8K的多语言版本，包含相同难度的小学数学应用题，只是使用不同的语言表述。

## 🗂️ 实现文件结构

```
ScoreFlow/
├── scripts/
│   ├── mgsmbn/
│   │   ├── handler.py       # 孟加拉语数据处理器
│   │   └── conditions.py    # 孟加拉语提示模板
│   └── mgsmde/
│       ├── handler.py       # 德语数据处理器
│       └── conditions.py    # 德语提示模板
└── benchmark_mapping.jsonl  # 已更新，包含新benchmark注册

Processed_dataset/
├── mgsm_bn/
│   ├── mgsm_bn_train.jsonl  # 训练数据
│   └── mgsm_bn_test.jsonl   # 测试数据
└── mgsm_de/
    ├── mgsm_de_train.jsonl  # 训练数据
    └── mgsm_de_test.jsonl   # 测试数据
```

## 🚀 使用方法

### 1. 在workflow系统中使用

修改 `run_workflow_system.sh` 中的BENCHMARK变量：

```bash
# 使用孟加拉语版本
BENCHMARK="mgsmbn"

# 或使用德语版本
BENCHMARK="mgsmde"
```

然后运行：
```bash
bash run_workflow_system.sh
```

### 2. 在Python代码中直接使用

```python
# 孟加拉语版本
from ScoreFlow.scripts.mgsmbn.handler import MgsmbnHandler

handler = MgsmbnHandler(dataset_path="Processed_dataset/mgsm_bn/mgsm_bn_test.jsonl")
prompt = handler.get_prompt_text([0, 1, 2])  # 获取前3个问题
```

```python
# 德语版本
from ScoreFlow.scripts.mgsmde.handler import MgsmdeHandler

handler = MgsmdeHandler(dataset_path="Processed_dataset/mgsm_de/mgsm_de_test.jsonl")
prompt = handler.get_prompt_text([0, 1, 2])  # 获取前3个问题
```

## ✅ 验证状态

- ✅ 数据加载功能正常
- ✅ 提示生成功能正常
- ✅ 验证数据获取正常
- ✅ conditions.py包含所有必需变量
- ✅ 语言特定内容正确配置
- ✅ benchmark_mapping.jsonl已更新

## 📊 数据集信息

### MGSM Bengali (mgsmbn)
- 语言：孟加拉语 (বাংলা)
- 测试集大小：50个问题
- 答案类型：数值答案

### MGSM German (mgsmde)
- 语言：德语 (Deutsch)
- 测试集大小：50个问题
- 答案类型：数值答案

## 🔍 实现特点

1. **完全复用GSM8K逻辑**：由于MGSM是GSM8K的多语言版本，处理逻辑完全相同
2. **语言无关的数学推理**：虽然问题语言不同，但数学推理过程是通用的
3. **LLM智能判断**：使用基类的LLM judge功能，能够理解不同语言的数学问题

## 📝 注意事项

1. **字符编码**：在Windows环境下显示非ASCII字符可能有编码问题，但不影响实际运行
2. **LLM能力**：确保使用的LLM模型支持相应的语言（孟加拉语/德语）
3. **数据格式**：数据格式与GSM8K完全一致，包含question和answer字段

## 🧪 测试验证

运行验证脚本：
```bash
python verify_mgsm.py
```

输出应显示：
```
[PASSED] mgsmbn is ready to use!
[PASSED] mgsmde is ready to use!
[SUCCESS] Both MGSM benchmarks are ready!
```

## 🎯 下一步

1. 可以继续添加其他语言版本的MGSM（如法语、西班牙语等）
2. 可以在veRL训练中使用这些多语言数据集
3. 可以进行跨语言的性能对比分析

---

**实施日期**: 2025-01-06  
**实施者**: Claude Code Assistant  
**状态**: ✅ 完成并验证