# ScoreFlow Reward Utils V2 Technical Documentation

## Overview

The `scoreflow_reward_utils.py` is a sophisticated reward calculation system designed for the VERL (Vectorized Environment for Reinforcement Learning) framework. It evaluates workflow generation models' performance through parallel execution and comprehensive scoring mechanisms.

## Architecture Overview

### Core Components

1. **Logging Management System** - Multi-level logging and output redirection
2. **Workflow Execution Manager** - Parallel execution and result aggregation
3. **Reward Calculator** - ScoreFlow framework-based scoring logic
4. **Global Interface Functions** - VERL-compliant external interfaces

### System Flow Diagram

```
┌──────────────────────────────────┐
│   compute_score() Entry Point    │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  ScoreFlowRewardCalculator       │
│  - Extract workflow code         │
│  - Load benchmark handler        │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  WorkflowExecutionManager        │
│  - Create workspace directory    │
│  - Manage parallel execution     │
│  - All-Reduce result aggregation │
└────────────┬─────────────────────┘
             │
             ▼ Parallel Execution
┌──────────────────────────────────┐
│  IndividualTestCaseLogger × N    │
│  - Independent log per test case │
│  - Avoid I/O conflicts           │
└──────────────────────────────────┘
```

## Class Documentation

### 1. TeeOutput (Lines 170-196)
**Purpose**: Basic dual-output class for terminal and file output

**Methods**:
| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `__init__` | Initialize terminal and file handles | `terminal`, `file` | None |
| `write` | Write to both terminal and file | `message: str` | `int` |
| `flush` | Flush both output streams | None | None |
| `isatty` | Check if terminal device | None | `bool` |
| `fileno` | Return file descriptor | None | `int` |

### 2. SafeTeeOutput (Lines 198-261)
**Purpose**: Safe dual-output class preventing writes to closed files

**Methods**:
| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `__init__` | Initialize with manager reference | `terminal`, `file_handle`, `manager_ref` | None |
| `write` | Safely write with state checking | `message: str` | `int` |
| `flush` | Safely flush buffers | None | None |
| `close_when_safe` | Mark as safe to close | None | None |
| `isatty` | Check terminal status | None | `bool` |
| `fileno` | Return file descriptor | None | `int` |

### 3. WorkflowExecutionLogger (Lines 263-303)
**Purpose**: Workflow execution log capturer managing stdout/stderr redirection

**Context Manager Protocol**:
- `__enter__()`: Redirects output when entering context
- `__exit__()`: Restores original output when exiting

### 4. IndividualTestCaseLogger (Lines 305-378)
**Purpose**: Individual test case logger to avoid concurrent I/O conflicts

**Key Features**:
- Creates separate log file for each test case
- Thread-safe logging mechanism
- Automatic cleanup on context exit

### 5. SimpleTeeOutput (Lines 380-431)
**Purpose**: Simplified dual-output class for independent logging

**Methods**:
| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `write` | Safe write to terminal and file | `message: str` | `int` |
| `flush` | Safe buffer flush | None | None |
| `isatty` | Check if terminal | None | `bool` |
| `fileno` | Return file descriptor | None | `int` |

### 6. WorkflowExecutionManager (Lines 433-943) ⭐ Core Class
**Purpose**: Manages single workflow execution and logging with parallel execution + safe aggregation mode

**Key Attributes**:
- `workflow_id`: Unique workflow identifier
- `workflow_dir`: Workflow-specific directory
- `test_cases`: List of test cases to execute
- `data_source`: Data source/benchmark name
- `results_collector`: Thread-safe results collector
- `results_lock`: Async lock for result protection

**Core Methods**:

| Method | Description | Key Parameters | Returns |
|--------|-------------|----------------|---------|
| `__init__` | Initialize execution manager | `workspace_path`, `data_source`, `test_cases` | None |
| `save_workflow_code` | Save workflow code to file | `workflow_code: str` | None |
| `save_metadata` | Save metadata information | `extra_info: Dict` | None |
| `execute_all_test_cases_parallel_safe` | ⭐ Parallel execution of all test cases | `calculator`, `workflow_code`, `dataset_path` | `float` |
| `_execute_single_test_case_isolated` | Execute single test case independently | `calculator`, `workflow_code`, `test_case_index`, `dataset_path` | `dict` |
| `_finalize_and_save_summary` | All-Reduce aggregation phase | `total_duration: float` | `float` |
| `_save_results_csv_safe` | Safely save CSV results | None | None |
| `_save_summary_json_safe` | Safely save JSON summary | Multiple statistics parameters | None |
| `_save_global_execution_log_safe` | Save global execution log | `avg_score`, `total_duration` | None |

### 7. ScoreFlowRewardCalculator (Lines 945-1644) ⭐ Core Class
**Purpose**: ScoreFlow task reward calculator, reusing existing BenchmarkHandler system

**Key Attributes**:
- `llm_config`: LLM configuration
- `reward_config`: Reward calculation configuration
- `workspace_path`: Workspace path
- `timeout`: Execution timeout
- `max_concurrent`: Maximum concurrency
- `_handler_cache`: Handler cache
- `benchmark_mapping`: Benchmark mapping information

**Core Methods**:

