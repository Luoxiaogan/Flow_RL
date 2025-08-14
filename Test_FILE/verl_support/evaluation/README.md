# 📊 Model Evaluation System

A comprehensive evaluation system for testing models on workflow generation tasks. Supports both local models (via SGLang) and external API models.

## 🚀 Features

- **Dual Backend Support**: Local SGLang servers or external APIs (OpenAI, Anthropic, Qwen, etc.)
- **Concurrent Processing**: Parallel inference and scoring for high throughput
- **Comprehensive Reporting**: Detailed JSONL results, markdown summaries, CSV exports, and visualizations
- **Flexible Configuration**: Support for various model types and parameters
- **Error Handling**: Automatic retries and graceful error recovery
- **Progress Tracking**: Real-time progress bars for long-running evaluations

## 📋 Prerequisites

```bash
# Install required packages
pip install pandas numpy matplotlib seaborn tqdm aiohttp psutil sglang

# For scoreflow reward computation, ensure the server is running:
python ../scoreflow_reward_server.py
```

## 🎯 Quick Start

### 1. Using External API Models

```bash
# Create API configuration
cat > api_config.json << EOF
{
  "api_url": "https://api.openai.com/v1/chat/completions",
  "api_key": "your-api-key",
  "api_model": "gpt-4"
}
EOF

# Run evaluation
python evaluate_model.py \
  --api-config api_config.json \
  --test-data ../data/test_new/test.parquet \
  --output-dir ./results \
  --max-inference-workers 10 \
  --max-scoring-workers 5
```

### 2. Using Local Models (SGLang)

```bash
# Run evaluation with local model
python evaluate_model.py \
  --model-path /path/to/model/checkpoint \
  --test-data ../data/test_new/test.parquet \
  --output-dir ./results \
  --tensor-parallel 2 \
  --port 30000
```

### 3. Using Qwen API

```bash
# Create Qwen API configuration
cat > qwen_config.json << EOF
{
  "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
  "api_key": "your-qwen-api-key",
  "api_model": "qwen-max-latest"
}
EOF

# Run evaluation
python evaluate_model.py \
  --api-config qwen_config.json \
  --test-data ../data/test_new/test.parquet \
  --output-dir ./results
```

## 📁 Output Structure

```
results/
└── 20250114_103000_model_name/
    ├── summary_report.md          # Overall evaluation report
    ├── results.csv                 # All results in CSV format
    ├── gsm8k_results.jsonl        # Detailed results per benchmark
    ├── mbpp_results.jsonl
    ├── score_distribution.png     # Visualization plots
    ├── average_scores.png
    └── success_rates.png
```

## 🛠️ Advanced Usage

### Limiting Samples (for Testing)

```bash
python evaluate_model.py \
  --api-config api_config.json \
  --test-data ../data/test_new/test.parquet \
  --limit 10  # Only evaluate first 10 samples
```

### Custom Generation Parameters

```bash
python evaluate_model.py \
  --api-config api_config.json \
  --test-data ../data/test_new/test.parquet \
  --temperature 0.8 \
  --max-tokens 8192
```

### Batch Processing Configuration

```bash
python evaluate_model.py \
  --api-config api_config.json \
  --test-data ../data/test_new/test.parquet \
  --batch-size 50 \
  --max-inference-workers 20 \
  --max-scoring-workers 10
```

## 📊 Report Format

### Summary Report (Markdown)

The summary report includes:
- Configuration details
- Overall statistics
- Per-benchmark performance metrics
- Error analysis
- Sample outputs (best/worst examples)

### Detailed Results (JSONL)

Each line contains:
```json
{
  "prompt": "...",
  "response": "...",
  "workflow": "extracted workflow code",
  "score": 0.85,
  "success": true,
  "inference_time": 2.3,
  "scoring_time": 1.5,
  "metadata": {...}
}
```

## 🔧 Configuration Files

### API Configuration

```json
{
  "api_url": "https://api.example.com/v1/chat/completions",
  "api_key": "your-api-key",
  "api_model": "model-name"
}
```

### Supported APIs

- **OpenAI**: GPT-4, GPT-3.5-Turbo
- **Anthropic**: Claude-3 models
- **Qwen**: Qwen-Max, Qwen-Plus, Qwen-Turbo
- **DeepSeek**: DeepSeek-Chat, DeepSeek-Coder
- **Local**: Any OpenAI-compatible server (vLLM, TGI, etc.)

## 🐛 Troubleshooting

### SGLang Server Issues

```bash
# Check if port is in use
lsof -i :30000

# Kill existing process
kill -9 $(lsof -t -i:30000)

# Use different port
python evaluate_model.py --model-path /path/to/model --port 30001
```

### API Rate Limits

```bash
# Reduce concurrent workers
python evaluate_model.py \
  --api-config api_config.json \
  --test-data data.parquet \
  --max-inference-workers 5  # Reduce from default 10
```

### Memory Issues

```bash
# Process in smaller batches
python evaluate_model.py \
  --model-path /path/to/model \
  --test-data data.parquet \
  --batch-size 10  # Reduce from default 100
```

## 📈 Performance Tips

1. **For API models**: Increase `max-inference-workers` for better throughput
2. **For local models**: Use `tensor-parallel` and `data-parallel` for multi-GPU
3. **For large datasets**: Enable intermediate result saving (automatic)
4. **For debugging**: Use `--limit` to test with fewer samples first

## 🔗 Related Tools

- `scoreflow_reward_server.py`: Reward computation server (must be running)
- `generate_verl_data.py`: Generate test data in VERL format
- `../verl_support/`: Main VERL support directory

## 📝 Example Complete Workflow

```bash
# Step 1: Start scoreflow reward server (in separate terminal)
cd ..
python scoreflow_reward_server.py

# Step 2: Prepare API configuration
echo '{
  "api_url": "https://api.openai.com/v1/chat/completions",
  "api_key": "sk-...",
  "api_model": "gpt-4"
}' > api_config.json

# Step 3: Run evaluation
python evaluate_model.py \
  --api-config api_config.json \
  --test-data ../data/test_new/test.parquet \
  --output-dir ./evaluation_results \
  --max-inference-workers 10 \
  --temperature 0.7

# Step 4: View results
cat evaluation_results/*/summary_report.md
```

## 📄 License

This evaluation system is part of the Flow_RL project.