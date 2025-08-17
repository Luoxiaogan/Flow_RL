# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This device is a windows device.
## Project Overview

Flow_RL is a workflow generation and execution system with three main purposes:

1. **Synthetic SFT Data Generation**: Generates meta-workflows that can solve all problems in a given benchmark using predefined operators, executes them, and saves successful ones as training data
2. **SFT Training**: Fine-tunes LLaMA3 models using the collected workflow data
3. **RL Training with veRL**: Uses reinforcement learning (VERL framework) to improve workflow generation models through reward-based optimization

The system generates workflows to solve benchmark problems (GSM8K, MBPP, HumanEval, HotpotQA) using LLMs, executes them via MetaGPT, and collects successful solutions as training data for model fine-tuning. The veRL support enables reinforcement learning training where models learn to generate better workflows based on execution accuracy rewards.

## Key Technologies

- Python with AsyncIO for asynchronous execution
- MetaGPT framework for agent-based workflow execution
- OpenAI-compatible APIs (Alibaba Qwen models)
- PyTorch/Transformers for LLaMA3 fine-tuning
- DeepSpeed for distributed training optimization
- VERL framework for vectorized reinforcement learning training
- Parquet format for efficient data storage and processing
- PPO (Proximal Policy Optimization) for RL training

## Development Commands

### Running the Workflow System

```bash
# Activate the correct conda environment
conda activate workflow

# Navigate to the Test_FILE directory (required for config2.yaml)
cd Test_FILE/

# Run the complete workflow system
bash run_workflow_system.sh

# Or run components individually:
python workflow_generator.py [args]  # Generate workflows
python workflow_executor.py [args]   # Execute workflows
python master_runner.py [args]      # Orchestrate batch processing
```

### Fine-tuning LLaMA3

```bash
# Navigate to fine-tuning directory
cd my_llama3_full_finetune/

# Activate training environment
conda activate qzh

# Run fine-tuning
bash run_finetune.sh

# Monitor training with tmux
tmux attach -t llama_training
```

### SFT (Supervised Fine-Tuning) Training

The `my_llama3_h100_new/` directory contains the production SFT training configuration for H100/L20Z servers.

#### Key Features

1. **Multi-Model Support**
   - **Llama-3.1-8B-Instruct**: Meta's instruction-tuned model
   - **Qwen-2.5-7B-Instruct**: Alibaba's instruction-tuned model
   - Both models use chat templates with system, user, and assistant messages

2. **Advanced Training Features**
   - **Loss Masking**: Optional feature to compute loss only on assistant responses
   - **DeepSpeed ZeRO-3**: Distributed training with model sharding across 8 GPUs
   - **Flash Attention 2**: Optimized attention mechanism for faster training
   - **BF16 Precision**: Native H100 support for brain float16
   - **Gradient Checkpointing**: Trade compute for memory efficiency

3. **Data Format**
   ```json
   {
     "messages": [
       {"role": "system", "content": "System prompt..."},
       {"role": "user", "content": "User question..."},
       {"role": "assistant", "content": "Assistant response..."}
     ]
   }
   ```

#### Running SFT Training

```bash
# Navigate to training directory
cd my_llama3_h100_new/

# Basic training (loss on all tokens)
bash run_finetune.sh

# Training with loss masking (loss only on assistant tokens)
USE_LOSS_MASK_OVERRIDE=true bash run_llama.sh  # For Llama
USE_LOSS_MASK_OVERRIDE=true bash run_qwen.sh   # For Qwen

# Or modify run_finetune.sh directly:
# USE_LOSS_MASK=true  # Enable loss masking
```

#### Loss Masking Feature

Loss masking improves training quality by computing loss only on assistant responses:

- **Without Loss Masking**: Loss computed on all tokens (system + user + assistant)
- **With Loss Masking**: Loss computed only on assistant tokens
- **Benefits**: Better generalization, focuses learning on actual outputs

Token identification:
- **Llama**: Identifies `<|start_header_id|>assistant<|end_header_id|>` boundaries
- **Qwen**: Identifies `<|im_start|>assistant` boundaries

Test loss masking:
```bash
python test_loss_mask.py  # Verify masking works correctly
```

#### Training Configuration

**Hardware Setup (H100/L20Z)**:
- 8x NVIDIA L20Z GPUs (80GB each)
- Total GPU memory: 640GB
- DeepSpeed ZeRO-3 for model sharding

**Training Parameters**:
```bash
# Llama-3.1-8B
- Batch size: 4 per device
- Gradient accumulation: 4 steps
- Global batch size: 128
- Learning rate: 1e-5
- Max sequence length: 4096

# Qwen-2.5-7B
- Batch size: 4 per device
- Gradient accumulation: 4 steps
- Global batch size: 128
- Learning rate: 2e-5
- Max sequence length: 8192
```

**DeepSpeed Configuration** (`configs/deepspeed_config_z3.json`):
- ZeRO Stage 3 optimization
- BF16 mixed precision
- No CPU offloading (sufficient GPU memory)
- Gradient clipping and accumulation