| Method | Description | Key Parameters | Returns |
|--------|-------------|----------------|---------|
| `__init__` | Initialize and load configuration | `config_path: str` | None |
| `_load_benchmark_mapping` | Load benchmark mapping file | None | `Dict` |
| `extract_workflow_from_response` | Extract workflow code from LLM response | `response: str` | `Optional[str]` |
| `_load_benchmark_handler` | Dynamically load benchmark handler | `benchmark_name`, `dataset_path` | Handler instance |
| `execute_workflow_metagpt` | ⭐ Execute workflow using MetaGPT | `workflow_code`, `benchmark_name`, `test_case_index`, `dataset_path` | `str` |
| `compute_score_for_testcase` | Compute score for single test case | `workflow_code`, `benchmark_name`, `test_case_index`, `dataset_path` | `float` |
| `compute_reward_async` | Async compute average reward | `workflow_code`, `benchmark_name`, `test_cases`, `dataset_path` | `float` |

## Key Design Patterns

### 1. All-Reduce Parallel Pattern
- Parallel execution of all test cases
- Independent log files for each test case
- Unified result aggregation at the end

### 2. Context Manager Pattern
- WorkflowExecutionManager uses `with` statement for lifecycle management
- Logging classes use `__enter__`/`__exit__` for automatic output redirection

### 3. Caching Pattern
- Handler caching to avoid repeated loading
- Global calculator singleton pattern

## Dependencies and Configuration

### External Dependencies
- `metagpt`: MetaGPT framework for workflow execution
- `ScoreFlow.scripts.base_handler.BenchmarkHandler`: Benchmark handler base class
- `yaml`: Configuration file parsing
- `asyncio`: Asynchronous execution support

### Configuration Files
- `config.yaml`: Main configuration file with paths, service ports
- `benchmark_mapping.jsonl`: Benchmark mapping file

## Execution Flow

1. **Initialization Phase**
   - Load configuration
   - Set up paths
   - Clear proxy environment variables

2. **Workflow Extraction**
   - Extract workflow code from LLM response
   - Validate code structure

3. **Parallel Execution**
   - Create independent tasks for each test case
   - Assign separate log files

4. **MetaGPT Execution**
   - Execute workflow code using MetaGPT framework
   - Handle timeouts and errors

5. **Result Verification**
   - Use Handler's judge method to verify results
   - Calculate scores

6. **Aggregation**
   - All-Reduce mode for final score calculation
   - Collect statistics

7. **Logging**
   - Save CSV results
   - Save JSON summary
   - Save execution logs

## API Reference

### Global Functions

#### `compute_score(data_source, solution_str, ground_truth, extra_info) -> float`
Main entry point for reward calculation.

**Parameters**:
- `data_source`: Benchmark name (e.g., 'gsm8k', 'high_level_math_aime2024')
- `solution_str`: LLM-generated response containing workflow
- `ground_truth`: Ground truth information (usually "default")
- `extra_info`: Dictionary containing test_cases, data_path, etc.

**Returns**: Reward score (0.0 to 1.0)

#### `get_calculator() -> ScoreFlowRewardCalculator`
Get global calculator instance (singleton pattern).

## Performance Optimizations

1. **Parallel Processing**
   - Concurrent execution of test cases
   - Configurable max concurrency limit
   - Semaphore-based throttling

2. **I/O Optimization**
   - Independent log files prevent I/O conflicts
   - Buffered writing with immediate flush
   - Safe file handle management

3. **Memory Management**
   - Handler caching reduces memory overhead
   - Streaming log processing
   - Efficient result collection

## Error Handling

1. **Timeout Management**
   - Configurable timeout per workflow
   - Additional buffer time for cleanup
   - Graceful timeout handling

2. **Exception Handling**
   - Comprehensive try-catch blocks
   - Error sanitization for CSV storage
   - Detailed error logging

3. **Resource Cleanup**
   - Automatic file handle closure
   - Context manager ensures cleanup
   - Safe state transitions

## Debug Features

- `DEBUG` flag for detailed logging
- Debug data saved to `debug_logs/` directory
- Timestamp and duration tracking
- Comprehensive error traceback

## Usage Example

```python
import asyncio
from scoreflow_reward_utils import compute_score

# Prepare test data
test_solution = """
<code>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
    
    async def run_workflow(self):
        # Workflow implementation
        return "solution"
</code>
"""

extra_info = {
    'data_path': 'Processed_dataset/gsm8k/test.jsonl',
    'test_cases': [0, 1, 2],
}

# Compute score
score = compute_score('gsm8k', test_solution, "default", extra_info)
print(f"Reward score: {score}")
```

## Best Practices

1. **Resource Management**
   - Always use context managers for file operations
   - Properly close async resources
   - Monitor memory usage with large datasets

2. **Error Recovery**
   - Implement retry logic for transient failures
   - Log errors comprehensively
   - Validate input data before processing

3. **Performance Tuning**
   - Adjust `max_concurrent` based on system resources
   - Monitor I/O bottlenecks
   - Use appropriate timeout values

## Version History

- **V2.0**: Introduced All-Reduce parallel execution pattern
- **V1.0**: Initial implementation with sequential execution

## License

Proprietary - Part of Flow_RL project

## Contact

For questions or support, refer to the main Flow_RL documentation.