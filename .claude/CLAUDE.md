# Claude Code 项目规范 - 通用模板

## 📁 目录结构规范

### 核心原则
- **简洁优先**: 避免过度嵌套，目录深度不超过3层
- **功能导向**: 按功能模块组织，而非按技术栈分类
- **稳定结构**: 目录结构一旦确定，尽量保持稳定

### 标准目录结构

```
Flow_RL_refactor/
├── src/                       # 核心源代码（模块化设计，便于复用和测试）
├── scripts/                   # 运行脚本（启动、部署、数据处理等）
├── configs/                   # 配置文件（json/yaml/toml）
├── data/                      # 数据存储（输入数据、处理后数据）
├── outputs/                   # 输出结果（生成物、报告、模型等）
├── logs/                      # 日志文件（按模块和时间组织）
├── tests/                     # 测试代码（pytest 单元测试与集成测试）
├── docs/                      # 项目文档
├── demo/                      # 示例代码和使用演示
├── notebooks/                 # Jupyter Notebook（分析报告、可视化）
├── experiments/               # 实验配置（可复现实验的参数快照）
└── tmp/                       # 临时文件（即用即删，git忽略）
```

### 目录职责说明

| 目录 | 职责 | 注意事项 |
|------|------|---------|
| `src/` | 核心业务逻辑、算法实现 | 模块化设计，高内聚低耦合 |
| `scripts/` | 调用src的运行脚本 | 仅做参数传递和流程控制，不含复杂逻辑 |
| `configs/` | 所有配置参数 | 支持环境区分（dev/prod） |
| `tests/` | 单元测试和集成测试 | 覆盖核心功能，CI必须通过 |
| `tmp/` | 临时调试文件 | **必须在.gitignore中**，用完即删 |

### 临时文件管理

**`tmp/` 目录规范**:
- ✅ 快速验证功能、调试代码片段、一次性测试
- ❌ 正式测试 → `tests/`
- ❌ 示例代码 → `demo/`
- ❌ 任何需要保留的文件

**强制要求**:
```bash
# .gitignore 必须包含
tmp/
*.tmp
*.temp
```

---

## 🚨 核心编程原则

### 八荣八耻

| 以...为耻 | 以...为荣 | 说明 |
|-----------|-----------|------|
| 暗猜接口 | 认真查阅 | 禁止臆测API行为，必须查阅文档/源码确认 |
| 模糊执行 | 寻求确认 | 不确定的实现先向用户确认 |
| 默认忽略 | 主动报告 | 异常、警告、错误必须报告，不得静默忽略 |
| 隐式假设 | 显式验证 | 所有假设必须通过代码验证 |
| 随意修改 | 谨慎调试 | 修改前必须理解原理，禁止试错式编程 |
| 表面应付 | 深入理解 | 解决问题必须找到根因，禁止表面修补 |
| 复制粘贴 | 原创思考 | 理解每行代码含义，禁止盲目复制 |
| 孤立开发 | 协同沟通 | 主动汇报进度和问题 |

---

## 🔥 命名规范

### 禁用命名模式

**严格禁止以下前缀/后缀**:
```
❌ enhanced_* / *_enhanced
❌ integrated_* / *_integrated  
❌ cleaned_* / *_cleaned / *_clean
❌ improved_* / *_improved
❌ optimized_* / *_optimized
❌ advanced_* / *_advanced
❌ *_v2 / *_v3 / *_new / *_old / *_temp / *_final
```

### 正确命名原则

```bash
# ❌ 错误
enhanced_data_processor.py
train_model_integrated.py
utils_clean.py
config_v2.yaml

# ✅ 正确
data_processor.py          # 功能导向
train_model.py             # 简洁明确
utils.py                   # 无冗余修饰
config.yaml                # 使用版本控制而非文件名
```

**命名规则**:
- 使用 `snake_case`（Python）或项目约定的命名风格
- 文件名直接描述功能，不加形容词修饰
- 版本管理交给 Git，不要在文件名中体现

---

## 🛡️ 错误处理规范

### 核心原则：让错误暴露，不要掩盖

```python
# ❌ 严格禁止：静默fallback
try:
    result = risky_operation()
except Exception:
    result = default_value  # 掩盖了问题！

# ❌ 严格禁止：hasattr降级
if hasattr(obj, 'attr'):
    return obj.attr
else:
    return fallback  # 隐藏了设计问题！

# ✅ 正确做法：让错误自然抛出
result = risky_operation()  # 失败时显示完整traceback
value = obj.attr            # 缺失时明确报错
```

**为什么**:
- 错误暴露 = 问题可发现 = 可从根本解决
- 静默处理 = 问题隐藏 = 积累技术债务

**唯一例外**: 明确的业务逻辑需要降级处理，且必须记录日志。

---

## 📚 模块文档规范

### 模块头部模板

每个 Python 模块**必须**在文件开头包含标准文档头：

```python
"""
[模块功能一句话描述]

Documentation:
    Interface: docs/modules/[module_name].md
    Evolution: docs/modules/evolution/[module_name]_evolution.md
    Deprecated: docs/deprecated/deprecated_[module_name].md

Key Features:
    - Feature 1: Brief description
    - Feature 2: Brief description

Dependencies:
    - dependency_a: Why needed
    - dependency_b: Why needed

Example:
    >>> from module import MainClass
    >>> obj = MainClass(config)
    >>> result = obj.process(data)
"""
```

