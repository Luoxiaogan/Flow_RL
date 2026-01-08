# verl API 文档导读

> **本目录定位**：verl 训练框架的完整 API 参考文档，涵盖数据接口、Reward 系统、训练配置、环境集成等核心模块。

---

## 📚 文档地图

```
verl API 文档体系
├── ⭐ 新任务接入 (核心指南)
│   └── 新任务 RL 训练接入完整指南 → new_task_integration_guide.md
│
├── 基础接口规范 (必读)
│   ├── 数据接口规范 → data_interface.md
│   ├── Reward 接口规范 → reward_interface.md
│   └── 训练配置规范 → training_config.md
│
├── 系统集成 (进阶)
│   ├── 配置与加载机制 → config_and_loading.md
│   └── 环境集成指南 → environment_integration.md
│
└── 案例深度解析 (ToolOrchestra)
    ├── 自定义实现模块 → toolorchestra_custom_implementations.md
    ├── Multi-Turn 逻辑实现 → toolorchestra_multiturn_implementation.md
    ├── generation_quick3.py 详解 → generation_quick3_detailed.md
    └── 上下文维护机制 → context_maintenance_mechanism.md
```

---

## ⭐ 新任务接入必读

### [新任务 RL 训练接入完整指南](new_task_integration_guide.md)

**最重要的文档！** 如果你需要在新任务上进行 RL 训练，这份文档包含了：

- ✅ **完整的修改清单**: 所有需要修改/创建的文件（7-20个文件）
- ✅ **详细的实现步骤**: 分块的实现指南，包含完整示例代码
- ✅ **开发顺序建议**: 从数据准备到最终调试的完整流程
- ✅ **Checklist**: 区分必需和可选的修改点
- ✅ **调试技巧**: 常见问题和解决方案

**阅读时间**: 60-90 分钟
**实施时间**: 1天-2周（取决于任务复杂度）

---

## 🎯 推荐学习路径

### 路径 0: 新任务接入（最常用）

适合：需要在新任务上训练模型的开发者

**直接阅读** → [新任务 RL 训练接入完整指南](new_task_integration_guide.md) ⏱️ 60-90分钟

这个文档整合了下面所有路径的关键内容，并提供了完整的实施方案。

---

### 路径 1: 快速上手（新手）

适合：第一次使用 verl 的开发者

1. **[训练配置规范](training_config.md)** ⏱️ 15分钟
   - 了解 verl 的配置系统
   - 理解 Hydra 配置管理
   - 掌握常用配置项

2. **[数据接口规范](data_interface.md)** ⏱️ 20分钟
   - 准备训练数据（Parquet 格式）
   - 理解必需字段和可选字段
   - 使用 RLHFDataset

3. **[Reward 接口规范](reward_interface.md)** ⏱️ 25分钟
   - 实现 compute_score 函数
   - 理解 RewardManager 架构
   - 掌握 Reward 后处理

---

### 路径 2: 系统集成（进阶）

适合：需要自定义环境或工具的开发者

1. **[配置与加载机制](config_and_loading.md)** ⏱️ 30分钟
   - 理解 verl 如何发现和加载组件
   - 掌握配置文件的层级结构
   - 学习自定义 Tool 的接入方式

2. **[环境集成指南](environment_integration.md)** ⏱️ 45分钟
   - 完整的环境接入流程
   - 数据准备和验证
   - Reward 函数设计
   - 工具配置和注册

---

### 路径 3: 深度理解（专家）

适合：需要深入理解 multi-turn RL 机制的研究者

1. **[ToolOrchestra 自定义实现模块](toolorchestra_custom_implementations.md)** ⏱️ 40分钟
   - 理解 ToolOrchestra 的架构设计
   - 学习自定义 Generation Manager
   - 掌握 multi-turn 训练机制

2. **[Multi-Turn 逻辑实现](toolorchestra_multiturn_implementation.md)** ⏱️ 50分钟
   - 完整的 multi-turn 生成流程
   - 工具调用和执行机制
   - Reward 计算和数据筛选

3. **[generation_quick3.py 详解](generation_quick3_detailed.md)** ⏱️ 60分钟
   - 核心文件的逐行解析
   - 理解每个函数的实现细节
   - 掌握复杂的状态管理

