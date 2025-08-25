#!/usr/bin/env python
"""
Directory reorganization script for my_llama3_h100_with_eval
Safely reorganizes the project structure
"""
import os
import shutil
from pathlib import Path
import json

class ProjectReorganizer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.operations = []
        self.file_mapping = {}
        
    def plan_reorganization(self):
        """Plan the reorganization without executing"""
        print("="*60)
        print("PROJECT REORGANIZATION PLAN")
        print("="*60)
        
        # 1. Create new directories
        new_dirs = [
            "src/training",
            "configs/training",
            "configs/evaluation",
            "scripts/utils",
            "tests/unit",
            "tests/integration",
            "tests/benchmarks",
            "docs/guides",
            "examples",
            "tools",
            "outputs/checkpoints",
            "outputs/logs",
            "outputs/reports",
            "outputs/cache"
        ]
        
        print("\n1. NEW DIRECTORIES TO CREATE:")
        for dir_path in new_dirs:
            full_path = self.base_dir / dir_path
            print(f"   [+] {dir_path}")
            self.operations.append(('mkdir', full_path))
        
        # 2. Files to move
        print("\n2. FILES TO MOVE:")
        
        moves = {
            # Training module
            "src/train.py": "src/training/trainer.py",
            "src/data_collator.py": "src/training/data_collator.py",
            "src/utils.py": "src/training/utils.py",
            
            # Config files
            "accelerate_config.yaml": "configs/training/accelerate_config.yaml",
            "configs/deepspeed_config_z3.json": "configs/training/deepspeed_z3.json",
            
            # Scripts
            "run_finetune.sh": "scripts/train.sh",
            "run_finetune_with_eval.sh": "scripts/train_with_eval.sh",
            "run_llama.sh": "scripts/train_llama.sh",
            "run_qwen.sh": "scripts/train_qwen.sh",
            "run_all.sh": "scripts/train_all.sh",
            
            # Analysis tools
            "analysis_training_data_first.py": "scripts/utils/analyze_data.py",
            "analysis_using_real_tokenizer.py": "scripts/utils/analyze_tokenizer.py",
            "training_data_template.py": "scripts/utils/data_template.py",
            
            # Unit tests
            "test_loss_mask.py": "tests/unit/test_loss_mask.py",
            "test_model.py": "tests/unit/test_model_loading.py",
            
            # Integration tests
            "test_evaluation_system.py": "tests/integration/test_evaluation_system.py",
            "local_test_evaluation.py": "tests/integration/test_local_evaluation.py",
            "simple_local_test.py": "tests/integration/test_simple_local.py",
            
            # Benchmark tests
            "standalone_test.py": "tests/benchmarks/standalone_test.py",
            "mock_evaluation_test.py": "tests/benchmarks/mock_api_test.py",
            
            # Documentation
            "H100_SETUP.md": "docs/guides/h100_setup.md",
            "LOSS_MASKING.md": "docs/guides/loss_masking.md",
            "DEMAND.md": "docs/requirements.md",
            "evaluation_plan.md": "docs/evaluation.md",
            
            # Tools
            "cleanup.py": "tools/cleanup.py",
        }
        
        for src, dst in moves.items():
            src_path = self.base_dir / src
            dst_path = self.base_dir / dst
            if src_path.exists():
                print(f"   {src} -> {dst}")
                self.operations.append(('move', src_path, dst_path))
                self.file_mapping[src] = dst
        
        # 3. Files to create
        print("\n3. NEW FILES TO CREATE:")
        
        new_files = {
            "README.md": self.generate_readme(),
            "requirements.txt": self.generate_requirements(),
            ".gitignore": self.generate_gitignore(),
            "setup.py": self.generate_setup_py(),
            "configs/evaluation/eval_config.yaml": self.generate_eval_config(),
            "src/__init__.py": "",
            "src/training/__init__.py": "from .trainer import train",
            "tests/__init__.py": "",
            "tests/unit/__init__.py": "",
            "tests/integration/__init__.py": "",
            "tests/benchmarks/__init__.py": "",
        }
        
        for filepath, content in new_files.items():
            print(f"   [+] {filepath}")
            self.operations.append(('create', self.base_dir / filepath, content))
        
        # 4. Files to delete (logs and temp files)
        print("\n4. FILES TO DELETE:")
        
        delete_patterns = [
            "*.log",
            "*_test_reports",
            "*_callback_test",
            "reorganize.py",  # This script itself
        ]
        
        for pattern in delete_patterns:
            for path in self.base_dir.glob(pattern):
                print(f"   [-] {path.name}")
                self.operations.append(('delete', path))
        
        # 5. Update imports
        print("\n5. IMPORTS TO UPDATE:")
        print("   - Update train.py imports in evaluation_callback.py")
        print("   - Update relative imports in moved files")
        
        return self.operations
    
    def generate_readme(self):
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
        return """# Core dependencies
torch>=2.0.0
transformers>=4.35.0
accelerate>=0.25.0
deepspeed>=0.12.0

# Evaluation dependencies
aiohttp>=3.8.0
pandas>=1.5.0
tqdm>=4.65.0

# Optional
wandb>=0.15.0
matplotlib>=3.6.0
"""
    
    def generate_gitignore(self):
        return """# Python
__pycache__/
*.py[cod]
*.pyc
.Python
build/
dist/
*.egg-info/

# Outputs
outputs/
checkpoint-*/
*.log
*_reports/
*_test/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
venv/
env/

# Local configs
local_*.yaml
local_*.json
*.local

# Data
*.jsonl
*.parquet
*.csv
!examples/*.jsonl
"""
    
    def generate_setup_py(self):
        return '''"""Setup script for the project"""
from setuptools import setup, find_packages

setup(
    name="llama3-h100-eval",
    version="1.0.0",
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
    },
)
'''
    
    def generate_eval_config(self):
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
"""
    
    def update_imports(self):
        """Update import statements in moved files"""
        updates = [
            # Update evaluation_callback.py
            {
                "file": "src/evaluation/evaluation_callback.py",
                "old": "from evaluation.",
                "new": "from src.evaluation."
            },
            # More updates as needed
        ]
        
        for update in updates:
            filepath = self.base_dir / update["file"]
            if filepath.exists():
                content = filepath.read_text()
                content = content.replace(update["old"], update["new"])
                filepath.write_text(content)
                print(f"   Updated imports in {update['file']}")
    
    def execute_reorganization(self):
        """Execute the planned reorganization"""
        print("\n" + "="*60)
        print("EXECUTING REORGANIZATION")
        print("="*60)
        
        for operation in self.operations:
            try:
                if operation[0] == 'mkdir':
                    operation[1].mkdir(parents=True, exist_ok=True)
                    print(f"✓ Created directory: {operation[1].relative_to(self.base_dir)}")
                
                elif operation[0] == 'move':
                    src, dst = operation[1], operation[2]
                    if src.exists():
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(src), str(dst))
                        print(f"✓ Moved: {src.name} -> {dst.relative_to(self.base_dir)}")
                
                elif operation[0] == 'create':
                    filepath, content = operation[1], operation[2]
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    filepath.write_text(content)
                    print(f"✓ Created: {filepath.relative_to(self.base_dir)}")
                
                elif operation[0] == 'delete':
                    path = operation[1]
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    print(f"✓ Deleted: {path.name}")
                    
            except Exception as e:
                print(f"✗ Failed: {operation} - {e}")
        
        # Update imports
        self.update_imports()
        
        # Save mapping for reference
        mapping_file = self.base_dir / "reorganization_mapping.json"
        with open(mapping_file, 'w') as f:
            json.dump(self.file_mapping, f, indent=2)
        print(f"\n✓ Saved file mapping to: {mapping_file}")
        
        print("\n" + "="*60)
        print("REORGANIZATION COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Review the new structure")
        print("2. Test imports: python -c 'from src.training import train'")
        print("3. Run tests: pytest tests/")
        print("4. Update any hardcoded paths in scripts")

def main():
    reorganizer = ProjectReorganizer()
    
    # Plan the reorganization
    operations = reorganizer.plan_reorganization()
    
    print("\n" + "="*60)
    print(f"Total operations planned: {len(operations)}")
    print("="*60)
    
    # Show summary
    op_types = {}
    for op in operations:
        op_types[op[0]] = op_types.get(op[0], 0) + 1
    
    print("\nOperation Summary:")
    for op_type, count in op_types.items():
        print(f"  - {op_type}: {count}")
    
    print("\n" + "="*60)
    print("WARNING: This will restructure the entire project!")
    print("Make sure you have a backup before proceeding.")
    print("="*60)
    
    response = input("\nExecute reorganization? (yes/no): ")
    
    if response.lower() == 'yes':
        reorganizer.execute_reorganization()
    else:
        print("\nReorganization cancelled.")
        print("You can review this script and modify it as needed.")

if __name__ == "__main__":
    main()