#### Data Analysis Tools

```bash
# Analyze token counts with actual tokenizers
python analysis_using_real_tokenizer.py \
  --data_path merged_training_data_llama.jsonl \
  --model_path meta-llama/Llama-3.2-1B-Instruct \
  --plot

# Analyze character lengths
python analysis_training_data_first.py

# Test chat templates
python test_chat_template.py
```

#### Directory Structure

```
my_llama3_h100_new/
├── src/
│   ├── train.py           # Main training script
│   ├── data_collator.py   # Custom data collators with loss masking
│   └── utils.py           # Training utilities
├── configs/
│   └── deepspeed_config_z3.json  # DeepSpeed ZeRO-3 config
├── run_finetune.sh        # Main training launcher
├── run_llama.sh           # Llama-specific launcher
├── run_qwen.sh            # Qwen-specific launcher
├── accelerate_config.yaml # Accelerate/DeepSpeed config
├── test_loss_mask.py      # Test loss masking
├── LOSS_MASKING.md        # Loss masking documentation
└── H100_SETUP.md          # Hardware setup details
```

#### Important Training Details

1. **Chat Templates**: Both models include system prompts in training
   - Llama adds default date/knowledge cutoff info
   - Qwen adds default "You are Qwen" if no custom system prompt
   - System prompts are clearly marked with special tokens

2. **Model Saving**: With DeepSpeed ZeRO-3, model is sharded across GPUs
   - Each GPU holds ~1/8 of the model
   - Final save consolidates all shards (~15GB for 8B model)
   - Only rank 0 saves the complete model

3. **Monitoring**: Training logs include
   - WandB integration for metrics tracking
   - Loss masking status
   - Token statistics per batch
   - Checkpoint saving every 500 steps

### veRL Data Generation and Training

```bash
# Navigate to verl_support directory
cd Test_FILE/verl_support/

# Generate VERL format data for all benchmarks
python generate_verl_data.py

# Or generate for a specific benchmark
python generate_verl_data.py --benchmark gsm8k

# Test the VERL system
python test_verl_system.py

# Run VERL training (adjust paths in test.sh first)
bash test.sh
```

## Architecture

The system operates in three phases:

1. **Generation**: Creates workflow code using LLMs to solve benchmark problems
   - Prompts include predefined templates + 1-3 randomly selected benchmark problems
   - Generated workflows use predefined operators compatible with MetaGPT ActionNodes
2. **Execution**: Runs workflows through MetaGPT and validates outputs
3. **Training Data Collection**: Formats successful workflows for model fine-tuning

### Directory Structure

- `Test_FILE/`: Main workflow system
  - `ScoreFlow/`: Core benchmarking framework
    - `scripts/base_handler.py`: Unified abstract interface for all benchmarks
    - `scripts/{benchmark}/`: Benchmark-specific implementations
      - `conditions.py`: Prompts (META_PROMPTS, SYSTEM_PROMPT, PYTHON_START/END, etc.)
      - `handler.py`: Workflow execution and validation methods
      - `operator_an.py`: Operator Pydantic models
      - `operator.py`: Operator class definitions (MetaGPT ActionNode compatible)
      - `op_prompt.py`: Operator-specific prompts
  - `config2.yaml`: MetaGPT configuration with API settings
  - `workflow_generator.py`: Generates workflow code
  - `workflow_executor.py`: Executes and validates workflows
  - `master_runner.py`: Orchestrates batch processing
  - `verl_support/`: veRL reinforcement learning support
    - `generate_verl_data.py`: Generates training/test data in VERL format
    - `workflow_reward.py`: Computes rewards based on workflow execution accuracy
    - `test.sh`: Script to launch VERL training with PPO
    - `config.json`: Configuration for data generation and reward calculation
    - `utils.py`: Utility functions that reuse existing system components
    - `test_verl_system.py`: System testing script
    - `data/`: Generated parquet files for training and testing
- `my_llama3_h100_new/`: H100/L20Z GPU training configuration (production)
  - Full SFT training implementation with loss masking support
  - Supports both Llama-3.1-8B and Qwen-2.5-7B models
  - DeepSpeed ZeRO-3 distributed training across 8 GPUs
- `my_llama3_full_finetune/`: A800 GPU training configuration
- `my_llama3_v100/`: V100 GPU training (memory issues)
- `my_llama3_v100_pp/`: V100 pipeline parallel training (not recommended)
- `Processed_dataset/`: Preprocessed benchmark datasets in JSONL format
- `workspace*/`: Output directories for generated workflows and results
- `training_data/`: Collected successful workflows for fine-tuning

### Benchmark Support Status

- **Fully Supported**: GSM8K, MBPP
- **Not Yet Supported**: DROP, HotpotQA, HumanEval, MATH

## API Configuration

