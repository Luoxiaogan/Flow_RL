# New Benchmarks Added: MBPP+, HumanEval+, and SimpleQA

## Summary

Successfully added support for three new benchmark datasets:
- **mbppplus**: Enhanced version of MBPP with more comprehensive test cases
- **humanevalplus**: Enhanced version of HumanEval with extended test suites
- **simpleqa**: World knowledge question answering benchmark

## Files Created

### MBPP+ Support Files
1. **ScoreFlow/scripts/mbppplus/handler.py**
   - Handler class: `MbppplusHandler`
   - Handles code generation with enhanced test validation
   - Supports both basic test cases and extended test suites

2. **ScoreFlow/scripts/mbppplus/conditions.py**
   - Contains prompt templates for workflow generation
   - Optimized for Python function implementation tasks

### HumanEval+ Support Files
1. **ScoreFlow/scripts/humanevalplus/handler.py**
   - Handler class: `HumanevalplusHandler`
   - Processes function signatures with docstrings
   - Validates against comprehensive test suites

2. **ScoreFlow/scripts/humanevalplus/conditions.py**
   - Contains prompt templates for function implementation
   - Focuses on precise signature matching and edge case handling

### SimpleQA Support Files
1. **ScoreFlow/scripts/simpleqa/handler.py**
   - Handler class: `SimpleqaHandler`
   - Processes world knowledge questions
   - Intelligent answer extraction from model outputs

2. **ScoreFlow/scripts/simpleqa/conditions.py**
   - Contains prompt templates for knowledge-based QA
   - Optimized for factual answer generation

### Configuration Updates
- **ScoreFlow/benchmark_mapping.jsonl**
  - Added mbppplus entry with data paths
  - Added humanevalplus entry with data paths
  - Added simpleqa entry with data paths

## Data Paths

### MBPP+
- Training data: `Processed_dataset/mbppplus/mbppplus_train.jsonl`
- Test data: `Processed_dataset/mbppplus/mbppplus_test.jsonl`

### HumanEval+
- Training data: `Processed_dataset/humanevalplus/humanevalplus_train.jsonl`
- Test data: `Processed_dataset/humanevalplus/humanevalplus_test.jsonl`

### SimpleQA
- Training data: `Processed_dataset/simpleqa/simpleqa_train.jsonl`
- Test data: `Processed_dataset/simpleqa/simpleqa_test.jsonl`

## Testing

Created test script: `test_new_benchmarks.py`

Test Results:
- [OK] Benchmark Registration
- [OK] MBPPPLUS - 76 test samples loaded successfully
- [OK] HUMANEVALPLUS - 33 test samples loaded successfully
- [OK] SIMPLEQA - 866 test samples loaded successfully

## Usage

To use the new benchmarks with the workflow system:

```bash
# Generate workflows for MBPP+
python workflow_generator.py --benchmark mbppplus --num_problems 3

# Generate workflows for HumanEval+
python workflow_generator.py --benchmark humanevalplus --num_problems 3

# Generate workflows for SimpleQA
python workflow_generator.py --benchmark simpleqa --num_problems 3

# Run complete workflow system with new benchmarks
bash run_workflow_system.sh
# Then modify BENCHMARK variable to "mbppplus", "humanevalplus", or "simpleqa"
```

## Key Features

### MBPP+ Handler
- Extracts task descriptions, code signatures, and test cases
- Executes generated code with comprehensive test validation
- Supports numpy and other common libraries
- Handles both basic and extended test suites

### HumanEval+ Handler
- Processes function signatures with type hints
- Validates using check(candidate) test format
- Includes canonical solutions for reference (not for copying)
- Supports complex test scenarios with edge cases

### SimpleQA Handler
- Processes world knowledge questions across multiple topics
- Intelligent answer extraction from various output formats
- Supports topics: Science, Geography, History, Culture, etc.
- Handles different answer types: Person, Place, Date, etc.
- Includes reference URLs for fact verification

## Implementation Notes

1. **Data Format Compatibility**: All handlers are designed to work with the existing jsonl data format
2. **Test Coverage**: Enhanced test suites provide more robust validation than original benchmarks
3. **Error Handling**: Comprehensive error messages for debugging failed tests
4. **Code Extraction**: Smart code extraction from LLM outputs (handles code blocks, function definitions)

## Next Steps

1. Run full workflow generation and execution tests
2. Fine-tune prompt templates in conditions.py based on results
3. Consider adding support for additional enhanced benchmarks
4. Monitor performance compared to original MBPP and HumanEval