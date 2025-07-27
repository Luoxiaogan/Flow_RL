# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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