4. **[上下文维护机制](context_maintenance_mechanism.md)** ⏱️ 45分钟
   - 多轮对话的上下文累积策略
   - 长度控制和截断算法
   - 三层上下文管理架构

---

## 📖 文档速查

### ⭐ 新任务接入指南

#### [新任务 RL 训练接入完整指南](new_task_integration_guide.md)

**主题**: 从零开始在新任务上进行 RL 训练的完整实施指南

**核心内容**:
- ✅ 完整的修改清单概览（树形图）
- ✅ 9个部分的详细实施步骤（数据、Reward、配置、Tool、Generation Manager、Trainer、启动脚本、Checklist、调试建议）
- ✅ 每个修改点都包含：文件位置、作用、示例代码、注意事项
- ✅ 区分最小版本（7个文件）和完整版本（15-20个文件）
- ✅ 开发顺序建议、调试技巧、常见问题

**适用场景**:
- 接入全新的任务类型
- 实现 multi-turn RL 训练
- 基于 ToolOrchestra/verl 进行定制开发

**快速导航**:
- 修改清单概览 → 开头
- 数据准备 → 第一部分
- Reward 系统 → 第二部分
- 训练配置 → 第三部分
- Tool 实现 → 第四部分
- Generation Manager → 第五部分
- 完整 Checklist → 第八部分
- 调试技巧 → 第九部分

---

### 基础接口规范

#### [数据接口规范](data_interface.md)

**主题**: 如何准备和实现符合 verl 的数据接口

**核心内容**:
- ✅ Parquet 数据格式要求（prompt, reward_model, data_source）
- ✅ RLHFDataset 的使用和自定义
- ✅ 数据配置参数详解
- ✅ 多轮对话、多模态数据处理

**适用场景**:
- 准备训练数据
- 验证数据格式
- 自定义 Dataset 类

**快速导航**:
- 必需字段 → 第1.2节
- 数据示例 → 第1.4节
- 配置参数 → 第3节
- 常见问题 → 第5节

---

#### [Reward 接口规范](reward_interface.md)

**主题**: 如何实现和配置 Reward 计算系统

**核心内容**:
- ✅ compute_score 函数的签名和返回值
- ✅ RewardManager 的架构和实现
- ✅ 数学题、代码题的 Reward 实现示例
- ✅ Reward 后处理（Length Penalty, KL Penalty）

**适用场景**:
- 实现自定义 Reward 函数
- 理解 Reward 计算流程
- 配置 Reward Manager

**快速导航**:
- 函数签名 → 第2.1节
- 实现示例 → 第3节
- 自定义 RewardManager → 第4.2节
- 调试和测试 → 第7节

---

#### [训练配置规范](training_config.md)

**主题**: verl 训练框架的完整配置系统

**核心内容**:
- ✅ Hydra 配置管理基础
- ✅ 所有配置项的详细说明（data, reward_manager, actor_rollout_ref, algorithm, trainer）
- ✅ 配置模板和示例
- ✅ 命令行覆盖和最佳实践

**适用场景**:
- 创建训练配置文件
- 调整训练超参数
- 优化显存和速度

**快速导航**:
- 配置结构 → 第2节
- 数据配置 → 第3.1节
- 模型配置 → 第3.3节
- 算法配置 → 第3.4节
- 最佳实践 → 第7节

---

### 系统集成

#### [配置与加载机制](config_and_loading.md)

**主题**: verl 如何发现和加载环境、工具、模型

**核心内容**:
- ✅ 配置文件架构（Hydra 多层配置）
- ✅ 环境发现机制（不是"环境路径"，而是"组件路径"）
- ✅ Tool 加载流程（动态导入 + 配置文件）
- ✅ 数据路径配置和 Parquet 格式
- ✅ Generation Manager 配置

**适用场景**:
- 理解 verl 的模块化设计
- 接入自定义 Tool
- 配置工具和环境

**快速导航**:
- 配置架构 → 第1节
- Tool 加载流程 → 第3节
- 数据路径配置 → 第4节
- 自定义环境接入清单 → 第7节

---

#### [环境集成指南](environment_integration.md)

**主题**: 完整的自定义环境接入流程

