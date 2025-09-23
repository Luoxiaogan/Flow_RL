#!/usr/bin/env python
"""
Hierarchical evaluation script with incremental reporting
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
import signal
import traceback

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.evaluators.hierarchical_evaluator import HierarchicalEvaluator
from core.utils.incremental_report_generator import IncrementalReportGenerator

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
            if 'api_keys' in model:
                api_keys = model['api_keys']
                if isinstance(api_keys, list):
                    model['api_keys'] = [
                        os.path.expandvars(key) for key in api_keys
                    ]
                else:
                    model['api_keys'] = os.path.expandvars(api_keys)
    
    return config

def prepare_hierarchical_config(config):
    """Prepare configuration for HierarchicalEvaluator"""
    eval_config = {
        # Basic settings from unified evaluator
        'test_data_path': config['test_data']['path'],
        'max_samples': config['test_data'].get('max_samples'),
        'reward_server_url': config['reward_server']['url'],
        'eval_batch_size': config['evaluation']['batch_size'],
        'output_dir': config['evaluation']['output_dir'],
        'save_intermediate': config['evaluation'].get('save_intermediate', True),
        
        # Hierarchical-specific settings
        'hierarchical_mode': config['evaluation'].get('hierarchical_mode', True),
        'incremental_reporting': config['evaluation'].get('incremental_reporting', True),
        'save_sample_scores': config['evaluation'].get('save_sample_scores', True),
        'report_levels': config['evaluation'].get('report_levels', ['operator', 'benchmark', 'model'])
    }
    
    # Resolve relative paths
    if not Path(eval_config['test_data_path']).is_absolute():
        eval_config['test_data_path'] = str(
            Path(__file__).parent / eval_config['test_data_path']
        )
    
    return eval_config

def print_evaluation_plan(config, models):
    """Print evaluation plan summary"""
    print("\n" + "="*60)
    print("分层评估计划")
    print("="*60)
    
    print(f"\n📁 测试数据: {config['test_data']['path']}")
    max_samples = config['test_data'].get('max_samples')
    if max_samples:
        print(f"   样本限制: {max_samples}")
    else:
        print(f"   样本限制: 使用全部")
    
    print(f"\n🌐 Reward服务器: {config['reward_server']['url']}")
    
    print(f"\n📊 评估设置:")
    eval_settings = config['evaluation']
    print(f"   - 分层模式: {'✓' if eval_settings.get('hierarchical_mode', True) else '✗'}")
    print(f"   - 增量报告: {'✓' if eval_settings.get('incremental_reporting', True) else '✗'}")
    print(f"   - 保存样本分数: {'✓' if eval_settings.get('save_sample_scores', True) else '✗'}")
    print(f"   - 批次大小: {eval_settings['batch_size']}")
    print(f"   - 输出目录: {eval_settings['output_dir']}")
    
    report_levels = eval_settings.get('report_levels', [])
    if report_levels:
        print(f"   - 报告级别: {', '.join(report_levels)}")
    
    print(f"\n🤖 待评估模型 ({len(models)} 个):")
    for i, model in enumerate(models, 1):
        model_type = model.get('type', 'unknown')
        model_name = model.get('name', 'unnamed')
        
        type_emoji = {
            'api': '🌐',
            'huggingface': '🤗',
            'jsonl': '📄',
            'local': '💻'
        }.get(model_type, '❓')
        
        print(f"   {i}. {type_emoji} [{model_type:^12}] {model_name}")
        
        if model_type == 'api':
            print(f"      └─ Endpoint: {model.get('api_endpoints', ['N/A'])[0]}")
        elif model_type == 'huggingface':
            print(f"      └─ Model: {model.get('path', 'N/A')}")
        elif model_type == 'jsonl':
            print(f"      └─ File: {Path(model.get('jsonl_path', 'N/A')).name}")
    
    # Statistics
    api_models = [m for m in models if m.get('type') == 'api']
    local_models = [m for m in models if m.get('type') in ['huggingface', 'local']]
    jsonl_models = [m for m in models if m.get('type') == 'jsonl']
    
    print(f"\n📈 模型统计:")
    print(f"   - API模型: {len(api_models)}")
    print(f"   - 本地模型: {len(local_models)}")
    print(f"   - JSONL模型: {len(jsonl_models)}")
    
    print("\n" + "="*60)

async def run_evaluation(config, models, args):
    """Run hierarchical evaluation"""
    # Prepare configuration
    eval_config = prepare_hierarchical_config(config)
    
    # Create output directory
    output_dir = Path(eval_config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup logging
    log_file = None
    if config.get('advanced', {}).get('save_logs', True):
        log_prefix = config.get('advanced', {}).get('log_file_prefix', 'hierarchical_eval')
        log_file = output_dir / f"{log_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    log_level = args.log_level or config.get('advanced', {}).get('log_level', 'INFO')
    setup_logging(log_level, log_file)
    
    logger = logging.getLogger(__name__)
    logger.info("="*60)
    logger.info("开始分层评估")
    logger.info("="*60)
    logger.info(f"配置文件: {args.config}")
    logger.info(f"输出目录: {output_dir}")
    logger.info(f"模型数量: {len(models)}")
    
    # Create evaluator with incremental reporter
    evaluator = HierarchicalEvaluator(eval_config)
    
    # Inject incremental reporter if enabled
    if eval_config.get('incremental_reporting', True):
        evaluator.incremental_reporter = IncrementalReportGenerator(str(output_dir))
        evaluator.report_generator = evaluator.incremental_reporter
    
    # Setup signal handler for graceful shutdown
    def signal_handler(signum, frame):
        logger.warning("\n收到中断信号，正在保存当前进度...")
        if hasattr(evaluator, 'score_recorder'):
            evaluator.score_recorder.save_final_report()
        logger.info("进度已保存，退出程序")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Run evaluation
        start_time = datetime.now()
        results = await evaluator.evaluate_models(models)
        
        # Calculate total time
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Save final results summary
        summary_file = output_dir / "evaluation_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'config_file': str(args.config),
                'total_time': total_time,
                'num_models': len(models),
                'successful_models': results['successful_models'],
                'failed_models': results['failed_models'],
                'output_dir': str(results['output_dir']),
                'detailed_scores_path': results.get('detailed_scores_path')
            }
            
            # Add best model if available
            if results.get('comparison') and results['comparison'].get('rankings'):
                summary['best_model'] = results['comparison']['rankings'].get('best_model')
                summary['worst_model'] = results['comparison']['rankings'].get('worst_model')
            
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Print final summary
        print("\n" + "="*60)
        print("✅ 分层评估完成!")
        print("="*60)
        
        print(f"\n⏱️  总耗时: {total_time:.1f} 秒 ({total_time/60:.1f} 分钟)")
        print(f"📊 成功评估: {len(results['successful_models'])} 个模型")
        
        if results['failed_models']:
            print(f"❌ 失败: {len(results['failed_models'])} 个模型")
            for name in results['failed_models'][:5]:
                print(f"   - {name}")
        
        print(f"\n📁 报告已保存至: {output_dir}")
        print("   目录结构:")
        print("   ├── 模型名称/")
        print("   │   ├── 基准名称/")
        print("   │   │   ├── Operator组/")
        print("   │   │   │   ├── operator_report.json")
        print("   │   │   │   ├── detailed_scores.json")
        print("   │   │   │   └── scores.csv")
        print("   │   │   ├── benchmark_report.json")
        print("   │   │   └── benchmark_summary.md")
        print("   │   ├── model_report.json")
        print("   │   └── model_summary.md")
        print("   ├── evaluation_summary.json")
        print("   └── evaluation_dashboard.html")
        
        if results.get('detailed_scores_path'):
            print(f"\n📝 详细评分数据: {results['detailed_scores_path']}")
        
        if log_file:
            print(f"\n📋 日志文件: {log_file}")
        
        # Open dashboard if enabled
        if config.get('report', {}).get('enable_dashboard', True):
            dashboard_path = output_dir / 'evaluation_dashboard.html'
            if dashboard_path.exists():
                print(f"\n🌐 实时监控面板: {dashboard_path}")
                print("   (在浏览器中打开以查看实时进度)")
        
        return 0
        
    except Exception as e:
        logger.error(f"评估过程出错: {e}")
        traceback.print_exc()
        
        # Try to save partial results
        if hasattr(evaluator, 'score_recorder'):
            try:
                partial_path = evaluator.score_recorder.save_final_report()
                print(f"\n⚠️  已保存部分结果: {partial_path}")
            except:
                pass
        
        return 1

async def main(args):
    """Main function"""
    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ 错误: 配置文件不存在: {config_path}")
        sys.exit(1)
    
    print(f"📄 加载配置: {config_path}")
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
    
    # Get models list
    models = config.get('models', [])
    
    # Filter models if specified
    if args.filter:
        filtered_models = []
        for model in models:
            if args.filter.lower() in model['name'].lower() or \
               args.filter.lower() == model.get('type', '').lower():
                filtered_models.append(model)
        models = filtered_models
        
        if not models:
            print(f"❌ 错误: 没有匹配过滤条件的模型: {args.filter}")
            sys.exit(1)
    
    # Limit number of models if specified
    if args.limit:
        models = models[:args.limit]
    
    if not models:
        print("❌ 错误: 没有配置要评估的模型")
        sys.exit(1)
    
    # Check test data exists
    test_data_path = Path(config['test_data']['path'])
    if not test_data_path.is_absolute():
        test_data_path = Path(__file__).parent / test_data_path
    
    if not test_data_path.exists():
        print(f"❌ 错误: 测试数据文件不存在: {test_data_path}")
        print("   请先生成测试数据或指定正确的路径")
        sys.exit(1)
    
    # Print evaluation plan
    print_evaluation_plan(config, models)
    
    # Confirmation prompt
    if not args.yes:
        response = input("\n是否开始分层评估? (y/n): ")
        if response.lower() != 'y':
            print("评估已取消")
            sys.exit(0)
    
    # Run evaluation
    exit_code = await run_evaluation(config, models, args)
    sys.exit(exit_code)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='分层评估模型并生成增量报告'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='../configs/hierarchical_evaluation_config.yaml',
        help='配置文件路径 (默认: ../configs/hierarchical_evaluation_config.yaml)'
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
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='日志级别 (覆盖配置文件)'
    )
    
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='跳过确认提示'
    )
    
    parser.add_argument(
        '--resume',
        type=str,
        help='从指定的checkpoint恢复评估 (暂未实现)'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(main(args))