1 InternBootcamp Tools

`bootcamp_tools.py` 是一个综合工具，用于管理和维护 InternBootcamp 模块。

## 功能

### 1. 修复导入 (--fix-imports)
修复所有 bootcamp 文件中的导入语句，将 `from bootcamp import Basebootcamp` 改为 `from ..base import Basebootcamp`。

```bash
python bootcamp_tools.py --fix-imports
# 或者使用 dry-run 模式预览
python bootcamp_tools.py --fix-imports --dry-run
```

### 2. 生成注册表 (--generate-registry)
扫描所有 bootcamp 文件并生成注册表文件：
- `bootcamp_registry.json` - JSON 格式的注册表
- `bootcamp_registry_generated.py` - Python 代码格式的注册表

```bash
python bootcamp_tools.py --generate-registry
```

### 3. 检查所有模块 (--check-all)
检查所有 bootcamp 模块的错误，包括：
- 导入错误
- 缺失的依赖
- 未实现的必需方法

```bash
python bootcamp_tools.py --check-all
```

结果保存在 `bootcamp_check_results.json`。

### 4. 检查单个模块 (--check)
详细检查指定的 bootcamp 模块。

```bash
python bootcamp_tools.py --check Sudokubootcamp
```

### 5. 列出所有模块 (--list)
列出所有可用的 bootcamp 模块。

```bash
python bootcamp_tools.py --list
```

## 生成的文件

- `bootcamp_registry.json` - 包含所有 bootcamp 类及其模块路径的映射
- `bootcamp_registry_generated.py` - 可以直接复制到 `__init__.py` 中的 Python 代码
- `bootcamp_check_results.json` - 模块检查结果，包含成功、警告和错误信息

## 使用建议

1. 首次使用时，先运行 `--generate-registry` 生成注册表
2. 使用 `--check-all` 检查所有模块的健康状态
3. 对于有问题的模块，使用 `--check MODULE_NAME` 查看详细错误信息
4. 如果需要修复导入问题，运行 `--fix-imports`