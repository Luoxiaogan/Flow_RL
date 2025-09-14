#!/usr/bin/env python
"""
Main script to run batch model evaluation
"""
import os
import sys
import yaml
import json
import asyncio
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.evaluators import BatchModelEvaluator

# Setup logging
def setup_logging(log_level='INFO', log_file=None):
    """
    Setup logging configuration
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=handlers
    )

def load_config(config_path):
    """
    Load configuration from YAML file
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def prepare_evaluation_config(config):
    """
    Prepare configuration for BatchModelEvaluator
    """
    eval_config = {
        'test_data_path': config['test_data']['path'],
        'max_samples': config['test_data'].get('max_samples'),
        'reward_server_url': config['reward_server']['url'],
        'eval_batch_size': config['evaluation']['batch_size'],
        'output_dir': config['evaluation']['output_dir'],
        'generation_params': config['evaluation'].get('generation_params', {})
    }
    
    # Resolve relative paths
    if not Path(eval_config['test_data_path']).is_absolute():
        eval_config['test_data_path'] = str(
            Path(__file__).parent / eval_config['test_data_path']
        )
    
    return eval_config

def prepare_model_configs(config):
    """
    Prepare model configurations
    """
    model_configs = []
    
    for model in config['models']:
        model_config = {
            'name': model['name'],
            'path': model['path'],
            'type': model.get('type', 'unknown')
        }
        
        # Add generation params if specified
        if 'generation_params' in model:
            model_config['generation_params'] = model['generation_params']
        
        model_configs.append(model_config)
    
    return model_configs

async def main(args):
    """
    Main evaluation function
    """
    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"错误: 配置文件不存在: {config_path}")
        sys.exit(1)
    
    print(f"加载配置: {config_path}")
    config = load_config(config_path)
    
    # Override config with command line arguments
    if args.test_data:
        config['test_data']['path'] = args.test_data
    if args.max_samples is not None:
        config['test_data']['max_samples'] = args.max_samples
    if args.output_dir:
        config['evaluation']['output_dir'] = args.output_dir
    if args.batch_size:
        config['evaluation']['batch_size'] = args.batch_size
    
    # Prepare configurations
    eval_config = prepare_evaluation_config(config)
    model_configs = prepare_model_configs(config)
    
    # Check if test data exists
    test_data_path = Path(eval_config['test_data_path'])
    if not test_data_path.exists():
        print(f"错误: 测试数据文件不存在: {test_data_path}")
        print("请先生成测试数据或指定正确的路径")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(eval_config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup logging
    log_file = output_dir / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    setup_logging(args.log_level, log_file)
    
    logger = logging.getLogger(__name__)
    logger.info(f"开始模型评估")
    logger.info(f"配置文件: {config_path}")
    logger.info(f"测试数据: {test_data_path}")
    logger.info(f"输出目录: {output_dir}")
    logger.info(f"模型数量: {len(model_configs)}")
    
    # Print model list
    print("\n待评估模型:")
    for i, model in enumerate(model_configs, 1):
        print(f"  {i}. {model['name']} ({model['path']})")
    
    if not args.yes:
        response = input("\n是否开始评估? (y/n): ")
        if response.lower() != 'y':
            print("评估已取消")
            sys.exit(0)
    
    # Create evaluator and run
    evaluator = BatchModelEvaluator(eval_config)
    
    try:
        results = await evaluator.evaluate_models(model_configs)
        
        # Save final results
        results_file = output_dir / "evaluation_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            # Convert Path objects to strings for JSON serialization
            json_results = {
                'timestamp': datetime.now().isoformat(),
                'config': config,
                'output_dir': str(results['output_dir']),
                'comparison': results['comparison']
            }
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 评估完成!")
        print(f"报告已保存至: {output_dir}")
        print(f"  - 模型报告: {output_dir}/model_*.json")
        print(f"  - 对比报告: {output_dir}/model_comparison.md")
        print(f"  - 图表: {output_dir}/charts/")
        print(f"  - 日志: {log_file}")
        
        # Print top results
        if 'comparison' in results and 'models' in results['comparison']:
            print("\n模型排名 (按总体分数):")
            for i, model in enumerate(results['comparison']['models'][:3], 1):
                print(f"  {i}. {model['name']}: {model['overall_score']:.2%}")
        
        return 0
        
    except Exception as e:
        logger.error(f"评估过程出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description='批量评估多个模型并生成对比报告'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='../configs/evaluation_config.yaml',
        help='配置文件路径 (默认: ../configs/evaluation_config.yaml)'
    )
    
    parser.add_argument(
        '--test-data', '-t',
        type=str,
        help='测试数据文件路径 (覆盖配置文件)'
    )
    
    parser.add_argument(
        '--max-samples', '-n',
        type=int,
        help='最大评估样本数 (覆盖配置文件)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        help='输出目录 (覆盖配置文件)'
    )
    
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        help='批处理大小 (覆盖配置文件)'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='日志级别 (默认: INFO)'
    )
    
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='跳过确认提示'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    exit_code = asyncio.run(main(args))
    sys.exit(exit_code)