**核心内容**:
- ✅ verl 训练流程和组件划分
- ✅ 数据准备（Parquet 格式、字段规范）
- ✅ Reward 函数实现（compute_score）
- ✅ Tool 实现和注册
- ✅ 配置文件编写
- ✅ 完整的接入清单

**适用场景**:
- 接入新的任务和环境
- 实现自定义 Tool
- 端到端集成测试

**快速导航**:
- 数据准备 → 第2节
- Reward 实现 → 第3节
- Tool 实现 → 第4节
- 配置文件 → 第5节
- 接入清单 → 第7节

---

### 案例深度解析 (ToolOrchestra)

#### [ToolOrchestra 自定义实现模块](toolorchestra_custom_implementations.md)

**主题**: ToolOrchestra 项目的自定义实现模块详解

**核心内容**:
- ✅ 自定义 Generation Manager (LLMGenerationManager)
- ✅ 自定义 Reward Manager (RewardManager)
- ✅ 自定义 Trainer (GRPORayTrainer)
- ✅ TensorHelper 工具类
- ✅ 与标准 verl 的对比

**适用场景**:
- 实现自定义 Generation Manager
- 理解 multi-turn 训练流程
- 参考复杂项目的架构设计

**快速导航**:
- Generation Manager → 第2节
- Reward Manager → 第3节
- Trainer → 第4节
- 完整流程图 → 第6节

---

#### [Multi-Turn 逻辑实现](toolorchestra_multiturn_implementation.md)

**主题**: ToolOrchestra 的 multi-turn 生成循环完整解析

**核心内容**:
- ✅ multi-turn 核心流程（初始化、循环、终止）
- ✅ 工具调用和执行机制
- ✅ 状态管理（active_mask, 累积上下文）
- ✅ Reward 计算（Outcome + Efficiency + GRPO）
- ✅ QA 和 Function Call 两种任务对比

**适用场景**:
- 理解 multi-turn RL 训练
- 实现复杂的工具调用逻辑
- 设计多轮对话系统

**快速导航**:
- 整体流程图 → 第3节
- 工具调用实现 → 第4节
- Reward 计算 → 第9节
- 关键设计模式 → 第10节

---

#### [generation_quick3.py 详解](generation_quick3_detailed.md)

**主题**: ToolOrchestra 核心文件 generation_quick3.py 的逐行解析

**核心内容**:
- ✅ 文件概览和导入依赖
- ✅ 辅助函数详解（merge_documents, cut_seq, cut_middle_turns）
- ✅ call_tool 工具调用函数（enhance_reasoning, answer, search）
- ✅ LLMGenerationManager 类
- ✅ run_llm_loop 核心方法（600+ 行）
- ✅ Reward 计算细节

**适用场景**:
- 深入理解代码实现
- 调试和修改核心逻辑
- 学习复杂系统的代码组织

**快速导航**:
- 工具调用实现 → 第4节
- LLMGenerationManager → 第5节
- run_llm_loop → 第6节
- 完整执行流程示例 → 第9节

---

#### [上下文维护机制](context_maintenance_mechanism.md)

**主题**: ToolOrchestra 的多轮对话上下文管理策略

**核心内容**:
- ✅ 三层上下文架构（应用层、提示层、张量层）
- ✅ 完整示例：从零到答案的3轮对话
- ✅ 长度控制机制（优先级金字塔、分级截断）
- ✅ 上下文传递路径
- ✅ 关键技巧（文档去重、GPU padding、active mask）

**适用场景**:
- 设计 multi-turn 上下文管理
- 理解长度控制策略
- 优化 prompt 构建

**快速导航**:
- 三层架构 → 第2节
- 完整示例 → 第3节
- 长度控制 → 第4节
- 关键技巧 → 第7节

---

## 🔍 按主题查找

### 新任务接入
- ⭐ **[新任务 RL 训练接入完整指南](new_task_integration_guide.md)** - **必读！完整的实施方案**
- 📄 [环境集成指南](environment_integration.md) - 环境接入流程概述

