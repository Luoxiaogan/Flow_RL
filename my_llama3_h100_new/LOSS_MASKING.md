# Loss Masking Feature Documentation

## Overview

The loss masking feature allows training to only compute loss on assistant responses, ignoring system prompts and user inputs. This is a common best practice in instruction fine-tuning that can improve model performance.

## How It Works

When enabled, the training script:
1. Identifies assistant response boundaries in the tokenized chat format
2. Creates labels where non-assistant tokens are masked with -100 (ignored by CrossEntropyLoss)
3. Only computes loss on actual assistant response tokens

### Token Identification

- **Llama Models**: Looks for `assistant<|end_header_id|>` markers and masks everything except content between this and `<|eot_id|>`
- **Qwen Models**: Looks for `<|im_start|>assistant\n` markers and masks everything except content between this and `<|im_end|>`

## Usage

### Method 1: Direct Configuration in run_finetune.sh

Edit `run_finetune.sh` and set:
```bash
USE_LOSS_MASK=true  # Enable loss masking
```

### Method 2: Using Model-Specific Scripts

```bash
# For Llama with loss masking
USE_LOSS_MASK_OVERRIDE=true bash run_llama.sh

# For Qwen with loss masking  
USE_LOSS_MASK_OVERRIDE=true bash run_qwen.sh
```

### Method 3: Direct Command Line

```bash
python -m accelerate.commands.launch \
    --config_file accelerate_config.yaml \
    src/train.py \
    --model_name_or_path /path/to/model \
    --model_type llama \
    --dataset_path /path/to/data.jsonl \
    --output_dir /path/to/output \
    --use_loss_mask True \  # Enable loss masking
    # ... other arguments
```

## Testing

Run the test script to verify loss masking is working correctly:

```bash
python test_loss_mask.py
```

This will:
- Test both Llama and Qwen tokenizers
- Show which tokens are marked as assistant responses
- Verify that labels are correctly masked
- Test batch processing

## Performance Impact

- **Training Speed**: Minimal impact (<5% slower due to mask computation)
- **Memory Usage**: No significant change
- **Model Quality**: Often improves response quality by focusing learning on actual outputs

## Example Output

When loss masking is enabled, you'll see in the training logs:
```
Using loss masking for llama (only computing loss on assistant responses)
Loss masking: ENABLED (only assistant tokens contribute to loss)
```

The training_config.json will also include:
```json
{
  "use_loss_mask": true,
  ...
}
```

## Comparison

### Without Loss Masking (Standard)
- Loss computed on all tokens
- Model learns to predict system prompts and user inputs
- May lead to overfitting on prompt structure

### With Loss Masking (Recommended)
- Loss only on assistant responses
- Model focuses on generating good responses
- Better generalization to new prompts

## Troubleshooting

1. **If loss becomes NaN or very high**: Check that your data has properly formatted assistant responses
2. **If no tokens are masked**: Verify the chat template format matches your model type
3. **For custom models**: May need to adjust the marker patterns in `data_collator.py`