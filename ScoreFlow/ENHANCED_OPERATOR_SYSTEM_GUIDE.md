# Enhanced Dynamic Operator System with Split Prompt Structure

## 📌 Overview

The Enhanced Dynamic Operator System now fully supports the original ScoreFlow split prompt structure, allowing for more modular and maintainable prompt generation while maintaining complete backward compatibility.

## 🔑 Key Improvements

### 1. Split Prompt Structure Support

The system now generates conditions.py with properly split prompt components:

- **TASK_PROMPT**: Domain-specific task description
- **OPERATOR_PROMPT_PART_1**: Basic operator descriptions
- **OPERATOR_PROMPT_PART_2**: Parameter explanations and design principles  
- **USER_PROMPT_LONG**: User task instructions and template
- **SYSTEM_PROMPT**: System-level instructions
- **START_PROMPT**: Combined prompt for backward compatibility
- **PYTHON_START/END**: Code wrapper templates

### 2. Structure Types

The system identifies and supports three structure types:

| Type | Description | Variables |
|------|-------------|-----------|
| **Split** | Modern modular structure | OPERATOR_PROMPT_PART_1/2, USER_PROMPT_LONG |
| **Legacy** | Traditional single prompt | START_PROMPT only |
| **Hybrid** | Both structures (compatible) | All variables present |

### 3. Enhanced Components

#### prompt_builder_v2.py
- `EnhancedPromptBuilder`: Generates split prompt structure
- Separate methods for each prompt component
- Dynamic operator initialization based on group
- Full backward compatibility support

#### benchmark_cloner_v2.py
- `EnhancedBenchmarkCloner`: Creates benchmarks with split structure
- `use_split_structure` parameter for structure selection
- Automatic TASK_PROMPT extraction from source
- Structure analysis capabilities

## 📚 Usage Guide

### Creating a New Benchmark with Split Structure

```python
from ScoreFlow.tools.benchmark_cloner_v2 import EnhancedBenchmarkCloner

cloner = EnhancedBenchmarkCloner()
cloner.clone_benchmark(
    source_benchmark='gsm8k',
    target_benchmark='gsm8k_advanced',
    operator_group='reasoning_heavy',
    use_split_structure=True  # Use modern split structure
)
```

### Creating with Legacy Structure (Backward Compatible)

```python
cloner.clone_benchmark(
    source_benchmark='gsm8k',
    target_benchmark='gsm8k_simple',
    operator_group='default',
    use_split_structure=False  # Use legacy single START_PROMPT
)
```

### Analyzing Benchmark Structure

```python
# Analyze a single benchmark
analysis = cloner.analyze_benchmark_structure('gsm8k')
print(f"Structure type: {analysis['structure_type']}")
print(f"Variables: {analysis['prompt_variables']}")

# Analyze all benchmarks
from benchmark_cloner_v2 import analyze_all_benchmarks
analyze_all_benchmarks()
```

## 🔧 Integration with workflow_generator.py

The updated workflow_generator.py now correctly loads split prompts:

```python
def _load_prompt_templates(self):
    conditions_module = importlib.import_module(f"ScoreFlow.scripts.{self.benchmark_name}.conditions")
    return (
        getattr(conditions_module, "SYSTEM_PROMPT", "..."),
        getattr(conditions_module, "TASK_PROMPT", ""),
        getattr(conditions_module, "OPERATOR_PROMPT_PART_1", ""),
        getattr(conditions_module, "OPERATOR_PROMPT_PART_2", ""),
        getattr(conditions_module, "USER_PROMPT_LONG", ""),
    )
```

The prompts are then properly combined in `_construct_generation_prompt()`.

## 🎯 Generated File Structure

### Split Structure (Modern)
```python
# conditions.py with split structure
TASK_PROMPT = '''..domain description..'''
OPERATOR_PROMPT_PART_1 = '''..operator basics..'''
OPERATOR_PROMPT_PART_2 = '''..parameters & principles..'''
USER_PROMPT_LONG = '''..task instructions..'''
SYSTEM_PROMPT = '''..system prompt..'''
START_PROMPT = OPERATOR_PROMPT_PART_1 + OPERATOR_PROMPT_PART_2 + USER_PROMPT_LONG  # Compatibility
PYTHON_START = '''..imports..'''
PYTHON_END = '''..wrapper..'''
```