### 数据相关
- 📄 [新任务接入指南 - 数据准备部分](new_task_integration_guide.md#第一部分数据准备必需)
- 📄 [数据接口规范](data_interface.md) - 数据格式、Dataset 实现
- 📄 [配置与加载机制](config_and_loading.md) - 数据路径配置、Parquet 加载
- 📄 [环境集成指南](environment_integration.md) - 数据准备流程

### Reward 相关
- 📄 [新任务接入指南 - Reward 部分](new_task_integration_guide.md#第二部分reward-系统必需)
- 📄 [Reward 接口规范](reward_interface.md) - Reward 函数实现、RewardManager
- 📄 [环境集成指南](environment_integration.md) - 自定义 Reward 设计
- 📄 [ToolOrchestra 自定义实现](toolorchestra_custom_implementations.md) - Reward Manager 案例

### 配置相关
- 📄 [新任务接入指南 - 配置部分](new_task_integration_guide.md#第三部分训练配置必需)
- 📄 [训练配置规范](training_config.md) - 完整配置参数
- 📄 [配置与加载机制](config_and_loading.md) - 配置系统架构
- 📄 [环境集成指南](environment_integration.md) - 配置文件编写

### Multi-Turn 相关
- 📄 [新任务接入指南 - Generation Manager 部分](new_task_integration_guide.md#第五部分generation-manager可选)
- 📄 [Multi-Turn 逻辑实现](toolorchestra_multiturn_implementation.md) - 完整流程
- 📄 [generation_quick3.py 详解](generation_quick3_detailed.md) - 代码实现
- 📄 [上下文维护机制](context_maintenance_mechanism.md) - 上下文管理

### 工具相关
- 📄 [新任务接入指南 - Tool 部分](new_task_integration_guide.md#第四部分tool-实现multi-turn-可选)
- 📄 [配置与加载机制](config_and_loading.md) - Tool 加载流程
- 📄 [环境集成指南](environment_integration.md) - Tool 实现和注册
- 📄 [Multi-Turn 逻辑实现](toolorchestra_multiturn_implementation.md) - 工具调用机制

---

## ⚡ 快速解决常见问题

### Q0: 我需要在新任务上训练模型，需要改哪些文件？

**答案**: → [新任务 RL 训练接入完整指南](new_task_integration_guide.md)

这是最常见的问题！这份指南包含了：
- 完整的文件清单（7-20个文件）
- 每个文件的详细实现步骤
- 完整的示例代码
- 开发顺序和调试技巧

---

### Q1: 如何准备训练数据？

**答案**: → [新任务接入指南 - 数据准备](new_task_integration_guide.md#第一部分数据准备必需) 或 [数据接口规范](data_interface.md) 第4节

关键步骤：
1. 准备 Parquet 文件（包含 prompt, reward_model, data_source 字段）
2. 验证数据格式
3. 测试 Dataset 加载

```python
import pandas as pd

data = [{
    "prompt": [{"role": "user", "content": "问题"}],
    "reward_model": {"ground_truth": "答案"},
    "data_source": "your_task"
}]

df = pd.DataFrame(data)
df.to_parquet("train.parquet", index=False)
```

---

### Q2: 如何实现自定义 Reward 函数？

**答案**: → [新任务接入指南 - Reward 系统](new_task_integration_guide.md#第二部分reward-系统必需) 或 [Reward 接口规范](reward_interface.md) 第3节

关键接口：
```python
def compute_score(data_source, solution_str, ground_truth, extra_info=None, **kwargs):
    # 实现你的评分逻辑
    if is_correct(solution_str, ground_truth):
        return 1.0
    else:
        return 0.0
```

---

### Q3: 如何配置 multi-turn 训练？

**答案**: → [新任务接入指南 - 训练配置](new_task_integration_guide.md#第三部分训练配置必需) 或 [训练配置规范](training_config.md) 第3.3节

关键配置：
```yaml
actor_rollout_ref:
  rollout:
    multi_turn:
      enable: True
      max_turns: 5
      tool_config_path: "./config/tool_config/your_tool.yaml"
```

---

### Q4: 如何接入自定义 Tool？

**答案**: → [新任务接入指南 - Tool 实现](new_task_integration_guide.md#第四部分tool-实现multi-turn-可选) 或 [配置与加载机制](config_and_loading.md) 第7节

关键步骤：
1. 实现 Tool 类（继承 BaseTool）
2. 编写 tool_config.yaml
3. 在配置中指定 tool_config_path

---

### Q5: 如何控制多轮对话的上下文长度？

**答案**: → [上下文维护机制](context_maintenance_mechanism.md) 第4节

关键机制：
- 优先级金字塔（Problem > Code > Attempts > Documents）
- 分级截断（从低优先级开始）
- Token 级精确控制

---

## 🛠️ 开发指南

### 新任务接入 Checklist

**完整清单**: → [新任务接入指南 - Checklist](new_task_integration_guide.md#第八部分完整-checklist)

**最小版本** (7个文件，1-2天):
- [ ] 数据预处理脚本
- [ ] Parquet 数据文件
- [ ] Reward 计分函数
- [ ] Reward 注册
- [ ] 主配置文件
- [ ] 启动脚本
- [ ] 数据验证

**完整版本** (15-20个文件，1-2周):
- [ ] 上述最小版本
- [ ] Tool 配置文件
- [ ] Tool 类实现
- [ ] Tool 注册
- [ ] 自定义 Generation Manager
- [ ] 上下文管理逻辑
- [ ] 自定义 Trainer (可选)
- [ ] 评估脚本

详细流程：→ [新任务 RL 训练接入完整指南](new_task_integration_guide.md)

---

### 调试技巧

**完整调试指南**: → [新任务接入指南 - 调试建议](new_task_integration_guide.md#第九部分开发和调试建议)

#### 数据问题
- 使用 [新任务接入指南 - 数据调试](new_task_integration_guide.md#数据调试) 的验证代码
- 或参考 [数据接口规范](data_interface.md) 第4.2节的验证脚本

#### Reward 问题
- 使用 [新任务接入指南 - Reward 调试](new_task_integration_guide.md#reward-调试) 的测试代码
- 或参考 [Reward 接口规范](reward_interface.md) 第7.1节的测试脚本

#### 配置问题
- 参考 [新任务接入指南 - 配置调试](new_task_integration_guide.md#配置调试)
- 使用 `--cfg job` 打印完整配置

#### Multi-Turn 问题
- 参考 [新任务接入指南 - 端到端调试](new_task_integration_guide.md#端到端调试)
- 阅读 [上下文维护机制](context_maintenance_mechanism.md)

---

## 📚 参考项目

### ToolOrchestra

一个基于 verl 的 multi-turn RL 训练系统，支持工具调用和推理。

**相关文档**:
- [自定义实现模块](toolorchestra_custom_implementations.md)
- [Multi-Turn 逻辑实现](toolorchestra_multiturn_implementation.md)
- [generation_quick3.py 详解](generation_quick3_detailed.md)
- [上下文维护机制](context_maintenance_mechanism.md)

**代码位置**: `.reference_projects/ToolOrchestra/training/`

**特点**:
- ✅ 支持 QA 和 Function Call 两种任务
- ✅ 异步并行工具调用
- ✅ 动态上下文管理
- ✅ Preference-based Reward

---

## 💡 学习建议

### 需要在新任务上训练模型？⭐
**直接阅读** → [新任务 RL 训练接入完整指南](new_task_integration_guide.md)

这是 **最重要的文档**，包含完整的实施方案，无需阅读其他文档即可完成接入。

### 第一次使用 verl？
建议先阅读 [新任务接入指南](new_task_integration_guide.md)，然后按需参考 **路径 1: 快速上手** 的文档。

### 需要深入理解某个模块？
建议先完成新任务接入，有实际经验后，再按照 **路径 2/3** 深入学习。

### 遇到问题？
1. 首先查看 [新任务接入指南 - 常见问题](new_task_integration_guide.md#93-常见问题)
2. 然后使用 **按主题查找** 或 **快速解决常见问题** 找到相关文档

---

## 📝 文档维护

### 文档版本
- **创建日期**: 2026-01-08
- **最后更新**: 2026-01-08
- **维护者**: Claude Code

### 贡献指南
- 发现文档问题？请提交 Issue
- 有改进建议？欢迎 Pull Request
- 需要新增主题？在 `PROJECT_TODO.md` 中提出

---

## 🔗 相关资源

### 外部文档
- [verl 官方文档](https://github.com/volcengine/verl)
- [Hydra 配置框架](https://hydra.cc/)
- [GRPO 论文](https://arxiv.org/abs/2402.03300)

### 项目文档
- [项目 TODO](../PROJECT_TODO.md)
- [设计文档](../design/)
- [实现细节](../implementation/)

---

**Happy Training! 🚀**
