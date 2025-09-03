# Model Evaluation Module

A comprehensive batch model evaluation system for testing multiple models on workflow generation tasks and generating comparison reports.

## Features

- **Batch Evaluation**: Test multiple models on the same dataset
- **Async Processing**: Efficient concurrent evaluation with memory management
- **Comprehensive Reports**: JSON, Markdown, CSV formats with comparison charts
- **Flexible Configuration**: YAML-based configuration with parameter overrides
- **Error Handling**: Graceful handling of model failures
- **Memory Management**: Automatic GPU cache clearing between models

## Quick Start

### 1. Prerequisites

```bash
# Activate conda environment
source /opt/anaconda3/etc/profile.d/conda.sh && conda activate workflow

# Start reward server (required)
bash ../servers_and_proxy/start_scoreflow_reward.sh
```

### 2. Basic Usage

```bash
# Run with default configuration
bash evaluate_models.sh

# Quick test with 10 samples
bash evaluate_models.sh -n 10 -y

# Use custom configuration
bash evaluate_models.sh -c example_config.yaml
```

### 3. Python API

```python
import asyncio
from model_evaluation import BatchModelEvaluator

# Configuration
config = {
    'test_data_path': 'test_data.jsonl',
    'reward_server_url': 'http://localhost:8899',
    'output_dir': 'evaluation_reports',
    'eval_batch_size': 8,
    'max_samples': 100
}

# Model list
models = [
    {'name': 'Model-1', 'path': 'path/to/model1'},
    {'name': 'Model-2', 'path': 'path/to/model2'}
]

# Run evaluation
evaluator = BatchModelEvaluator(config)
results = asyncio.run(evaluator.evaluate_models(models))
```

## Configuration

### Main Configuration File

Edit `evaluation_config.yaml`:

```yaml
test_data:
  path: "path/to/test_data.jsonl"
  max_samples: null  # null for all samples

reward_server:
  url: "http://localhost:8899"

evaluation:
  batch_size: 8
  output_dir: "./evaluation_reports"
  generation_params:
    max_new_tokens: 4096
    temperature: 0.7
    top_p: 0.9

models:
  - name: "Model-Name"
    path: "model/path"
    type: "huggingface"  # or "checkpoint", "local"
    generation_params:  # optional override
      temperature: 0.8
```

### Model Types

- **huggingface**: Models from HuggingFace Hub
- **checkpoint**: Local fine-tuned checkpoints
- **local**: Local model directories

## Output Structure

```
evaluation_reports/
├── model_*.json            # Individual model reports
├── model_*.md              # Markdown reports
├── model_comparison.json   # Comparison data
├── model_comparison.md     # Comparison report
├── detailed_results.csv    # Detailed CSV data
├── charts/
│   ├── overall_scores.png  # Score comparison chart
│   └── benchmark_heatmap.png # Performance heatmap
└── evaluation_*.log        # Execution logs
```

## Report Contents

### Individual Model Report
- Overall score and success rate
- Per-benchmark performance metrics
- Statistical analysis (mean, max, min, std)
- Detailed error tracking

### Comparison Report
- Model rankings by overall score
- Benchmark-specific comparisons
- Best/worst model identification
- Visual charts for easy comparison

## Command Line Options

```bash
run_evaluation.py [options]

Options:
  --config, -c FILE      Config file (default: evaluation_config.yaml)
  --test-data, -t FILE   Test data file (overrides config)
  --max-samples, -n N    Maximum samples to evaluate
  --output-dir, -o DIR   Output directory
  --batch-size, -b N     Batch size for processing
  --log-level, -l LEVEL  Log level (DEBUG/INFO/WARNING/ERROR)
  --yes, -y              Skip confirmation prompt
```

## Advanced Usage

### Custom Test Data

Create test data in JSONL format:

```json
{"data_source": "workflow_gsm8k", "prompt": [...], "reward_model": {...}}
{"data_source": "workflow_mbpp", "prompt": [...], "reward_model": {...}}
```

### Adding New Models

1. Edit `evaluation_config.yaml`
2. Add model configuration:
   ```yaml
   - name: "My-Custom-Model"
     path: "/path/to/model"
     type: "checkpoint"
     generation_params:
       temperature: 0.75
   ```
3. Run evaluation

### Parallel Evaluation

For faster evaluation with multiple GPUs:

```python
# Future enhancement: Multi-GPU support
# Currently processes models sequentially to manage memory
```

## Troubleshooting

### Common Issues

1. **Reward Server Not Running**
   ```bash
   bash ../servers_and_proxy/start_scoreflow_reward.sh
   ```

2. **Out of Memory**
   - Reduce batch_size in configuration
   - Process fewer samples with --max-samples
   - Models are automatically cleared after evaluation

3. **Test Data Not Found**
   - Generate test data first:
     ```bash
     cd ../generate_parquet_and_jsonl
     python generate_verl_training_data.py
     ```

4. **Model Loading Errors**
   - Verify model path exists
   - Check CUDA/PyTorch compatibility
   - Ensure sufficient GPU memory

## Integration with Training

This module integrates with the training pipeline:

1. Train models using SFT/RL training
2. Generate test data from benchmarks
3. Evaluate trained checkpoints
4. Compare with baseline models
5. Select best performing model

## Performance Tips

- Use smaller max_samples for quick testing
- Adjust batch_size based on GPU memory
- Enable chart generation only when needed
- Use example_config.yaml for testing

## License

Part of the Flow_RL project. See main project LICENSE.