### 文档目录结构

```
docs/
├── modules/                           # 模块接口文档
│   ├── module_a.md
│   ├── module_b.md
│   └── evolution/                     # 演进历史
│       ├── module_a_evolution.md
│       └── module_b_evolution.md
├── deprecated/                        # 废弃功能
│   ├── DEPRECATED_INDEX.md           # 废弃组件索引
│   ├── deprecated_module_a.md
│   └── deprecated_module_b.md
└── design/                           # 设计文档
    └── architecture.md
```

---

## 🔧 脚本与模块分离

### 复杂度控制

| 代码位置 | 行数上限 | 职责 |
|---------|---------|------|
| `scripts/` | ≤50行 | 参数传递、流程控制、调用src |
| `src/` | 无限制 | 核心逻辑、算法、数据处理 |

### 分离原则

```bash
# ❌ 错误：脚本内嵌复杂逻辑
scripts/run_task.sh:
    python -c "
    # 100行复杂代码...
    "

# ✅ 正确：逻辑在模块，脚本仅调用
src/task/runner.py:
    class TaskRunner: ...

scripts/run_task.sh:
    python -m src.task.runner --config "$1"
```

### 决策标准

- **集成到一个文件**: 功能高度相关 + 配置一致
- **分离为独立模块**: 可复用 + 独立测试 + 超过50行

---

## 📋 文档管理生命周期

### 新增模块时

```bash
# 1. 创建代码
src/new_module/

# 2. 同步创建文档（必须）
docs/modules/new_module.md
docs/modules/evolution/new_module_evolution.md
docs/deprecated/deprecated_new_module.md
```

### 废弃功能时

```python
# 1. 代码添加警告
import warnings

def old_function():
    warnings.warn(
        "old_function() deprecated since v2.0, removed in v3.0. "
        "Use new_function() instead. "
        "See docs/deprecated/deprecated_xxx.md",
        DeprecationWarning,
        stacklevel=2
    )
```

```bash
# 2. 移动到deprecated目录
mv src/module/old.py src/deprecated/v2/old.py

# 3. 更新废弃文档
docs/deprecated/deprecated_xxx.md
```

### 完全移除时

```bash
# 1. 确认无依赖
grep -r "old_function" src/

# 2. 删除代码
rm src/deprecated/v2/old.py

# 3. 归档文档
mv docs/deprecated/deprecated_xxx.md docs/deprecated/archive/
```

---

## 📝 TODO 管理

### 文件位置
`docs/PROJECT_TODO.md`

### 优先级定义

| 级别 | 含义 | 响应时间 |
|------|------|---------|
| P0 | 阻塞开发/严重bug | 立即处理 |
| P1 | 新功能/重构/优化 | 本周内 |
| P2 | 代码清理/文档补充 | 本月内 |

### 模板

```markdown
# Project TODO

## 🔥 P0 - 紧急
- [ ] **[模块]**: 任务描述
  - 负责人: @xxx
  - 截止: YYYY-MM-DD

## 🎯 P1 - 重要
- [ ] **[模块]**: 任务描述

## 📋 P2 - 常规
- [ ] **[模块]**: 任务描述

## ✅ 已完成 (本周)
- [x] **[模块]**: 任务描述 (完成: YYYY-MM-DD, commit: abc123)
```

### 工作流

1. **会话开始**: 查看 P0/P1 任务
2. **会话中**: 使用 Claude Code TodoWrite 工具
3. **会话结束**: 更新 PROJECT_TODO.md，标记完成项

---

## ✅ 提交前检查清单

### 代码规范
- [ ] 无禁用命名模式（enhanced_/v2/等）
- [ ] 无静默错误处理（try-except fallback）
- [ ] 模块头部包含标准文档引用
- [ ] 脚本行数 ≤50，复杂逻辑在 src/

### 文件管理
- [ ] tmp/ 目录已清空
- [ ] 新文件放在正确目录
- [ ] .gitignore 包含 tmp/

### 文档同步
- [ ] 新模块有对应文档
- [ ] 接口变更已记录演进历史
- [ ] 废弃功能已标记并记录

### TODO 更新
- [ ] PROJECT_TODO.md 已更新
- [ ] 完成项标记 commit hash

---

## 🎯 快速参考

```
目录选择:
  核心逻辑 → src/
  运行脚本 → scripts/
  配置文件 → configs/
  测试代码 → tests/
  临时调试 → tmp/ (用完删除)

命名检查:
  ❌ enhanced_ improved_ clean_ v2 new old temp
  ✅ 功能导向、简洁明确、snake_case

错误处理:
  ❌ try-except fallback
  ✅ 让错误暴露，显示traceback

文档同步:
  新模块 → 同步创建 docs/modules/xxx.md
  改接口 → 更新 evolution/xxx_evolution.md
  废弃时 → 记录 deprecated/deprecated_xxx.md
```

---

*模板版本: 1.0*
*适用于: Claude Code 项目协作*