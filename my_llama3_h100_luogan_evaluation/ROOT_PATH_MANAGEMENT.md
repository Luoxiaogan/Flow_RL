# 根路径管理系统

## 概述

本系统通过单一配置文件 `configs/root.yaml` 统一管理项目根路径，实现了本地开发和服务器部署环境的无缝切换。

## 核心特性

1. **一处修改，全局生效** - 只需修改 `configs/root.yaml` 即可切换环境
2. **智能路径解析** - Python脚本和Shell脚本都能动态读取根路径
3. **相对路径配置** - 配置文件使用相对路径，提高可移植性
4. **智能配置分析** - 自动计算训练统计信息

## 配置文件

### `configs/root.yaml`
```yaml
# 本地开发
root: "/Users/luogan/Code/workflow_generation/Flow_RL"

# 服务器部署（修改为以下值）
# root: "/nas/ganluo/Flow_RL"
```

## 使用方法

### 1. 切换到服务器环境

编辑 `configs/root.yaml`：
```bash
# 在服务器上
vim configs/root.yaml
# 将 root 改为: /nas/ganluo/Flow_RL
```

### 2. 运行训练脚本

无需修改其他任何文件：
```bash
bash run_finetune_with_inplace_eval.sh
```

## 技术实现

### Python脚本
```python
def get_project_root():
    """从root.yaml获取项目根路径"""
    script_dir = Path(__file__).parent
    root_config_path = script_dir / "configs" / "root.yaml"
    with open(root_config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('root', '/nas/ganluo/Flow_RL')
```

### Shell脚本
```bash
# 从root.yaml读取项目根路径
ROOT=$(python3 "$SCRIPT_DIR/get_root.py" 2>/dev/null)
CONFIG_FILE="$ROOT/New_evaluation_and_RL/config.yaml"
```

## 智能配置分析

系统会自动分析训练数据并计算：
- 训练样本总数
- 全局批次大小
- 每轮步数
- 总训练步数
- 预计评估次数

示例输出：
```
训练数据分析：
  训练样本总数: 50000
  全局批次大小: 128
  每轮步数: 390
  总训练步数: 3900
  预计评估次数: 78
```

## 文件结构

```
my_llama3_h100_luogan_evaluation/
├── configs/
│   ├── root.yaml              # 根路径配置（唯一需要修改的文件）
│   └── evaluation_config.yaml # 使用相对路径
├── get_root.py                # Shell脚本用的辅助工具
├── read_eval_config.py        # 智能配置读取器
└── src/
    └── evaluation/
        └── inplace_evaluation_callback.py # 动态读取根路径
```

## 优势

1. **易于部署** - 服务器上只需修改一个文件
2. **减少错误** - 避免了多处修改可能的遗漏
3. **版本控制友好** - 可以将root.yaml加入.gitignore
4. **智能分析** - 自动计算训练相关统计信息

## 注意事项

- `accelerate_config.yaml` 在运行时动态生成，自动使用正确的路径
- 所有相对路径都相对于根路径进行解析
- 默认使用服务器路径作为后备选项