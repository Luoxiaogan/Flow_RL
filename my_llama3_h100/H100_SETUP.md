# H100/L20Z Training Configuration

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