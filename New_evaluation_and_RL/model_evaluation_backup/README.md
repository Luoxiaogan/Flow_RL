# Model Evaluation Framework

A comprehensive framework for evaluating both local and API-based language models on various benchmarks.

**📁 Restructured Directory Organization**: This module has been reorganized with clean separation between configurations, scripts, and core functionality for better maintainability.

## 📁 Directory Structure

```
model_evaluation/
├── configs/                    # Configuration files
│   ├── evaluation_config.yaml  # Single model evaluation config  
│   ├── example_config.yaml     # Example configuration template
│   └── models_config.yaml      # Batch evaluation models config
├── scripts/                    # Executable scripts and entry points
│   ├── evaluate_all_models.sh  # Unified model evaluation (Linux/macOS)
│   ├── evaluate_all_models.bat # Unified model evaluation (Windows)
│   ├── evaluate_models.sh      # Legacy batch evaluation (Linux/macOS) 
│   ├── evaluate_models.bat     # Legacy batch evaluation (Windows)
│   ├── run_evaluation.py       # Single model evaluation entry
│   └── run_unified_evaluation.py # Unified evaluation entry
├── core/                       # Core functionality by component type
│   ├── __init__.py
│   ├── interfaces/             # Model interface abstractions
│   │   ├── __init__.py
│   │   ├── model_interface.py      # Base interface for all models
│   │   ├── local_model_interface.py # Local model implementation
│   │   └── api_model_interface.py   # API model implementation  
│   ├── evaluators/             # Batch and unified evaluation logic
│   │   ├── __init__.py
│   │   ├── model_evaluator.py      # Core evaluation logic
│   │   ├── batch_evaluator.py      # Batch evaluation orchestration
│   │   └── unified_batch_evaluator.py # Advanced unified evaluation
│   └── utils/                  # Supporting utilities and helpers
│       ├── __init__.py
│       ├── api_connection_pool.py  # API connection management
│       ├── config_validator.py     # Configuration validation
│       ├── model_factory.py        # Model creation factory
│       ├── report_generator.py     # Results reporting & visualization
│       ├── resource_manager.py     # GPU resource management
│       ├── reward_server_checker.py # Health checks for reward server
│       └── score_collector.py      # Score collection and processing
└── __init__.py                 # Main module entry (backward compatible)
```

## 🚀 Quick Start

### Prerequisites

1. **Environment Setup**
   ```bash
   # Linux/macOS
   source /opt/anaconda3/etc/profile.d/conda.sh
   conda activate workflow
   
   # Windows
   conda activate workflow
   ```

2. **Required Dependencies**
   ```bash
   pip install torch transformers aiohttp peft bitsandbytes pandas matplotlib seaborn tqdm pyyaml
   ```

3. **Start Reward Server** (Required)
   ```bash
   # Linux/macOS/WSL
   bash ../servers_and_proxy/start_scoreflow_reward.sh
   
   # Windows
   ..\servers_and_proxy\start_scoreflow_reward.bat
   ```

### Usage Examples

#### 1. Unified Model Evaluation (Recommended)

**Linux/macOS:**
```bash
cd scripts/
./evaluate_all_models.sh
```

**Windows:**
```batch
cd scripts
evaluate_all_models.bat
```

**With Parameters:**
```bash
# Linux/macOS
./evaluate_all_models.sh -c ../configs/models_config.yaml -n 100 -o ../results -f api

# Windows  
evaluate_all_models.bat -c ..\configs\models_config.yaml -n 100 -o ..\results -f api
```

#### 2. Single Model Evaluation

```bash
cd scripts/
python run_evaluation.py --config ../configs/evaluation_config.yaml --max-samples 50
```

#### 3. Custom Unified Evaluation

```bash
cd scripts/
python run_unified_evaluation.py --config ../configs/models_config.yaml --batch-size 4
```

## ⚙️ Configuration

### Unified Models Configuration (`configs/models_config.yaml`)

```yaml
models:
  # Local models
  - name: "llama-3-8b-instruct" 
    type: "local"
    model_path: "/path/to/model"
    load_in_4bit: true
    generation_params:
      max_new_tokens: 4096
      temperature: 0.7
    
  # API models  
  - name: "gpt-4"
    type: "api"
    api_base: "https://api.openai.com/v1"
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
    generation_params:
      max_new_tokens: 4096
      temperature: 0.8

evaluation:
  benchmark: "gsm8k"          # gsm8k, mbpp, hotpotqa, etc.
  max_samples: 100            # Number of test samples 
  batch_size: 4               # Processing batch size
  timeout: 180                # Timeout per evaluation (seconds)
  
output:
  save_results: true
  output_dir: "./evaluation_results"
  generate_report: true
  save_detailed_csv: true
```

### Single Model Configuration (`configs/evaluation_config.yaml`)

```yaml
model:
  name: "test-model"
  type: "local"              # or "api"
  model_path: "/path/to/model"
  generation_params:
    max_new_tokens: 4096
    temperature: 0.7
    
evaluation:
  benchmark: "gsm8k" 
  max_samples: 50
  batch_size: 2
  
output:
  output_dir: "./results"
  generate_charts: true
```

## 📊 Command Line Options

### Unified Evaluation Script Options

