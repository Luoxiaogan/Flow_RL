# CoT vs Self-Consistency Workflow Evaluation System

This system evaluates the performance of Chain-of-Thought (CoT) and Self-Consistency workflows on multiple benchmarks using the ScoreFlow reward server.

## Overview

The system tests two workflow strategies:
- **Chain-of-Thought (CoT)**: Guides the model to think step-by-step
- **Self-Consistency**: Generates multiple solutions and selects the best one

## Benchmarks Tested

1. **GSM8K** - Mathematical reasoning problems
2. **MBPP** - Basic Python programming problems
3. **HumanEval** - Python function implementation tasks

Note: The system uses benchmark names from `ScoreFlow/benchmark_mapping.jsonl`:
- Use `humaneval` (not `human_eval`)
- Data paths are automatically loaded from the mapping file

## Prerequisites

1. **Reward Server** must be running:
   ```bash
   # Start reward server (in another terminal)
   cd ../New_evaluation_and_RL/reward_server
   python scoreflow_reward_server.py
   ```

2. **API Proxy** (if required):
   ```bash
   # Start API proxy (if using remote models)
   cd ../New_evaluation_and_RL/servers_and_proxy
   bash start_api_proxy.sh
   ```

## Installation

No additional installation required. The system uses existing ScoreFlow infrastructure.

## Usage

### Quick Start

```bash
# Navigate to baseline directory
cd D:/temp/Flow_RL/baseline

# Run the evaluation
python test_workflows.py
```

### Configuration

Edit `config.yaml` to adjust:
- Number of samples per benchmark (default: 50)
- Benchmarks to test
- Reward server URL
- Output directory

### Output

The system generates:
- `results/{benchmark}_results.json` - Individual benchmark results
- `results/summary_report.txt` - Human-readable report
- `results/all_results.json` - Complete evaluation data

## How It Works

1. **Sample Selection**: Randomly selects N samples from each benchmark's test set
2. **Workflow Execution**: Sends fixed workflow templates to reward server
3. **Score Collection**: Reward server executes workflows and returns accuracy scores
4. **Report Generation**: Creates comparative analysis of both methods

## Workflow Templates

### CoT Workflow
```python
1. Generate solution with step-by-step prompting
2. Refine the solution
3. Format the final answer
```

### Self-Consistency Workflow
```python
1. Generate 3 solutions using different approaches
2. Use ensemble to select best solution
3. Format the final answer
```

## Expected Results

Typical performance improvements with Self-Consistency:
- GSM8K: +4-6% accuracy
- MBPP: +3-5% accuracy
- HumanEval: +4-6% accuracy

## Troubleshooting

### Reward Server Connection Failed
- Check if reward server is running: `curl http://localhost:8899/health`
- Verify the URL in config.yaml

### Timeout Errors
- Increase timeout in config.yaml (default: 300 seconds)
- Reduce samples_per_benchmark

### File Not Found
- Ensure test data exists in `../Processed_dataset/{benchmark}/test.jsonl`
- Check data.base_path in config.yaml

## Sample Output

```
============================================
     CoT vs Self-Consistency 评估报告
============================================
测试时间: 2024-XX-XX XX:XX:XX

Benchmark: GSM8K
--------------------------------------------
CoT准确率:              70.0%
Self-Consistency准确率: 76.0%
提升:                   +6.0%

Benchmark: MBPP
--------------------------------------------
CoT准确率:              60.0%
Self-Consistency准确率: 66.0%
提升:                   +6.0%

============================================
总体统计
--------------------------------------------
平均CoT准确率:          65.0%
平均Self-Consistency:   71.0%
平均提升:               +6.0%
============================================
```