# Realtime Data Collection and Checkpoint Recovery Guide

## Overview

The model evaluation system now supports realtime data collection with checkpoint recovery. This feature allows:

1. **Realtime Recording**: Each evaluation result is immediately saved to a JSONL file
2. **Checkpoint Recovery**: Resume interrupted evaluations from the last processed sample
3. **Duplicate Prevention**: Automatically skip already processed samples
4. **Performance Tracking**: Record latency and execution time for each evaluation

## Features

### 1. Realtime Data Collection

Each evaluation record contains:
- `sample_id`: Unique identifier for the test sample
- `timestamp`: When the evaluation was performed
- `model_name`: Model being evaluated
- `benchmark`: Dataset/benchmark name
- `input`: Original prompt and metadata
- `output`: Generated solution
- `evaluation`: Success status, score, errors, timeout info
- `performance`: Latency and total execution time

### 2. Checkpoint Recovery

The system maintains three types of files:
- **Data file** (`evaluation_data_*.jsonl`): Actual evaluation records
- **Checkpoint file** (`checkpoint_*.json`): Progress snapshot
- **Resume info** (`resume_info.json`): Current evaluation status

### 3. Data Analysis

Export summary statistics including:
- Overall success rate
- Per-model performance
- Per-benchmark statistics
- Performance metrics

## Usage

### Basic Configuration

```python
from model_evaluation.core.evaluators.unified_batch_evaluator import UnifiedBatchEvaluator

config = {
    'test_data_path': 'data/test_samples.jsonl',
    'reward_server_url': 'http://localhost:8899',
    'output_dir': 'evaluation_reports',
    'eval_batch_size': 8,
    'max_samples': None,  # Process all samples
    'save_intermediate': True,

    # Enable realtime collection
    'enable_realtime_collection': True,
    'collection_output_dir': 'evaluation_data'
}

evaluator = UnifiedBatchEvaluator(config)
```

### Running Evaluation with Realtime Collection

```python
import asyncio

async def run_evaluation():
    model_configs = [
        {
            'name': 'qwen-turbo',
            'type': 'api',
            'api_config': {
                'base_url': 'http://localhost:5019/v1',
                'api_key': 'your-key',
                'model': 'qwen-turbo'
            }
        }
    ]

    results = await evaluator.evaluate_models(model_configs)
    print(f"Evaluation complete: {results['successful_models']}")

asyncio.run(run_evaluation())
```

### Resuming Interrupted Evaluation

If evaluation is interrupted:

1. The system automatically saves progress
2. On next run, it loads `resume_info.json`
3. Skips already processed samples
4. Continues from where it left off

No manual intervention needed!

### Analyzing Collected Data

```python
from model_evaluation.core.utils.realtime_data_collector import RealtimeDataCollector

collector = RealtimeDataCollector('evaluation_data')
summary = await collector.export_summary('summary.json')

print(f"Total records: {summary['total_records']}")
print(f"Success rate: {summary['success_rate']:.2%}")
```

### Reading JSONL Data

```python
import json

with open('evaluation_data/evaluation_data_20250914_120000.jsonl', 'r') as f:
    for line in f:
        record = json.loads(line)
        print(f"Model: {record['model_name']}")
        print(f"Score: {record['evaluation']['score']}")
        print(f"Latency: {record['performance']['latency']}s")
```

## File Structure

```
evaluation_data/
├── evaluation_data_20250914_120000.jsonl  # Evaluation records
├── checkpoint_20250914_120000.json        # Progress checkpoint
├── resume_info.json                       # Resume status
└── realtime_summary_20250914_123000.json  # Summary statistics
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable_realtime_collection` | bool | False | Enable realtime data collection |
| `collection_output_dir` | str | "evaluation_data" | Directory for data files |
| `checkpoint_interval` | int | 10 | Save checkpoint every N records |
| `skip_processed` | bool | True | Skip already processed samples |

## Best Practices

1. **Always enable for long evaluations**: Prevents data loss from interruptions
2. **Use appropriate batch sizes**: Balance between speed and reliability
3. **Monitor disk space**: Each evaluation record takes ~5-10KB
4. **Regular exports**: Generate summaries periodically for analysis
5. **Clean old data**: Archive or delete old evaluation data files

## Troubleshooting

### Issue: Duplicate Records
**Solution**: Check `resume_info.json` status. Delete it to start fresh.

### Issue: High Memory Usage
**Solution**: Reduce `eval_batch_size` in configuration.

### Issue: Slow Recovery
**Solution**: Processing large checkpoint files. Consider smaller `checkpoint_interval`.

### Issue: Missing Data
**Solution**: Check if realtime collection was enabled. Look for JSONL files in collection directory.

## Example Test Script

See `test_realtime_collection.py` for a complete example that demonstrates:
- Setting up realtime collection
- Running evaluation
- Simulating interruption
- Testing checkpoint recovery
- Analyzing collected data

## Performance Impact

Realtime collection adds minimal overhead:
- ~5ms per record write
- ~100KB memory for collector
- Async writes don't block evaluation

## Data Privacy

Be aware that collected data contains:
- Full prompts and solutions
- Model responses
- Error messages

Ensure proper data handling and storage policies.