# Getting Started

## Prerequisites

- Python 3.8+
- CUDA 11.7+ (for GPU training)
- 8x NVIDIA GPUs (H100/A100 recommended)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/llama3-h100-eval.git
cd llama3-h100-eval
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install the package
```bash
pip install -e .
```

## Quick Test

### Test imports
```bash
python test_imports.py
```

### Run standalone test
```bash
python tests/benchmarks/standalone_test.py
```

## Training

### Basic training
```bash
bash scripts/train.sh
```

### Training with evaluation
```bash
# Start reward server first
cd ../New_evaluation_and_RL/reward_server
python scoreflow_reward_server.py

# In another terminal
bash scripts/train_with_eval.sh
```

## Configuration

Edit configuration files in `configs/` directory:
- `configs/training/` - Training configurations
- `configs/evaluation/` - Evaluation settings

## Troubleshooting

### Import errors
- Ensure you've installed the package: `pip install -e .`
- Check Python path: `echo $PYTHONPATH`

### CUDA errors
- Check GPU availability: `nvidia-smi`
- Verify CUDA version: `nvcc --version`

### Memory issues
- Reduce batch size in config
- Enable gradient checkpointing
- Use DeepSpeed ZeRO-3
