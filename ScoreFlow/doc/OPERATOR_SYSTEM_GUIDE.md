# ScoreFlow Dynamic Operator System User Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [System Architecture](#system-architecture)
- [Using the CLI Tool](#using-the-cli-tool)
- [Creating Custom Operator Groups](#creating-custom-operator-groups)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Overview

The ScoreFlow Dynamic Operator System allows you to:
- 🔄 **Switch operator combinations** for different benchmarks
- 📦 **Clone benchmarks** with custom operator groups
- 🎯 **Optimize workflows** by selecting appropriate operators
- 🚀 **Reduce code duplication** through shared templates

### Key Benefits
1. **Flexibility**: Mix and match operators for different problem domains
2. **Reusability**: Common code is centralized in base templates
3. **Extensibility**: Easy to add new operators and groups
4. **Maintainability**: Configuration-driven approach separates logic from implementation

## Quick Start

### 1. Test the System
```bash
cd ScoreFlow/tools
python test_system.py
```

### 2. List Available Operator Groups
```bash
python cli.py list-groups
```

### 3. Clone a Benchmark with a New Operator Group
```bash
# Create gsm8k variant with reasoning-heavy operators
python cli.py clone -s gsm8k -t gsm8k_reasoning -g reasoning_heavy

# Create mbpp variant with code-focused operators  
python cli.py clone -s mbpp -t mbpp_code -g code_focused
```

### 4. Run the New Benchmark
```bash
cd ../..  # Back to Flow_RL root
bash run_workflow_system.sh --benchmark gsm8k_reasoning
```

## System Architecture

### File Structure
```
ScoreFlow/
├── config/
│   ├── operator_registry.csv      # Operator definitions
│   └── operator_groups.yaml       # Group configurations
├── scripts/
│   ├── common/
│   │   ├── base_conditions.py     # Shared templates
│   │   ├── operator_loader.py     # Dynamic loading
│   │   └── prompt_builder.py      # Prompt generation
│   └── [benchmarks]/              # Individual benchmarks
├── tools/
│   ├── cli.py                     # Command-line interface
│   ├── benchmark_cloner.py        # Cloning utility
│   └── test_system.py            # System tests
```

### Operator Groups

| Group Name | Description | Operators |
|------------|-------------|-----------|
| `default` | Standard 4-operator set | Generate, Revise, Summarize, Ensemble |
| `extended` | All general-purpose operators | Default + CodeGenerate, Decompose, FormatAnswer |
| `reasoning_heavy` | Complex reasoning tasks | Generate, Decompose, Revise, Summarize, Ensemble, FormatAnswer |
| `code_focused` | Programming problems | Generate, CodeGenerate, Revise, Ensemble |
| `math_specialized` | MATH benchmark specific | Custom, Review, Programmer, ScEnsemble |
| `minimal` | Bare minimum | Generate, Revise |

## Using the CLI Tool

### Basic Commands

#### List all operator groups
```bash
python cli.py list-groups
python cli.py list-groups -v  # Verbose output
```

#### Show details of a specific group
```bash
python cli.py show-group default
python cli.py show-group reasoning_heavy
```

#### List all operators
```bash
python cli.py list-operators
python cli.py list-operators --category core
python cli.py list-operators --benchmark gsm8k
```

#### List all benchmarks
```bash
python cli.py list-benchmarks
python cli.py list-benchmarks -v  # Show details
```

#### Clone a benchmark
```bash
python cli.py clone \
    --source gsm8k \
    --target gsm8k_custom \
    --operator-group extended \
    --train-data /path/to/train.jsonl \
    --test-data /path/to/test.jsonl
```

#### Validate operator compatibility
```bash
python cli.py validate -g code_focused -b mbpp
```

### Advanced Clone Options

```bash
# Force overwrite existing benchmark
python cli.py clone -s gsm8k -t gsm8k_test -g default --force

# Clone with custom dataset paths
python cli.py clone \
    -s mbpp \
    -t mbpp_custom \
    -g code_focused \
    --train-data /custom/path/train.jsonl \
    --test-data /custom/path/test.jsonl
```

## Creating Custom Operator Groups

### Step 1: Edit operator_groups.yaml
```yaml
# Add to ScoreFlow/config/operator_groups.yaml
custom_group:
  name: "My Custom Group"
  description: "Custom operator combination for specific tasks"
  module: "common.operator"
  operators:
    - Generate
    - Decompose
    - CodeGenerate
    - Ensemble
```

### Step 2: Test the New Group
```bash
python cli.py show-group custom_group
python cli.py validate -g custom_group -b gsm8k
```

### Step 3: Use the Group
```bash
python cli.py clone -s gsm8k -t gsm8k_custom -g custom_group
```

## Advanced Usage

### Adding New Operators

1. **Register in operator_registry.csv**:
```csv
MyOperator,common.operator,MyOperator,"instruction: str, context: str",My custom operator,custom,all,"operator.MyOperator(self.llm, self.problem_text)","Custom operation description"
```

2. **Implement the operator class** in appropriate module

3. **Add to operator groups** as needed

### Mixed Module Groups

For groups using operators from different modules:

```yaml
hybrid_group:
  name: "Hybrid Group"
  description: "Mix of common and specialized operators"
  module: "mixed"  # Special flag for mixed modules
  operators:
    - Generate      # from common.operator
    - Programmer    # from MATH.operator
    - Ensemble      # from common.operator
```

### Customizing Generated Conditions

After cloning, you can manually edit the generated `conditions.py`:

1. **Adjust TASK_PROMPT** for domain-specific descriptions
2. **Modify operator instructions** in START_PROMPT
3. **Add custom initialization** in OPERATOR_INIT_CODE

## Troubleshooting

### Common Issues

#### "Operator group not found"
- Check available groups: `python cli.py list-groups`
- Verify spelling in command

#### "Operator does not support benchmark"
- Use `python cli.py validate -g [group] -b [benchmark]`
- Check operator support: `python cli.py list-operators -b [benchmark]`

#### "Target directory already exists"
- Use `--force` flag to overwrite
- Or choose a different target name

### Testing Components

```bash
# Test operator registry
python -c "from ScoreFlow.scripts.common.operator_loader import OperatorRegistry; r = OperatorRegistry(); print(f'Loaded {len(r.operators)} operators')"

# Test prompt builder
python -c "from ScoreFlow.scripts.common.prompt_builder import DynamicPromptBuilder; b = DynamicPromptBuilder('test', 'default'); print('Builder created successfully')"

# Run full system test
python test_system.py
```

### Debug Mode

Enable debug output:
```bash
DEBUG=1 python cli.py clone -s gsm8k -t test -g default
```

## Best Practices

1. **Always test after cloning**: Run a small test to verify the new benchmark works
2. **Review generated conditions**: Check that operator descriptions match your needs
3. **Use appropriate groups**: Select operator groups that match the problem domain
4. **Document custom groups**: Add clear descriptions when creating new groups
5. **Backup before modifying**: Keep copies of working configurations

## Examples

### Example 1: Create Math-Heavy GSM8K
```bash
# Clone with reasoning operators
python cli.py clone -s gsm8k -t gsm8k_math -g reasoning_heavy

# Test with a small batch
cd ../..
bash run_workflow_system.sh --benchmark gsm8k_math --generation-tasks "0-2"
```

### Example 2: Create Minimal MBPP for Testing
```bash
# Clone with minimal operators for faster testing
python cli.py clone -s mbpp -t mbpp_minimal -g minimal

# Verify the setup
python cli.py show-group minimal
python cli.py list-benchmarks | grep mbpp_minimal
```

### Example 3: Create Custom Hybrid Benchmark
```bash
# First, add custom group to operator_groups.yaml
# Then clone
python cli.py clone -s high_level_math -t math_hybrid -g hybrid_math

# Validate compatibility
python cli.py validate -g hybrid_math -b math_hybrid
```

## Support

For issues or questions:
1. Check this guide and troubleshooting section
2. Run `python test_system.py` to verify system integrity
3. Review generated files in `ScoreFlow/scripts/[your_benchmark]/`
4. Check logs in `workspace*/` directories after running workflows

---

**Version**: 1.0
**Last Updated**: 2024
**System Requirements**: Python 3.7+, PyYAML