```bash
Options:
  -c, --config FILE      Model config file (default: ../configs/models_config.yaml)
  -n, --max-samples N    Maximum evaluation samples
  -o, --output-dir DIR   Output directory
  -b, --batch-size N     Batch processing size  
  -f, --filter TYPE      Filter model types (api/local/etc.)
  -l, --limit N          Limit number of models to evaluate
  -y, --yes              Skip confirmation prompts
  -h, --help             Show help information
```

### Single Model Evaluation Options

```bash
Options:
  --config, -c           Configuration file path
  --test-data, -t        Test data file path  
  --max-samples, -n      Maximum number of samples
  --output-dir, -o       Output directory
  --batch-size, -b       Batch size for processing
  --log-level, -l        Logging level (DEBUG/INFO/WARNING/ERROR)
  --yes, -y              Skip confirmation prompts
```

## 🔧 Architecture & Features

### Core Design Principles

1. **Separation of Concerns**: Clean separation between configs, scripts, and core logic
2. **Unified Interface**: Single interface for local and API models
3. **Resource Management**: Intelligent GPU memory management for local models  
4. **Async Processing**: Efficient concurrent evaluation with connection pooling
5. **Health Monitoring**: Automatic reward server health checks
6. **Rich Reporting**: Comprehensive evaluation reports with visualizations

### Key Components

- **Interfaces**: Abstract model interfaces supporting both local and API models
- **Evaluators**: Batch processing logic with advanced resource management
- **Utils**: Supporting utilities for validation, reporting, and infrastructure

### Import Usage (Backward Compatible)

```python
# Main imports - fully backward compatible
from model_evaluation import (
    BatchModelEvaluator,
    UnifiedBatchEvaluator, 
    BaseModelInterface,
    LocalModelInterface,
    APIModelInterface,
    ModelFactory,
    RewardServerChecker,
    ScoreCollector
)

# Direct imports from organized structure
from model_evaluation.core.interfaces import LocalModelInterface
from model_evaluation.core.evaluators import UnifiedBatchEvaluator  
from model_evaluation.core.utils import ModelFactory, ReportGenerator
```

## 📈 Output Structure

```
evaluation_results/
├── model_*.json                # Individual model detailed reports
├── model_*.md                  # Human-readable markdown reports  
├── model_comparison.json       # Cross-model comparison data
├── model_comparison.md         # Comparison summary report
├── detailed_results.csv        # Complete results in CSV format
├── charts/                     # Generated visualization charts
│   ├── overall_scores.png      # Score comparison bar chart
│   ├── benchmark_heatmap.png   # Performance heatmap  
│   └── model_rankings.png      # Ranking visualization
└── logs/
    ├── evaluation_*.log        # Detailed execution logs
    └── error_*.log             # Error tracking logs
```

## 🛠️ Development & Extensibility

### Adding New Model Types

1. Create new interface in `core/interfaces/`
2. Extend `BaseModelInterface` 
3. Update `ModelFactory` in `core/utils/model_factory.py`
4. Add configuration examples and tests

### Adding New Benchmarks

1. Update evaluation logic in `core/evaluators/`
2. Add benchmark-specific configuration schemas
3. Update reward server integration if needed
4. Add validation and error handling

### Custom Evaluation Metrics

1. Extend `ScoreCollector` in `core/utils/score_collector.py`  
2. Update report generation in `ReportGenerator`
3. Add new visualization types if needed

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors After Restructuring**
   ```bash
   # Ensure proper PYTHONPATH
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   
   # Test imports
   python -c "from model_evaluation import BatchModelEvaluator; print('OK')"
   ```

2. **Reward Server Connection Issues**  
   ```bash
   # Check health
   curl -s http://localhost:8899/health
   
   # Restart if needed
   bash ../servers_and_proxy/start_scoreflow_reward.sh
   ```

3. **Configuration File Not Found**
   ```bash
   # Ensure running from correct directory
   cd scripts/  
   ls ../configs/  # Should show yaml files
   ```

4. **GPU Memory Issues**
   - Reduce `batch_size` in configuration
   - Use smaller `max_samples` for testing  
   - Enable 4-bit quantization for local models

5. **Windows Batch Script Encoding Issues**
   ```batch
   # Test encoding display
   cd scripts
   test_encoding.bat
   
   # If Chinese characters don't display correctly:
   # - Ensure terminal supports UTF-8 (Windows Terminal recommended)
   # - Scripts automatically set UTF-8 code page (chcp 65001)
   # - Status messages use [OK], [WARNING], [ERROR] instead of symbols
   ```

### Health Checks

```bash
# Verify directory structure
ls -la configs/ scripts/ core/

# Test Python module structure  
cd model_evaluation
python -c "from core.utils import RewardServerChecker; print('Module structure OK')"

# Validate configuration
cd scripts/
python -c "import yaml; print(yaml.safe_load(open('../configs/example_config.yaml')))"
```

## 📄 Migration from Old Structure

The restructuring maintains full backward compatibility:

- All existing import statements continue to work
- Configuration file paths are automatically updated in scripts
- Old script names and parameters remain functional  
- API interfaces remain unchanged

**New structure benefits:**
- Better code organization and maintainability
- Clearer separation of concerns
- Easier testing and debugging
- Improved IDE support and navigation

## 📝 License  

Part of the Flow_RL project - see main project documentation for license details.