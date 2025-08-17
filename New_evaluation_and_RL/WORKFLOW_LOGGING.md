# Workflow Execution Logging System

## Overview

The workflow execution logging system provides comprehensive logging and result tracking for all workflow executions in the ScoreFlow Reward service. Each workflow execution creates a dedicated directory with detailed logs, results, and metadata.

## Features

- **Structured Directory Organization**: Workflows are organized by benchmark/data_source
- **Dual Output**: All logs are displayed in terminal AND saved to files
- **CSV Result Tracking**: Test case results are saved in CSV format for easy analysis
- **Execution Metadata**: Complete workflow context and configuration saved
- **Error Sanitization**: Error messages are cleaned for CSV compatibility

## Directory Structure

```
workspace/
├── gsm8k/
│   ├── workflow_20250117_143025_abc123/
│   │   ├── workflow.py               # Original workflow code
│   │   ├── metadata.json            # Execution metadata
│   │   ├── test_case_0.log         # Test case 0 execution log
│   │   ├── test_case_1.log         # Test case 1 execution log
│   │   ├── test_case_2.log         # Test case 2 execution log
│   │   ├── results.csv             # All test case results
│   │   └── summary.json            # Execution summary
│   └── workflow_20250117_143125_def456/
│       └── ...
├── mbpp/
│   └── ...
└── high_level_math/
    └── ...
```

## Configuration

Add workspace path in `config.yaml`:

```yaml
scoreflow_reward:
  workspace: "/path/to/workspace"  # Workflow execution logs directory
```

## File Descriptions

### workflow.py
The original workflow code submitted for execution.

### metadata.json
Contains:
- workflow_id: Unique identifier
- data_source: Benchmark name
- test_cases: List of test case indices
- timestamp: Execution start time
- extra_info: Additional context from request

### test_case_X.log
Complete execution log for test case X, including:
- All print statements from workflow
- MetaGPT operator outputs
- Error messages and stack traces
- Timing information

### results.csv
CSV file with columns:
- test_case: Test case index
- success: true/false
- score: 0.0 to 1.0
- duration: Execution time in seconds
- error: Sanitized error message (if failed)
- timestamp: Completion time

### summary.json
Aggregated statistics:
- workflow_id: Unique identifier
- total_test_cases: Number of test cases
- successful_cases: Count of successful executions
- failed_cases: Count of failed executions
- average_score: Mean score across all test cases
- total_duration: Total execution time
- timestamp: Summary generation time

## Usage

### Testing the System

Run the test script:
```bash
bash test_logging_system.sh
```

Or test manually:
```bash
# Start services
bash servers_and_proxy/start_api_proxy.sh
bash servers_and_proxy/start_scoreflow_reward.sh

# Run test
python tests/test_workflow_logging.py
```

### Viewing Results

After execution, check the workspace directory:
```bash
# Find latest workflow
ls -lt workspace/gsm8k/ | head -5

# View summary
cat workspace/gsm8k/workflow_*/summary.json | jq .

# View results CSV
cat workspace/gsm8k/workflow_*/results.csv

# View specific test case log
less workspace/gsm8k/workflow_*/test_case_0.log
```

### Analyzing Results with Python

```python
import pandas as pd
import json
from pathlib import Path

# Load results
workspace = Path("workspace/gsm8k")
latest_workflow = sorted(workspace.glob("workflow_*"))[-1]

# Read CSV results
df = pd.read_csv(latest_workflow / "results.csv")
print(f"Average score: {df['score'].mean():.3f}")
print(f"Success rate: {df['success'].mean():.1%}")

# Read summary
with open(latest_workflow / "summary.json") as f:
    summary = json.load(f)
print(f"Total duration: {summary['total_duration']:.2f} seconds")
```

## Implementation Details

### Log Capture Mechanism

The system uses a `TeeOutput` class to duplicate all stdout/stderr:
- Terminal output remains visible in real-time
- All output is simultaneously written to log files
- Buffering is disabled for immediate visibility

### Error Handling

Error messages are sanitized for CSV storage:
- Newlines replaced with " | "
- Commas replaced with semicolons
- Quotes replaced with single quotes
- Length limited to 500 characters

### Concurrency Control

Test cases are executed with controlled concurrency:
- Maximum concurrent executions configured in config.yaml
- Batch processing to prevent resource exhaustion
- Exception handling for failed executions

## Troubleshooting

### No logs appearing
- Check if services are running: `curl http://localhost:8899/health`
- Verify workspace directory permissions
- Check config.yaml for correct workspace path

### Incomplete logs
- Increase timeout in config.yaml
- Check system resources (memory/CPU)
- Verify MetaGPT configuration

### CSV parsing errors
- Check for special characters in error messages
- Verify CSV file encoding (UTF-8)
- Use pandas with error_bad_lines=False

## Benefits

1. **Debugging**: Complete execution traces for troubleshooting
2. **Performance Analysis**: Duration tracking for optimization
3. **Quality Metrics**: Success rates and scores for evaluation
4. **Reproducibility**: Full workflow code and context saved
5. **Batch Analysis**: CSV format enables statistical analysis