The system uses OpenAI-compatible APIs configured in:
- `Test_FILE/config2.yaml`: MetaGPT execution configuration
- `run_workflow_system.sh`: API pool for workflow generation (see API_POOL and EXEC_LLM variables)

## veRL (Reinforcement Learning) Support

The veRL support enables reinforcement learning training for workflow generation models using the VERL framework. This allows models to learn from execution feedback and improve their workflow generation capabilities.

### Architecture

1. **Data Generation Phase**:
   - Generates prompts for workflow creation using existing benchmark problems
   - Splits data into training (80%) and testing (20%) sets with no overlap
   - Formats data in VERL-compatible parquet format
   - Strictly reuses `workflow_generator.py` logic for consistency

2. **Reward Calculation**:
   - Uses generated workflows on test set problems
   - Executes workflows and measures accuracy
   - Returns accuracy as reward signal (0.0 to 1.0)
   - Strictly reuses `workflow_executor.py` logic for execution

3. **Training Phase**:
   - Uses PPO algorithm for policy optimization
   - Trains on generated prompts with reward signals
   - Supports distributed training with VERL framework

### VERL Data Format

Training data includes:
```json
{
    "data_source": "gsm8k",
    "prompt": "<formatted_prompt>",
    "ability": "math_reasoning",
    "reward_model": {
        "ground_truth": [problem_indices]
    },
    "extra_info": {
        "sample_id": 0,
        "num_problems": 3,
        "problem_indices": [1, 5, 8]
    }
}
```

### Key Components

- **generate_verl_data.py**: Creates VERL-format training/test data
- **workflow_reward.py**: Computes rewards based on execution accuracy
- **test.sh**: Launches VERL training with configurable parameters
- **config.json**: Controls data generation and split ratios

### Usage Example

```python
# Simple reward calculation
from workflow_reward import compute_score

workflow_code = "class Workflow: ..."
score = compute_score(workflow_code, "gsm8k")
print(f"Reward: {score:.3f}")
```

## Important Notes

1. **Directory Requirements**: Always run from `Test_FILE/` directory to ensure config2.yaml is found
2. **Path Dependencies**: Many scripts use absolute server paths - local execution may require path adjustments
3. **Environment Setup**:
   - Use `workflow` conda environment for workflow operations
   - Use `qzh` conda environment for LLaMA3 fine-tuning
4. **MetaGPT**: Uses a local installation at `/home/lg/workflow_tooluse/ScoreFlow/metagpt_local` (old version)
5. **Execution Limits**:
   - Workflow execution timeout: 180 seconds per workflow
   - Maximum concurrent tasks during generation: 10 (configurable in run_workflow_system.sh)
6. **Parameter Reference**: See `./Test_FILE/V2版本.md` for detailed parameter documentation
7. **veRL Data Generation**: 
   - Strictly reuses existing workflow generation logic from `workflow_generator.py`
   - Reward function strictly reuses existing workflow execution logic from `workflow_executor.py`
   - Train/test split default: 80% training, 20% testing with no overlap
   - Generated data stored in parquet format for efficient processing
8. **veRL Training**:
   - Default model: Qwen2.5-Math-7B-Instruct
   - Uses PPO (Proximal Policy Optimization) algorithm
   - Training data paths must be adjusted in `test.sh` before running
   - Supports both GSM8K and MBPP benchmarks
9. **SFT Training (`my_llama3_h100_new/`)**:
   - **Environment**: Use `verl` conda environment
   - **Import Fix**: When running directly, imports are adjusted to handle module paths
   - **Loss Masking**: Optional feature to train only on assistant responses
   - **Data Format**: JSONL with messages array containing system/user/assistant roles
   - **Model Paths**: Located at `/nas/models/` on the server
   - **Output**: Saved to `/nas/ganluo/sft_output/`
   - **WandB**: Requires unsetting WANDB_API_KEY if issues occur

## Documentation Standards

When creating documentation files (README.md or other markdown documents):

1. **Always create TWO versions**:
   - English version: `README.md` or `[filename].md`
   - Chinese version: `README_zh.md` or `[filename]_zh.md`

2. **Content requirements**:
   - Both versions should contain equivalent information
   - Chinese version should use native Chinese expressions, not direct translations
   - Use appropriate emojis and formatting for better readability
   - Include clear section headers and table of contents for longer documents

3. **File naming convention**:
   - English: standard filename (e.g., `README.md`, `INSTALL.md`, `API.md`)
   - Chinese: add `_zh` suffix before `.md` (e.g., `README_zh.md`, `INSTALL_zh.md`, `API_zh.md`)

4. **Language quality**:
   - English: Clear, concise, professional technical writing
   - Chinese: 使用地道的中文表达，避免生硬翻译，使用适当的技术术语
- to memorize 所有代码的注释都应该是英文，所有的print和log都应该是中文输出
- to memorize 在本项目中，本地测试都需要source /opt/anaconda3/etc/profile.d/conda.sh && conda activate workflow
- to memorize 写计划和回答问题使用简体中文