### Legacy Structure (Backward Compatible)
```python
# conditions.py with legacy structure
TASK_PROMPT = '''..domain description..'''
START_PROMPT = '''..all operator content combined..'''
SYSTEM_PROMPT = '''..system prompt..'''
PYTHON_START = '''..imports..'''
PYTHON_END = '''..wrapper..'''
```

## 📊 Current System Status

Based on analysis of all benchmarks:
- **5 benchmarks** use split structure (gsm8k, mbpp, drop, hotpotqa, humaneval)
- **14 benchmarks** use legacy structure
- **1 benchmark** uses hybrid structure (gsm8k_reasoning_v2)

## ✅ Testing

Run the comprehensive test suite:

```bash
# Test enhanced system with split structure
python ScoreFlow/tools/test_enhanced_system.py

# Test original system (still works)
python ScoreFlow/tools/test_system.py
```

## 🚀 Quick Start Examples

### Example 1: Create Math Benchmark with Extended Operators
```bash
cd ScoreFlow/tools
python -c "
from benchmark_cloner_v2 import EnhancedBenchmarkCloner
cloner = EnhancedBenchmarkCloner()
cloner.clone_benchmark('gsm8k', 'gsm8k_extended', 'extended', use_split_structure=True)
"
```

### Example 2: Create Code Benchmark with Code-Focused Operators
```bash
python -c "
from benchmark_cloner_v2 import EnhancedBenchmarkCloner
cloner = EnhancedBenchmarkCloner()
cloner.clone_benchmark('mbpp', 'mbpp_code', 'code_focused', use_split_structure=True)
"
```

### Example 3: Analyze All Benchmark Structures
```bash
python -c "
from benchmark_cloner_v2 import analyze_all_benchmarks
analyze_all_benchmarks()
"
```

## 🔄 Migration Path

For existing benchmarks using legacy structure:

1. **No action required** - They continue to work
2. **Optional upgrade** - Use cloner to recreate with split structure
3. **Gradual migration** - New benchmarks use split, old ones remain

## 📝 Best Practices

1. **Use split structure for new benchmarks** - Better modularity
2. **Keep TASK_PROMPT focused** - Domain description only
3. **Operator descriptions in PART_1** - Basic signatures and purposes
4. **Design principles in PART_2** - Usage patterns and examples
5. **User instructions in USER_PROMPT_LONG** - Task template and rules

## 🛠️ Troubleshooting

### Issue: workflow_generator expects START_PROMPT
**Solution**: The enhanced system always generates START_PROMPT for compatibility, even in split structure.

### Issue: Operator initialization differs between groups
**Solution**: The builder handles special cases (e.g., MATH operators needing self.gid).

### Issue: Structure type unknown
**Solution**: Run `analyze_benchmark_structure()` to diagnose.

## 📖 API Reference

### EnhancedPromptBuilder
```python
builder = EnhancedPromptBuilder(benchmark_name, operator_group)
builder.build_operator_prompt_part_1()  # Generate OPERATOR_PROMPT_PART_1
builder.build_operator_prompt_part_2()  # Generate OPERATOR_PROMPT_PART_2
builder.build_user_prompt_long()        # Generate USER_PROMPT_LONG
builder.build_complete_conditions_v2()  # Generate complete conditions.py
```

### EnhancedBenchmarkCloner
```python
cloner = EnhancedBenchmarkCloner()
cloner.clone_benchmark(source, target, operator_group, use_split_structure=True)
cloner.analyze_benchmark_structure(benchmark_name)
cloner.list_benchmarks()
```

## 🎉 Summary

The Enhanced Dynamic Operator System successfully bridges the gap between the original ScoreFlow design and the dynamic operator configuration system. It provides:

- ✅ Full support for split prompt structure
- ✅ Complete backward compatibility
- ✅ Dynamic operator group configuration
- ✅ Automatic prompt generation
- ✅ Structure analysis tools
- ✅ Comprehensive testing

The system is production-ready and actively maintains both modern and legacy benchmark structures!

---

**Version**: 2.0  
**Last Updated**: 2024  
**Status**: ✅ Fully Operational