# Checkpoint Testing System

## Overview

The Checkpoint Testing System is designed to evaluate fine-tuned language models by testing their ability to generate and execute workflows for solving benchmark problems. The system uses vLLM to serve the checkpoint model and tests the generated workflows against known benchmarks like GSM8K and MBPP.

## Architecture

The system consists of four main components:

1. **vLLM Server (`start_vllm_server.py`)**: Serves the checkpoint model using vLLM for efficient inference
2. **Prompt Generator (`prompt_generator.py`)**: Constructs prompts and sends them to the vLLM server to generate workflows
3. **Workflow Tester (`workflow_tester.py`)**: Executes generated workflows and validates results against ground truth
4. **Main Orchestrator (`test_checkpoint.py`)**: Coordinates the generation and testing pipeline
5. **Shell Script (`run_checkpoint_test.sh`)**: Provides an easy-to-use interface for running the complete pipeline

## System Flow

1. **Server Startup**: The vLLM server is started with the specified checkpoint
2. **Batch Processing**: The system processes workflows in batches:
   - Creates random combinations of benchmark problems
   - Generates multiple workflow versions for each combination
   - Tests all generated workflows
3. **Result Collection**: Results are saved with detailed statistics and logs

## Installation and Setup

### Prerequisites

- Python 3.8+
- CUDA-capable GPU (default: GPU 7)
- vLLM installed (`pip install vllm`)
- Required Python packages:
  ```bash
  pip install aiohttp asyncio openai
  ```

### Directory Structure

```
test_checkpoint/
├── start_vllm_server.py      # vLLM server startup script
├── prompt_generator.py       # Prompt generation module
├── workflow_tester.py        # Workflow testing module
├── test_checkpoint.py        # Main orchestration script
├── run_checkpoint_test.sh    # Shell script for complete pipeline
├── ScoreFlow/               # Copied from Test_FILE/ScoreFlow
├── config/                  # Copied from Test_FILE/config
└── checkpoint_test_results/ # Output directory (created at runtime)
```

## Usage

### Quick Start

Run the complete pipeline with default settings:

```bash
./run_checkpoint_test.sh /path/to/checkpoint gsm8k ../Processed_dataset/gsm8k.jsonl
```

### Detailed Usage

#### 1. Starting vLLM Server Manually

```bash
python start_vllm_server.py \
    --model-path /path/to/checkpoint \
    --port 8000 \
    --gpu-id 7 \
    --tensor-parallel-size 1 \
    --max-model-len 4096
```

#### 2. Running Tests Manually

```bash
# First, ensure the server is running, then:
python test_checkpoint.py \
    --checkpoint-path /path/to/checkpoint \
    --benchmark gsm8k \
    --dataset-path ../Processed_dataset/gsm8k.jsonl \
    --server-url http://localhost:8000 \
    --exec-llm '{"provider": "openai", "model": "qwen2-72b-instruct", "api_key": "YOUR_KEY", "base_url": "https://api.siliconflow.cn/v1"}' \
    --num-batches 10 \
    --workflows-per-batch 15
```

### Configuration Parameters

#### Shell Script Arguments

1. `CHECKPOINT_PATH`: Path to the model checkpoint
2. `BENCHMARK`: Benchmark name (gsm8k, mbpp)
3. `DATASET_PATH`: Path to the dataset file
4. `SERVER_PORT`: vLLM server port (default: 8000)
5. `GPU_ID`: GPU device ID (default: 7)
6. `TENSOR_PARALLEL_SIZE`: Number of GPUs for tensor parallelism (default: 1)
7. `MAX_MODEL_LEN`: Maximum sequence length (default: 4096)

#### Test Parameters (in shell script)

- `NUM_BATCHES`: Number of batches to process (default: 10)
- `WORKFLOWS_PER_BATCH`: Workflows per batch (default: 15)
- `PROBLEMS_PER_WORKFLOW`: Average problems per workflow (default: 3)
- `PARALLELISM`: Number of versions per workflow combination (default: 2)

## Output Structure

