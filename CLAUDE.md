# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flow_RL is a workflow generation and execution system with two main purposes:

1. **Synthetic SFT Data Generation**: Generates meta-workflows that can solve all problems in a given benchmark using predefined operators, executes them, and saves successful ones as training data
2. **SFT Training**: Fine-tunes LLaMA3 models using the collected workflow data

The system generates workflows to solve benchmark problems (GSM8K, MBPP, HumanEval, HotpotQA) using LLMs, executes them via MetaGPT, and collects successful solutions as training data for model fine-tuning.

## Key Technologies

- Python with AsyncIO for asynchronous execution
- MetaGPT framework for agent-based workflow execution
- OpenAI-compatible APIs (Alibaba Qwen models)
- PyTorch/Transformers for LLaMA3 fine-tuning
- DeepSpeed for distributed training optimization

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