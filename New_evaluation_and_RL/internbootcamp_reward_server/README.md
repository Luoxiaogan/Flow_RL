# InternBootcamp Reward Server

A REST API server for computing rewards for InternBootcamp tasks, built on top of the ScoreFlow architecture.

## Architecture

The InternBootcamp Reward Server uses an adapter pattern to integrate InternBootcamp's bootcamp classes with ScoreFlow's BenchmarkHandler interface. This design maximizes code reuse while maintaining compatibility with both systems.

### Key Components

1. **internbootcamp_adapter.py**: Bridges InternBootcamp bootcamp classes to ScoreFlow's BenchmarkHandler interface
2. **internbootcamp_reward_utils.py**: Extends ScoreFlow's reward calculator for InternBootcamp tasks
3. **internbootcamp_reward_server.py**: REST API server (Flask) for reward computation
4. **test_internbootcamp_reward.py**: Comprehensive test suite

## Features

- **Full ScoreFlow Integration**: Inherits all ScoreFlow optimizations including parallel execution and All-Reduce aggregation
- **RESTful API**: Compatible with VERL training framework
- **Dynamic Task Loading**: Automatically discovers and loads all available InternBootcamp tasks
- **Batch Processing**: Support for computing rewards for multiple tasks concurrently
- **Comprehensive Logging**: Independent log files for each test case execution

## Installation

1. **Check Dependencies**:
   ```bash
   python init_internbootcamp.py
   ```
   This will verify all required directories, dependencies, and modules are properly installed.

2. **Install Missing Packages** (if any):
   ```bash
   pip install flask flask-cors pandas pyyaml requests
   ```

## Configuration

The server uses `internbootcamp_config.yaml` for configuration. Key settings include:

- **Port**: 8900 (default)
- **Workspace**: `New_evaluation_and_RL/internbootcamp_workspace`
- **LLM Config**: API settings for MetaGPT execution
- **Timeout**: 300 seconds per task

## Usage

### Starting the Server

**Windows**:
```bash
start_internbootcamp_reward.bat
```

**Linux/Mac**:
```bash
python internbootcamp_reward_server.py --host 0.0.0.0 --port 8900 --debug
```

### API Endpoints

#### Health Check
```bash
GET http://localhost:8900/health
```

#### Get Available Tasks
```bash
GET http://localhost:8900/tasks
```

#### Compute Score
```bash
POST http://localhost:8900/compute_score
Content-Type: application/json

{
  "data_source": "internbootcamp",
  "solution_str": "<workflow_code>",
  "ground_truth": "default",
  "extra_info": {
    "task_name": "sudoku_4x4_easy",
    "test_cases": [0],
    "data_path": ""
  }
}
```

#### Batch Compute
```bash
POST http://localhost:8900/batch_compute
Content-Type: application/json

{
  "tasks": [
    {
      "task_id": "task_1",
      "data_source": "internbootcamp",
      "solution_str": "<workflow_code>",
      "ground_truth": "default",
      "extra_info": {...}
    }
  ]
}
```

## Testing

### Run Full Test Suite
```bash
python test_internbootcamp_reward.py
```

### Test with curl
```bash
test_with_curl.bat
```

### Test with Sample Request
```bash
curl -X POST http://localhost:8900/compute_score \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

## Directory Structure

```
internbootcamp_reward_server/
├── internbootcamp_adapter.py          # Bootcamp to BenchmarkHandler adapter
├── internbootcamp_reward_utils.py     # Reward calculation logic
├── internbootcamp_reward_server.py    # REST API server
├── test_internbootcamp_reward.py      # Test suite
├── init_internbootcamp.py             # Initialization checker
├── start_internbootcamp_reward.bat    # Windows startup script
├── test_with_curl.bat                 # curl test script
├── test_request.json                  # Sample request
└── README.md                          # This file
```

## Integration with VERL

The server is fully compatible with VERL training framework. Use the following data format:

```python
{
    "data_source": "internbootcamp",
    "prompt": messages,  # HuggingFace chat format
    "ability": "task_specific",
    "reward_model": {
        "ground_truth": "default"
    },
    "extra_info": {
        "task_name": "sudoku_4x4_easy",
        "test_cases": [0, 1, 2],
        "entry_id": 0
    }
}
```

## Performance Optimizations

1. **Parallel Execution**: Test cases are executed in parallel with independent logging
2. **All-Reduce Aggregation**: Results are aggregated efficiently after parallel execution
3. **Handler Caching**: Bootcamp classes are cached after first load
4. **Connection Pooling**: HTTP connections are reused for better performance

## Troubleshooting

### Server Won't Start
- Check if port 8900 is already in use
- Verify conda environment is activated: `conda activate workflow`
- Run initialization check: `python init_internbootcamp.py`

### Tasks Not Loading
- Verify InternBootcamp directory exists at project root
- Check if internbootcamp_utils.py is in Test_FILE/verl_internbootcamp/
- Ensure bootcamp classes have required methods: case_generator, prompt_func, verify_score

### Low Scores
- Check MetaGPT API configuration in internbootcamp_config.yaml
- Verify API proxy is running (port 5009)
- Review workflow execution logs in internbootcamp_workspace/

## Migration from Original System

This implementation follows the migration plan in `docs/internbootcamp_migration_plan.md`:

- **90%+ Code Reuse**: Maximizes reuse of ScoreFlow infrastructure
- **Minimal Modifications**: Only ~200 lines of adapter code
- **Full Compatibility**: Maintains VERL interface compatibility
- **Enhanced Performance**: Inherits ScoreFlow's optimizations

## Support

For issues or questions:
1. Check the logs in `New_evaluation_and_RL/logs/`
2. Run the test suite to identify specific problems
3. Review the migration plan documentation
4. Check ScoreFlow documentation for inherited features