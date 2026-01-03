#!/usr/bin/env python
"""
Unified evaluation script for both local and API models
"""
import os
import sys
import yaml
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.evaluators import UnifiedBatchEvaluator

# Setup logging
def setup_logging(log_level='INFO', log_file=None):
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=handlers
    )
    
    # Set specific loggers
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)

def load_config(config_path):
    """Load configuration from YAML file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Expand environment variables in API keys
    for model in config.get('models', []):
        if model.get('type') == 'api':
            # Handle api_keys
            if 'api_keys' in model:
                api_keys = model['api_keys']
                if isinstance(api_keys, list):
                    model['api_keys'] = [
                        os.path.expandvars(key) for key in api_keys
                    ]
                else:
                    model['api_keys'] = os.path.expandvars(api_keys)
    
    return config

def prepare_evaluation_config(config):
    """Prepare configuration for UnifiedBatchEvaluator"""
    eval_config = {
        'test_data_path': config['test_data']['path'],
        'max_samples': config['test_data'].get('max_samples'),
        'reward_server_url': config['reward_server']['url'],
        'eval_batch_size': config['evaluation']['batch_size'],
        'output_dir': config['evaluation']['output_dir'],
        'save_intermediate': config['evaluation'].get('save_intermediate', True)
    }
    
    # Resolve relative paths
    if not Path(eval_config['test_data_path']).is_absolute():
        eval_config['test_data_path'] = str(
            Path(__file__).parent / eval_config['test_data_path']
        )
    
    return eval_config

def filter_models(models, model_filter):
    """Filter models based on criteria"""
    if not model_filter:
        return models
    
    filtered = []
    for model in models:
        # Check if filter matches name or type
        if model_filter.lower() in model['name'].lower() or \
           model_filter.lower() == model.get('type', '').lower():
            filtered.append(model)
    
    return filtered

def main(args):
    """Main evaluation function"""
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
    
    # Filter models if specified
    models = config.get('models', [])
    if args.filter:
        models = filter_models(models, args.filter)
        if not models:
            print(f"错误: 没有匹配过滤条件的模型: {args.filter}")
            sys.exit(1)
    
    # Limit number of models if specified
    if args.limit:
        models = models[:args.limit]
    
    # Prepare configurations
    eval_config = prepare_evaluation_config(config)
    
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
    logger.info(f"开始统一模型评估")
    logger.info(f"配置文件: {config_path}")
    logger.info(f"测试数据: {test_data_path}")
    logger.info(f"输出目录: {output_dir}")
    logger.info(f"模型数量: {len(models)}")
    
    # Print model list
    print("\n待评估模型:")
    for i, model in enumerate(models, 1):
        model_type = model.get('type', 'unknown')
        print(f"  {i}. [{model_type:^15}] {model['name']}")
    
    # Print statistics
    api_models = [m for m in models if m.get('type') == 'api']
    local_models = [m for m in models if m.get('type') != 'api']
    print(f"\n统计: {len(api_models)} 个API模型, {len(local_models)} 个本地模型")
    
    if not args.yes:
        response = input("\n是否开始评估? (y/n): ")
        if response.lower() != 'y':
            print("评估已取消")
            sys.exit(0)
    
    # Create evaluator and run
    evaluator = UnifiedBatchEvaluator(eval_config)
    
    try:
        results = evaluator.evaluate_models(models)
        
        # Save final results
        results_file = output_dir / "evaluation_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json_results = {
                'timestamp': datetime.now().isoformat(),
                'config_file': str(config_path),
                'num_models': len(models),
                'successful_models': results['successful_models'],
                'failed_models': results['failed_models'],
                'total_time': results['total_time'],
                'output_dir': str(results['output_dir'])
            }
            
            # Add summary if comparison exists
            if results.get('comparison'):
                json_results['summary'] = {
                    'best_model': results['comparison']['rankings']['best_model'],
                    'worst_model': results['comparison']['rankings']['worst_model']
                }
            
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 评估完成!")
        print(f"总耗时: {results['total_time']:.1f} 秒")
        print(f"报告已保存至: {output_dir}")
        print(f"  - 模型报告: {output_dir}/model_*.json")
        print(f"  - 对比报告: {output_dir}/model_comparison.md")
        print(f"  - 图表: {output_dir}/charts/")
        print(f"  - 日志: {log_file}")
        
        # Print top results
        if results.get('successful_models'):
            print(f"\n成功评估 {len(results['successful_models'])} 个模型")
            if results.get('comparison') and 'models' in results['comparison']:
                print("\n最佳模型 (按总体分数):")
                for i, model in enumerate(results['comparison']['models'][:3], 1):
                    print(f"  {i}. {model['name']}: {model['overall_score']:.2%}")
        
        if results.get('failed_models'):
            print(f"\n失败: {len(results['failed_models'])} 个模型")
            for name in results['failed_models'][:5]:
                print(f"  ✗ {name}")
        
        return 0
        
    except Exception as e:
        logger.error(f"评估过程出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='统一评估本地和API模型并生成对比报告'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='../configs/models_config.yaml',
        help='模型配置文件路径 (默认: ../configs/models_config.yaml)'
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
        '--filter', '-f',
        type=str,
        help='过滤模型 (按名称或类型)'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='限制评估的模型数量'
    )
    
    parser.add_argument(
        '--log-level',
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
    exit_code = main(args)
    sys.exit(exit_code)