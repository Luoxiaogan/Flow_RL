# H100/L20Z Training Configuration

unset WANDB_API_KEY 才行!
wandb api: 6d73f146a264e1dd556fc16529a88c3871ec4af3

This directory contains the configuration for training LLaMA-3-8B on the H100 server with 8x NVIDIA L20Z GPUs (80GB each).

## Key Configuration Changes from A100:

1. **GPU Configuration**:
   - 8x NVIDIA L20Z GPUs (80GB memory each)
   - Total GPU memory: 640GB
   - Using all 8 GPUs for distributed training

2. **Paths Updated**:
   - Model: `/nas/models/Meta-Llama-3-8B-Instruct`
   - Dataset: `/nas/ganluo/Flow_RL/training_data/gsm8k/jsonl1_verified_correct.jsonl`
   - Output: `/nas/ganluo/sft_output/Llama-3-8B-Instruct-Workflow-Expert-H100`
   - Config: `/nas/ganluo/Flow_RL/my_llama3_h100/`

3. **Training Parameters**:
   - Per-device batch size: 4 (increased from 2)
   - Gradient accumulation: 4 (reduced from 8)
   - Global batch size: 8 × 4 × 4 = 128
   - 8 processes for distributed training

4. **DeepSpeed Configuration**:
   - ZeRO Stage 3 optimization
   - BF16 precision (L20Z native support)
   - No CPU offloading (all data stays on GPU)
   - Optimized for high-memory GPUs

## Running Training:

```bash
# Direct execution
bash /nas/ganluo/Flow_RL/my_llama3_h100/run_finetune.sh

# Or with tmux
tmux new-session -d -s llama_h100_training
tmux kill-session -t llama_h100_training
tmux send-keys -t llama_h100_training "cd /nas/ganluo/Flow_RL/my_llama3_h100" Enter
tmux send-keys -t llama_h100_training "conda activate qzh" Enter
tmux send-keys -t llama_h100_training "bash run_finetune.sh" Enter
tmux attach -t llama_h100_training

# Background execution with logging
nohup bash /nas/ganluo/Flow_RL/my_llama3_h100/run_finetune.sh > /nas/ganluo/sft_output/training_h100.log 2>&1 &
```

## Monitoring:
- Logs: `/nas/ganluo/sft_output/training_h100.log`
- WandB project: `llama3-8b-workflow-h100-sft`
- Checkpoints: `/nas/ganluo/sft_output/Llama-3-8B-Instruct-Workflow-Expert-H100/`

## Training Details and Checkpoint Saving

### DeepSpeed ZeRO-3 Model Distribution

With DeepSpeed ZeRO Stage 3, the model weights are **NOT** replicated across all 8 GPUs. Instead:

1. **Model Sharding**: The 8B parameters are sharded (split) across all 8 GPUs
   - Each GPU holds ~1B parameters (8B ÷ 8 GPUs)
   - This is why each GPU process only saves ~18MB when using naive save methods
   - The complete model requires gathering all shards from all GPUs

2. **Why ZeRO-3 Sharding?**
   - Memory efficiency: Each GPU only stores 1/8th of the model
   - Enables training larger models that wouldn't fit on a single GPU
   - LLaMA-3-8B (~15GB in bf16) could fit on one L20Z (80GB), but sharding leaves more memory for activations and optimizer states

### Checkpoint Saving Process

1. **During Training (Intermediate Checkpoints)**:
   - The Trainer automatically handles DeepSpeed checkpoint saving
   - All 8 GPU processes participate in saving their respective shards
   - DeepSpeed checkpoints are saved in a distributed format

2. **Final Model Save (After Training)**:
   ```python
   trainer.save_model(output_dir)  # This line handles everything
   ```
   
   This method:
   - Gathers all model shards from GPUs 0-7
   - Consolidates them into a complete model on the main process (rank 0)
   - Saves the complete ~15GB model to disk
   - Only rank 0 performs the final write to avoid conflicts

3. **Expected Model Size**:
   - Full model: ~15GB (8B parameters × 2 bytes/param in bf16)
   - If you see 18MB: Only one shard was saved (bug we fixed)
   - Tokenizer files: ~2-3MB additional

### Verifying Successful Save

After training, check the model size:
```bash
du -sh /nas/ganluo/sft_output/Llama-3-8B-Instruct-Workflow-Expert-H100/
# Should show ~15GB, not 18MB
```

The saved files should include:
- `model.safetensors` or `pytorch_model.bin` (~15GB)
- `config.json` (model configuration)
- `tokenizer.json`, `tokenizer_config.json` (tokenizer files)
- `special_tokens_map.json`, `generation_config.json` (additional configs)