```
checkpoint_test_results/
└── gsm8k_20240321_143052/
    ├── generated_workflows/
    │   ├── gsm8k_20240321_143052_1234.py
    │   ├── gsm8k_20240321_143052_1234.meta.json
    │   └── ...
    ├── test_results/
    │   └── test_results.csv
    └── test_summary.json
```

### Output Files

- **Workflow Files (`.py`)**: Generated workflow code
- **Metadata Files (`.meta.json`)**: Workflow metadata including benchmark, problem indices
- **Test Results (`test_results.csv`)**: Detailed test results for each workflow
- **Test Summary (`test_summary.json`)**: Overall statistics and performance metrics

## Module Details

### vLLM Server Module

The `start_vllm_server.py` script:
- Starts a vLLM server with the specified checkpoint
- Configures GPU allocation and model parameters
- Provides health check endpoint for readiness detection

### Prompt Generator Module

The `prompt_generator.py` module:
- Constructs prompts using benchmark-specific templates
- Sends batch requests to vLLM server
- Supports diversity through reference workflows
- Saves generated workflows and metadata

Key methods:
- `construct_prompt()`: Builds prompts from benchmark problems
- `send_to_server()`: Sends requests to vLLM server
- `generate_workflow_batch()`: Processes multiple workflows in parallel

### Workflow Tester Module

The `workflow_tester.py` module:
- Loads generated workflows and metadata
- Builds executable scripts with proper imports and environment
- Executes workflows with timeout protection
- Validates results using benchmark-specific judge methods

Key methods:
- `build_executable_script()`: Creates runnable script with workflow
- `execute_workflow()`: Runs workflow and captures output
- `test_single_workflow()`: Complete test pipeline for one workflow

### Main Orchestrator

The `test_checkpoint.py` script:
- Manages the complete testing pipeline
- Creates random problem batches
- Coordinates generation and testing phases
- Collects and reports statistics

## Benchmark Support

Currently supported benchmarks:
- **GSM8K**: Grade school math problems
- **MBPP**: Basic Python programming problems

Each benchmark requires:
- Handler implementation in `ScoreFlow/scripts/{benchmark}/handler.py`
- Condition templates in `ScoreFlow/scripts/{benchmark}/conditions.py`
- Operator definitions in `ScoreFlow/scripts/{benchmark}/operator.py`

## Performance Considerations

1. **Batching**: The system processes workflows in batches to optimize throughput
2. **Parallelism**: Multiple workflows are generated and tested concurrently
3. **Timeout Protection**: Each workflow execution has a configurable timeout (default: 180s)
4. **GPU Utilization**: vLLM server uses specified GPU for efficient inference

## Troubleshooting

### Common Issues

1. **Server fails to start**:
   - Check GPU availability with `nvidia-smi`
   - Ensure vLLM is installed correctly
   - Verify checkpoint path exists

2. **Generation failures**:
   - Check server is running and accessible
   - Verify API endpoint URL
   - Check server logs for errors

3. **Testing failures**:
   - Ensure execution LLM config is valid
   - Check MetaGPT dependencies
   - Review workflow syntax errors in logs

### Debug Mode

For detailed debugging, modify the scripts to increase logging:
- Add `--log-level DEBUG` to Python scripts
- Check server logs for generation issues
- Review individual workflow files for syntax errors

## Future Improvements

1. **RL Training Integration**: The modular design allows easy integration with RL training pipelines
2. **Additional Benchmarks**: Support for HumanEval, HotpotQA, MATH, DROP
3. **Distributed Testing**: Multi-node testing for larger scale evaluation
4. **Real-time Monitoring**: Web dashboard for tracking test progress
5. **Adaptive Sampling**: Smart problem selection based on model performance

## API Reference

### CheckpointTester Class

```python
tester = CheckpointTester(
    checkpoint_path: str,
    benchmark: str,
    dataset_path: str,
    server_url: str,
    exec_llm_config: Dict[str, str],
    num_batches: int = 10,
    workflows_per_batch: int = 15,
    problems_per_workflow: int = 3,
    parallelism: int = 2,
    output_base_dir: str = "checkpoint_test_results"
)

await tester.run_full_test()
```

## License

This system is part of the Flow_RL project and follows the same licensing terms.