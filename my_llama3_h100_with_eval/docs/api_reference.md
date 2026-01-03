# API Reference

## Training Module

### `src.training.trainer`

Main training script with evaluation support.

```python
from src.training import train

# Run training
train()
```

### `src.training.data_collator`

Data collators for training.

```python
from src.training.data_collator import DataCollatorForChatML

collator = DataCollatorForChatML(
    tokenizer=tokenizer,
    model_type="llama",
    pad_to_multiple_of=8
)
```

## Evaluation Module

### `src.evaluation.EvaluationCallback`

Callback for automatic evaluation during training.

```python
from src.evaluation import EvaluationCallback

callback = EvaluationCallback({
    'test_data_path': 'path/to/test.jsonl',
    'reward_server_url': 'http://localhost:8899',
    'eval_batch_size': 8,
    'async_eval': True
})
```

### `src.evaluation.ReportGenerator`

Generate evaluation reports in multiple formats.

```python
from src.evaluation import ReportGenerator

generator = ReportGenerator('output_dir')
report = await generator.generate_report(scores, checkpoint_info, test_samples)
```

## Configuration

### Training Arguments

- `model_name_or_path`: Path to pretrained model
- `dataset_path`: Path to training data
- `output_dir`: Directory for outputs
- `num_train_epochs`: Number of training epochs
- `per_device_train_batch_size`: Batch size per GPU
- `learning_rate`: Learning rate
- `use_loss_mask`: Enable loss masking

### Evaluation Arguments

- `enable_auto_eval`: Enable automatic evaluation
- `eval_test_data_path`: Path to test data
- `reward_server_url`: Reward server URL
- `eval_batch_size`: Evaluation batch size
- `async_evaluation`: Run evaluation asynchronously
- `eval_interval`: Evaluate every N checkpoints
