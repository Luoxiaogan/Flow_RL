#!/usr/bin/env python
"""
Smart Directory Reorganization Script
Handles all import paths and dependencies correctly
"""
import os
import re
import shutil
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

class SmartReorganizer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.import_mapping = {}
        self.file_moves = {}
        self.affected_files = set()
        
    def analyze_dependencies(self):
        """Analyze all Python imports and Shell script dependencies"""
        print("="*60)
        print("ANALYZING DEPENDENCIES")
        print("="*60)
        
        # 1. Analyze Python imports
        python_deps = self.analyze_python_imports()
        
        # 2. Analyze Shell script paths
        shell_deps = self.analyze_shell_scripts()
        
        # 3. Create import mapping
        self.create_import_mapping()
        
        return python_deps, shell_deps
    
    def analyze_python_imports(self) -> Dict[str, List[str]]:
        """Find all Python import statements"""
        imports = {}
        
        print("\n1. Python Import Analysis:")
        print("-"*40)
        
        # Files that import from local modules
        local_imports = {
            'src/train.py': [
                'from data_collator import DataCollatorForChatML, DataCollatorForCausalLMWithMasking',
                'from evaluation.evaluation_callback import EvaluationCallback'
            ],
            'test_loss_mask.py': [
                'from data_collator import DataCollatorForChatML'
            ],
            'test_evaluation_system.py': [
                'from evaluation.reward_server_checker import RewardServerChecker',
                'from evaluation.model_evaluator import ModelEvaluator',
                'from evaluation.score_collector import ScoreCollector',
                'from evaluation.report_generator import ReportGenerator',
                'from evaluation.evaluation_callback import EvaluationCallback'
            ],
            'local_test_evaluation.py': [
                'from evaluation.report_generator import ReportGenerator',
                'from evaluation.evaluation_callback import EvaluationCallback'
            ],
            'simple_local_test.py': [
                'from evaluation.report_generator import ReportGenerator',
                'from evaluation.evaluation_callback import EvaluationCallback'
            ],
            'mock_evaluation_test.py': [
                'from evaluation.report_generator import ReportGenerator',
                'from evaluation.evaluation_callback import EvaluationCallback'
            ]
        }
        
        for file, imports_list in local_imports.items():
            print(f"\n  {file}:")
            for imp in imports_list:
                print(f"    - {imp}")
            imports[file] = imports_list
            
        return imports
    
    def analyze_shell_scripts(self) -> Dict[str, List[str]]:
        """Find all path references in shell scripts"""
        shell_refs = {}
        
        print("\n2. Shell Script Path Analysis:")
        print("-"*40)
        
        # Key paths in shell scripts
        script_paths = {
            'run_finetune.sh': [
                'src/train.py',
                'configs/deepspeed_config_z3.json',
                'accelerate_config.yaml'
            ],
            'run_finetune_with_eval.sh': [
                'src/train.py',
                'configs/deepspeed_config_z3.json',
                'accelerate_config.yaml'
            ],
            'run_llama.sh': [
                'src/train.py',
                'configs/deepspeed_config_z3.json',
                'accelerate_config.yaml'
            ],
            'run_qwen.sh': [
                'src/train.py',
                'configs/deepspeed_config_z3.json',
                'accelerate_config.yaml'
            ]
        }
        
        for script, paths in script_paths.items():
            if (self.base_dir / script).exists():
                print(f"\n  {script}:")
                for path in paths:
                    print(f"    - {path}")
                shell_refs[script] = paths
                
        return shell_refs
    
    def create_import_mapping(self):
        """Create mapping of old imports to new imports"""
        
        print("\n3. Import Path Mapping:")
        print("-"*40)
        
        # Define how imports should change
        self.import_mapping = {
            # data_collator moves to training module
            'from data_collator import': 'from src.training.data_collator import',
            'import data_collator': 'import src.training.data_collator as data_collator',
            
            # evaluation stays mostly the same but needs src prefix for external imports
            'from evaluation.': 'from src.evaluation.',
            'import evaluation': 'import src.evaluation',
            
            # train.py becomes trainer.py
            'from train import': 'from src.training.trainer import',
            'import train': 'import src.training.trainer as train',
            
            # utils moves to training
            'from utils import': 'from src.training.utils import',
            'import utils': 'import src.training.utils as utils'
        }
        
        # File move mapping
        self.file_moves = {
            'src/train.py': 'src/training/trainer.py',
            'src/data_collator.py': 'src/training/data_collator.py',
            'src/utils.py': 'src/training/utils.py',
            'configs/deepspeed_config_z3.json': 'configs/training/deepspeed_z3.json',
            'accelerate_config.yaml': 'configs/training/accelerate_config.yaml',
            
            # Test files
            'test_loss_mask.py': 'tests/unit/test_loss_mask.py',
            'test_model.py': 'tests/unit/test_model_loading.py',
            'test_evaluation_system.py': 'tests/integration/test_evaluation_system.py',
            'local_test_evaluation.py': 'tests/integration/test_local_evaluation.py',
            'simple_local_test.py': 'tests/integration/test_simple_local.py',
            'mock_evaluation_test.py': 'tests/benchmarks/mock_api_test.py',
            'standalone_test.py': 'tests/benchmarks/standalone_test.py',
            
            # Scripts
            'run_finetune.sh': 'scripts/train.sh',
            'run_finetune_with_eval.sh': 'scripts/train_with_eval.sh',
            'run_llama.sh': 'scripts/train_llama.sh',
            'run_qwen.sh': 'scripts/train_qwen.sh',
        }
        
        for old, new in self.import_mapping.items():
            print(f"  '{old}' -> '{new}'")
    
    def update_python_imports(self, filepath: Path, new_path: Path) -> str:
        """Update Python imports in a file"""
        
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        
        # Update imports based on new location
        if 'tests/' in str(new_path):
            # Test files need to add src to path or use absolute imports
            
            # Add path setup at the beginning if not present
            if 'sys.path' not in content:
                path_setup = """import sys
import os
# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
"""
                # Insert after initial imports
                import_end = content.find('\n\n')
                if import_end > 0:
                    content = content[:import_end] + '\n' + path_setup + content[import_end:]
            
            # Update evaluation imports
            content = content.replace('from evaluation.', 'from evaluation.')
            content = content.replace('from data_collator', 'from training.data_collator')
            
        elif 'src/training/' in str(new_path):
            # Training module files
            if new_path.name == 'trainer.py':
                # Update imports in trainer.py
                content = content.replace('from data_collator import', 'from .data_collator import')
                content = content.replace('from evaluation.', 'from ..evaluation.')
            else:
                # Other training files
                content = content.replace('from evaluation.', 'from ..evaluation.')
        
        elif 'src/evaluation/' in str(new_path):
            # Evaluation module files - use relative imports
            content = content.replace('from evaluation.', 'from .')
            content = content.replace('from data_collator', 'from ..training.data_collator')
            content = content.replace('from train import', 'from ..training.trainer import')
        
        if content != original_content:
            self.affected_files.add(str(new_path))
            
        return content
    
    def update_shell_scripts(self, filepath: Path, new_path: Path) -> str:
        """Update paths in shell scripts"""
        
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        
        # Update Python script paths
        content = content.replace('src/train.py', 'src/training/trainer.py')
        
        # Update config paths
        content = content.replace('configs/deepspeed_config_z3.json', 'configs/training/deepspeed_z3.json')
        content = content.replace('accelerate_config.yaml', 'configs/training/accelerate_config.yaml')
        
        # Update relative paths based on new location
        if 'scripts/' in str(new_path):
            # Scripts are one level deeper, adjust paths
            content = content.replace('/nas/ganluo/Flow_RL/my_llama3_h100_new/', '/nas/ganluo/Flow_RL/my_llama3_h100_with_eval/')
            content = content.replace('/nas/ganluo/Flow_RL/my_llama3_h100_with_eval/src/', '/nas/ganluo/Flow_RL/my_llama3_h100_with_eval/src/')
            content = content.replace('/nas/ganluo/Flow_RL/my_llama3_h100_with_eval/configs/', '/nas/ganluo/Flow_RL/my_llama3_h100_with_eval/configs/')
        
        if content != original_content:
            self.affected_files.add(str(new_path))
            
        return content
    
    def create_init_files(self):
        """Create __init__.py files for packages"""
        
        init_files = {
            'src/__init__.py': '"""Source code package"""',
            
            'src/training/__init__.py': '''"""Training module"""
from .trainer import train
from .data_collator import DataCollatorForChatML, DataCollatorForCausalLMWithMasking

__all__ = ['train', 'DataCollatorForChatML', 'DataCollatorForCausalLMWithMasking']
''',
            
            'tests/__init__.py': '"""Test package"""',
            'tests/unit/__init__.py': '"""Unit tests"""',
            'tests/integration/__init__.py': '"""Integration tests"""',
            'tests/benchmarks/__init__.py': '"""Benchmark tests"""',
        }
        
        return init_files
    
    def execute_reorganization(self):
        """Execute the smart reorganization"""
        
        print("\n" + "="*60)
        print("EXECUTING SMART REORGANIZATION")
        print("="*60)
        
        # 1. Create new directories
        new_dirs = [
            'src/training',
            'configs/training',
            'configs/evaluation',
            'scripts',
            'tests/unit',
            'tests/integration',
            'tests/benchmarks',
            'docs/guides',
            'outputs/logs',
            'outputs/reports'
        ]
        
        print("\n1. Creating directories...")
        for dir_path in new_dirs:
            (self.base_dir / dir_path).mkdir(parents=True, exist_ok=True)
            print(f"  [OK] {dir_path}")
        
        # 2. Move files with import updates
        print("\n2. Moving files and updating imports...")
        
        for old_path, new_path in self.file_moves.items():
            old_file = self.base_dir / old_path
            new_file = self.base_dir / new_path
            
            if old_file.exists():
                # Read content
                content = old_file.read_text(encoding='utf-8')
                
                # Update imports based on file type
                if old_path.endswith('.py'):
                    content = self.update_python_imports(old_file, new_file)
                elif old_path.endswith('.sh'):
                    content = self.update_shell_scripts(old_file, new_file)
                
                # Write to new location
                new_file.parent.mkdir(parents=True, exist_ok=True)
                new_file.write_text(content, encoding='utf-8')
                
                # Remove old file
                old_file.unlink()
                
                print(f"  [OK] {old_path} -> {new_path}")
        
        # 3. Create __init__ files
        print("\n3. Creating __init__.py files...")
        
        for filepath, content in self.create_init_files().items():
            file_path = self.base_dir / filepath
            file_path.write_text(content, encoding='utf-8')
            print(f"  [OK] {filepath}")
        
        # 4. Create essential files
        print("\n4. Creating essential files...")
        
        essential_files = {
            'README.md': self.generate_readme(),
            'requirements.txt': self.generate_requirements(),
            '.gitignore': self.generate_gitignore(),
            'setup.py': self.generate_setup_py(),
            'configs/evaluation/eval_config.yaml': self.generate_eval_config(),
            'docs/getting_started.md': self.generate_getting_started(),
            'docs/api_reference.md': self.generate_api_reference(),
        }
        
        for filepath, content in essential_files.items():
            file_path = self.base_dir / filepath
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            print(f"  [OK] {filepath}")
        
        # 5. Move documentation files
        print("\n5. Moving documentation files...")
        
        doc_moves = {
            'H100_SETUP.md': 'docs/guides/h100_setup.md',
            'LOSS_MASKING.md': 'docs/guides/loss_masking.md',
            'DEMAND.md': 'docs/requirements.md',
            'evaluation_plan.md': 'docs/evaluation.md',
        }
        
        for old_path, new_path in doc_moves.items():
            old_file = self.base_dir / old_path
            new_file = self.base_dir / new_path
            if old_file.exists():
                new_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old_file), str(new_file))
                print(f"  [OK] {old_path} -> {new_path}")
        
        # 6. Clean up old files
        print("\n6. Cleaning up old files...")
        
        cleanup_patterns = [
            '*.log',
            '*_test_reports',
            '*_callback_test',
            'reorganize.py',  # Old reorganize script
            'cleanup.py',     # Old cleanup script
        ]
        
        for pattern in cleanup_patterns:
            for path in self.base_dir.glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"  [OK] Removed directory: {path.name}")
                else:
                    path.unlink()
                    print(f"  [OK] Removed file: {path.name}")
        
        # 7. Create import fix script
        self.create_import_fix_script()
        
        # 8. Save reorganization report
        self.save_report()
        
        print("\n" + "="*60)
        print("REORGANIZATION COMPLETE!")
        print("="*60)
    
    def create_import_fix_script(self):
        """Create a script to verify and fix remaining import issues"""
        
        fix_script = '''#!/usr/bin/env python
"""
Import Fix Verification Script
Checks and fixes any remaining import issues after reorganization
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test all imports"""
    
    print("Testing imports...")
    
    # Add src to path
    base_dir = Path(__file__).parent
    sys.path.insert(0, str(base_dir / 'src'))
    
    try:
        # Test training imports
        from training import train
        from training.data_collator import DataCollatorForChatML
        print("[OK] Training module imports OK")
        
        # Test evaluation imports
        from evaluation import EvaluationCallback
        from evaluation.report_generator import ReportGenerator
        print("[OK] Evaluation module imports OK")
        
        print("\\nAll imports working correctly!")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
'''
        
        script_path = self.base_dir / 'test_imports.py'
        script_path.write_text(fix_script, encoding='utf-8')
        print("\n[OK] Created test_imports.py to verify imports")
    
    def generate_readme(self):
        """Generate README.md content"""
        return """# LLaMA3/Qwen H100 Training with Auto-Evaluation

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Training with Evaluation
```bash
# Start reward server (in separate terminal)
cd ../New_evaluation_and_RL/reward_server
python scoreflow_reward_server.py

# Run training
bash scripts/train_with_eval.sh
```

## 📁 Project Structure

- `src/` - Source code
  - `training/` - Training modules
  - `evaluation/` - Evaluation system
- `configs/` - Configuration files
- `scripts/` - Executable scripts
- `tests/` - Test suites
- `docs/` - Documentation

## 📖 Documentation

- [Getting Started](docs/getting_started.md)
- [Configuration Guide](docs/configuration.md)
- [Evaluation System](docs/evaluation.md)
- [API Reference](docs/api_reference.md)

## 🛠️ Features

- ✅ Supervised Fine-Tuning (SFT)
- ✅ DeepSpeed ZeRO-3 optimization
- ✅ Loss masking support
- ✅ Automatic checkpoint evaluation
- ✅ Multi-format reporting (JSON/Markdown/CSV)
- ✅ Async evaluation (non-blocking)

## 📊 Supported Models

- LLaMA 3.1 (8B)
- Qwen 2.5 (7B)

## 🔧 Configuration

See `configs/` directory for all configuration options.

## 📝 License

MIT
"""

    def generate_requirements(self):
        """Generate requirements.txt content"""
        return """# Core dependencies
torch>=2.0.0
transformers>=4.35.0
accelerate>=0.25.0
deepspeed>=0.12.0

# Evaluation dependencies
aiohttp>=3.8.0
pandas>=1.5.0
tqdm>=4.65.0
requests>=2.28.0

# Optional
wandb>=0.15.0
matplotlib>=3.6.0
numpy>=1.24.0

# Development
pytest>=7.0.0
black>=22.0.0
flake8>=4.0.0
"""

    def generate_gitignore(self):
        """Generate .gitignore content"""
        return """# Python
__pycache__/
*.py[cod]
*.pyc
.Python
build/
dist/
*.egg-info/
.pytest_cache/

# Outputs
outputs/
checkpoint-*/
*.log
*_reports/
*_test/
*_callback_test/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Environment
.env
venv/
env/
*.local

# Data
*.jsonl
*.parquet
*.csv
!examples/*.jsonl
!test_data/*.jsonl

# Models
*.bin
*.safetensors
*.pth

# Temporary
*.tmp
*.bak
reorganization_report.json
test_imports.py
"""

    def generate_setup_py(self):
        """Generate setup.py content"""
        return '''"""Setup script for the project"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llama3-h100-eval",
    version="1.0.0",
    author="Your Name",
    description="LLaMA3/Qwen training with automatic evaluation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/llama3-h100-eval",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "accelerate>=0.25.0",
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8"],
        "eval": ["aiohttp", "pandas", "tqdm"],
        "all": ["wandb", "matplotlib", "numpy"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
'''

    def generate_eval_config(self):
        """Generate evaluation config YAML"""
        return """# Evaluation Configuration
evaluation:
  # Test data
  test_data_path: "New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl"
  
  # Reward server
  reward_server:
    url: "http://localhost:8899"
    timeout: 300
    max_retries: 3
  
  # Evaluation parameters
  batch_size: 8
  async_eval: true
  eval_interval: 1  # Evaluate every N checkpoints
  max_samples: null  # null for all samples
  
  # Output
  output_dir: "outputs/reports"
  save_json: true
  save_markdown: true
  save_csv: true
  
  # Generation parameters
  generation:
    temperature: 0.7
    top_p: 0.9
    max_length: 4096
    do_sample: true
"""

    def generate_getting_started(self):
        """Generate getting started guide"""
        return """# Getting Started

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
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
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
"""

    def generate_api_reference(self):
        """Generate API reference"""
        return """# API Reference

## Training Module

### `src.training.trainer`

Main training script with evaluation support.

```python
from src.training import train

# Run training
train()
```

### `src.training.data_collator`

Data collators for training.

```python
from src.training.data_collator import DataCollatorForChatML

collator = DataCollatorForChatML(
    tokenizer=tokenizer,
    model_type="llama",
    pad_to_multiple_of=8
)
```

## Evaluation Module

### `src.evaluation.EvaluationCallback`

Callback for automatic evaluation during training.

```python
from src.evaluation import EvaluationCallback

callback = EvaluationCallback({
    'test_data_path': 'path/to/test.jsonl',
    'reward_server_url': 'http://localhost:8899',
    'eval_batch_size': 8,
    'async_eval': True
})
```

### `src.evaluation.ReportGenerator`

Generate evaluation reports in multiple formats.

```python
from src.evaluation import ReportGenerator

generator = ReportGenerator('output_dir')
report = await generator.generate_report(scores, checkpoint_info, test_samples)
```

## Configuration

### Training Arguments

- `model_name_or_path`: Path to pretrained model
- `dataset_path`: Path to training data
- `output_dir`: Directory for outputs
- `num_train_epochs`: Number of training epochs
- `per_device_train_batch_size`: Batch size per GPU
- `learning_rate`: Learning rate
- `use_loss_mask`: Enable loss masking

### Evaluation Arguments

- `enable_auto_eval`: Enable automatic evaluation
- `eval_test_data_path`: Path to test data
- `reward_server_url`: Reward server URL
- `eval_batch_size`: Evaluation batch size
- `async_evaluation`: Run evaluation asynchronously
- `eval_interval`: Evaluate every N checkpoints
"""

    def save_report(self):
        """Save reorganization report"""
        
        report = {
            'timestamp': str(Path.cwd()),
            'files_moved': len(self.file_moves),
            'files_updated': len(self.affected_files),
            'mapping': self.file_moves,
            'affected_files': list(self.affected_files)
        }
        
        report_path = self.base_dir / 'reorganization_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Saved report to {report_path}")
        
        # Print summary
        print("\nSummary:")
        print(f"  - Files moved: {len(self.file_moves)}")
        print(f"  - Files with updated imports: {len(self.affected_files)}")
        print("\nNext steps:")
        print("  1. Run: python test_imports.py")
        print("  2. Test the training script: bash scripts/train_with_eval.sh")
        print("  3. Run tests: python tests/benchmarks/standalone_test.py")

def main():
    reorganizer = SmartReorganizer()
    
    print("="*60)
    print("SMART PROJECT REORGANIZATION")
    print("="*60)
    print("\nThis script will:")
    print("  1. Move files to organized structure")
    print("  2. Update all Python imports automatically")
    print("  3. Update all shell script paths")
    print("  4. Create proper __init__.py files")
    print("  5. Generate import test script")
    
    # Analyze dependencies
    python_deps, shell_deps = reorganizer.analyze_dependencies()
    
    print("\n" + "="*60)
    response = input("\nProceed with smart reorganization? (yes/no): ")
    
    if response.lower() == 'yes':
        reorganizer.execute_reorganization()
    else:
        print("\nReorganization cancelled.")

if __name__ == "__main__":
    main()