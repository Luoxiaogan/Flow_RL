#!/usr/bin/env python
"""
Generate experiment configuration for batch evaluation
生成批量评估实验配置
"""
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def generate_experiment_config(
    experiments: List[Dict[str, Any]],
    output_path: str = "models_config_auto.yaml",
    test_data_path: str = "../../generate_parquet_and_jsonl/test_scoreflow_data_all/train.jsonl",
    max_samples: int = 100
):
    """
    Generate configuration file for multiple experiments
    
    Args:
        experiments: List of experiment definitions
        output_path: Output configuration file path
        test_data_path: Path to test data
        max_samples: Maximum samples to evaluate
    """
    
    # Base configuration
    config = {
        'test_data': {
            'path': test_data_path,
            'max_samples': max_samples
        },
        'reward_server': {
            'url': 'http://localhost:7788'
        },
        'evaluation': {
            'batch_size': 8,
            'output_dir': f'./evaluation_reports/{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'save_intermediate': True
        },
        'models': []
    }
    
    # Generate model configurations
    for exp in experiments:
        exp_name = exp['name']
        exp_dir = exp['dir']
        steps = exp.get('steps', [100, 500, 1000])
        
        for step in steps:
            model_config = {
                'name': f"{exp_name}-Step{step}",
                'type': 'jsonl',
                'jsonl_path': f"{exp_dir}/{step}.jsonl"
            }
            config['models'].append(model_config)
    
    # Save configuration
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"配置文件已生成: {output_path}")
    print(f"包含 {len(config['models'])} 个模型配置")
    
    return config

def generate_from_directory_scan(
    base_dir: str = "../val_logs",
    pattern: str = "*/[0-9]*.jsonl",
    output_path: str = "models_config_scan.yaml"
):
    """
    Scan directory and automatically generate configuration
    
    Args:
        base_dir: Base directory to scan
        pattern: File pattern to match
        output_path: Output configuration file
    """
    
    base_path = Path(base_dir)
    jsonl_files = list(base_path.glob(pattern))
    
    # Group by experiment (directory)
    experiments = {}
    for file_path in jsonl_files:
        exp_dir = file_path.parent.name
        step = file_path.stem  # filename without extension
        
        if exp_dir not in experiments:
            experiments[exp_dir] = {
                'name': exp_dir,
                'dir': str(file_path.parent.relative_to(Path('.'))),
                'steps': []
            }
        
        try:
            step_num = int(step)
            experiments[exp_dir]['steps'].append(step_num)
        except ValueError:
            continue
    
    # Sort steps
    for exp in experiments.values():
        exp['steps'].sort()
    
    # Generate config
    exp_list = list(experiments.values())
    config = generate_experiment_config(exp_list, output_path)
    
    print(f"\n扫描结果:")
    for exp in exp_list:
        print(f"  {exp['name']}: {len(exp['steps'])} 个步数")
    
    return config

def generate_comparison_matrix(
    hyperparameters: Dict[str, List[Any]],
    base_dir: str = "../val_logs",
    output_path: str = "models_config_matrix.yaml"
):
    """
    Generate configuration for hyperparameter comparison matrix
    
    Args:
        hyperparameters: Dictionary of hyperparameter variations
        base_dir: Base directory for logs
        output_path: Output configuration file
    
    Example:
        hyperparameters = {
            'lr': ['1e-6', '2e-6', '5e-6'],
            'batch_size': [8, 16],
            'temperature': [0.7, 1.0]
        }
    """
    
    experiments = []
    
    # Generate all combinations
    import itertools
    
    keys = list(hyperparameters.keys())
    values = list(hyperparameters.values())
    
    for combination in itertools.product(*values):
        params = dict(zip(keys, combination))
        
        # Create experiment name
        exp_name = "_".join([f"{k}{v}" for k, v in params.items()])
        exp_dir = f"{base_dir}/{exp_name}"
        
        experiments.append({
            'name': exp_name,
            'dir': exp_dir,
            'steps': [100, 500, 1000, 2000, 5000],
            'params': params  # Store for reference
        })
    
    config = generate_experiment_config(experiments, output_path)
    
    print(f"\n生成超参数矩阵:")
    print(f"  总实验数: {len(experiments)}")
    print(f"  参数组合:")
    for exp in experiments[:5]:  # Show first 5
        print(f"    {exp['name']}: {exp['params']}")
    if len(experiments) > 5:
        print(f"    ... 还有 {len(experiments)-5} 个组合")
    
    return config

def main():
    """Main function with examples"""
    
    print("="*60)
    print("实验配置生成器")
    print("="*60)
    
    # Example 1: Manual specification
    print("\n1. 手动指定实验:")
    experiments = [
        {
            'name': 'BaselineRun',
            'dir': '../val_logs/20241212_150000',
            'steps': [100, 500, 1000, 2000]
        },
        {
            'name': 'ImprovedReward',
            'dir': '../val_logs/20241213_093000',
            'steps': [100, 500, 1000]
        },
        {
            'name': 'MainExp',
            'dir': '../val_logs/main_exp/20241215_100000',
            'steps': [100, 200, 300, 400, 500]
        }
    ]
    
    generate_experiment_config(
        experiments,
        output_path="models_config_manual.yaml"
    )
    
    # Example 2: Directory scan
    print("\n2. 目录扫描自动生成:")
    # generate_from_directory_scan()  # Uncomment to run
    
    # Example 3: Hyperparameter matrix
    print("\n3. 超参数矩阵生成:")
    hyperparams = {
        'lr': ['1e-6', '2e-6'],
        'bs': [8, 16],
        'temp': [0.7, 1.0]
    }
    
    # generate_comparison_matrix(hyperparams)  # Uncomment to run
    
    print("\n" + "="*60)
    print("配置生成完成！")
    print("\n使用方法:")
    print("1. 修改生成的配置文件")
    print("2. 运行评估:")
    print("   python run_unified_evaluation.py --config models_config_manual.yaml")

if __name__ == "__main__":
    main()