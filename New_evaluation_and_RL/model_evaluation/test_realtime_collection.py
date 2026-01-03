"""
Test script for realtime data collection and checkpoint recovery
测试实时数据采集和断点续测功能
"""
import asyncio
import json
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from model_evaluation.core.evaluators.unified_batch_evaluator import UnifiedBatchEvaluator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'test_realtime_{Path(__file__).stem}.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_realtime_collection():
    """
    Test realtime data collection with checkpoint recovery
    """

    # Configuration
    config = {
        'test_data_path': 'data/test_samples.jsonl',
        'reward_server_url': 'http://localhost:8899',
        'output_dir': 'test_realtime_output',
        'eval_batch_size': 2,
        'max_samples': 10,  # Limit samples for testing
        'save_intermediate': True,
        'enable_realtime_collection': True,  # Enable realtime collection
        'collection_output_dir': 'test_realtime_data'
    }

    # Model configurations for testing
    model_configs = [
        {
            'name': 'qwen-turbo',
            'type': 'api',
            'api_config': {
                'base_url': 'http://localhost:5019/v1',
                'api_key': 'test-key',
                'model': 'qwen-turbo'
            },
            'generation_config': {
                'max_tokens': 4096,
                'temperature': 0.7
            }
        }
    ]

    logger.info("="*60)
    logger.info("测试实时数据采集和断点续测功能")
    logger.info("="*60)

    # Initialize evaluator
    evaluator = UnifiedBatchEvaluator(config)

    try:
        # Run evaluation
        logger.info("\n第一次运行评测...")
        results = await evaluator.evaluate_models(model_configs)

        logger.info("\n评测结果:")
        logger.info(f"  成功模型: {results['successful_models']}")
        logger.info(f"  失败模型: {results['failed_models']}")
        logger.info(f"  总耗时: {results['total_time']:.2f}秒")
        logger.info(f"  输出目录: {results['output_dir']}")

        # Check if realtime data was collected
        collection_dir = Path(config['collection_output_dir'])
        if collection_dir.exists():
            data_files = list(collection_dir.glob('evaluation_data_*.jsonl'))
            if data_files:
                logger.info(f"\n实时数据文件已创建:")
                for file in data_files:
                    # Count records
                    with open(file, 'r', encoding='utf-8') as f:
                        record_count = sum(1 for _ in f)
                    logger.info(f"  {file.name}: {record_count} 条记录")

            # Check checkpoint files
            checkpoint_files = list(collection_dir.glob('checkpoint_*.json'))
            if checkpoint_files:
                logger.info(f"\n检查点文件已创建:")
                for file in checkpoint_files:
                    with open(file, 'r', encoding='utf-8') as f:
                        checkpoint = json.load(f)
                    logger.info(f"  {file.name}: {checkpoint['record_count']} 条记录")

            # Check resume info
            resume_file = collection_dir / 'resume_info.json'
            if resume_file.exists():
                with open(resume_file, 'r', encoding='utf-8') as f:
                    resume_info = json.load(f)
                logger.info(f"\n恢复信息:")
                logger.info(f"  状态: {resume_info['status']}")
                logger.info(f"  记录数: {resume_info.get('record_count', 0)}")

        # Test checkpoint recovery
        logger.info("\n" + "="*60)
        logger.info("测试断点续测功能")
        logger.info("="*60)

        # Simulate interruption by modifying resume_info to incomplete
        if resume_file.exists():
            with open(resume_file, 'r', encoding='utf-8') as f:
                resume_info = json.load(f)

            # Mark as incomplete
            resume_info['status'] = 'incomplete'
            resume_info['record_count'] = 5  # Pretend only 5 records were processed

            with open(resume_file, 'w', encoding='utf-8') as f:
                json.dump(resume_info, f, ensure_ascii=False, indent=2)

            logger.info("模拟中断状态，标记为未完成")

        # Create new evaluator to test recovery
        logger.info("\n第二次运行评测（断点续测）...")
        evaluator2 = UnifiedBatchEvaluator(config)

        # Run evaluation again
        results2 = await evaluator2.evaluate_models(model_configs)

        logger.info("\n断点续测结果:")
        logger.info(f"  成功模型: {results2['successful_models']}")
        logger.info(f"  总耗时: {results2['total_time']:.2f}秒")

        # Verify that previously processed samples were skipped
        if collection_dir.exists():
            data_files = list(collection_dir.glob('evaluation_data_*.jsonl'))
            if data_files:
                logger.info(f"\n最终数据文件:")
                for file in data_files:
                    with open(file, 'r', encoding='utf-8') as f:
                        records = [json.loads(line) for line in f]

                    # Check for duplicates
                    sample_ids = [r['sample_id'] for r in records]
                    unique_ids = set(sample_ids)

                    logger.info(f"  {file.name}:")
                    logger.info(f"    总记录数: {len(records)}")
                    logger.info(f"    唯一样本: {len(unique_ids)}")
                    if len(sample_ids) != len(unique_ids):
                        logger.warning(f"    发现重复记录: {len(sample_ids) - len(unique_ids)} 个")
                    else:
                        logger.info(f"    ✓ 无重复记录")

        logger.info("\n测试完成!")

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_data_analysis():
    """
    Test data analysis from collected JSONL files
    """
    logger.info("\n" + "="*60)
    logger.info("测试数据分析功能")
    logger.info("="*60)

    collection_dir = Path('test_realtime_data')
    if not collection_dir.exists():
        logger.warning("数据目录不存在，请先运行测试")
        return

    # Find data files
    data_files = list(collection_dir.glob('evaluation_data_*.jsonl'))
    if not data_files:
        logger.warning("未找到数据文件")
        return

    # Analyze each file
    for file in data_files:
        logger.info(f"\n分析文件: {file.name}")

        with open(file, 'r', encoding='utf-8') as f:
            records = [json.loads(line) for line in f]

        if not records:
            logger.info("  文件为空")
            continue

        # Basic statistics
        total = len(records)
        successful = sum(1 for r in records if r['evaluation']['success'])
        timeouts = sum(1 for r in records if r['evaluation']['timeout'])

        logger.info(f"  总记录: {total}")
        logger.info(f"  成功: {successful} ({successful/total*100:.1f}%)")
        logger.info(f"  失败: {total - successful} ({(total-successful)/total*100:.1f}%)")
        logger.info(f"  超时: {timeouts} ({timeouts/total*100:.1f}%)")

        # Group by benchmark
        benchmarks = {}
        for record in records:
            benchmark = record['benchmark']
            if benchmark not in benchmarks:
                benchmarks[benchmark] = {'total': 0, 'successful': 0, 'scores': []}

            benchmarks[benchmark]['total'] += 1
            if record['evaluation']['success']:
                benchmarks[benchmark]['successful'] += 1
                benchmarks[benchmark]['scores'].append(record['evaluation']['score'])

        logger.info(f"\n  按Benchmark统计:")
        for benchmark, stats in benchmarks.items():
            avg_score = sum(stats['scores']) / len(stats['scores']) if stats['scores'] else 0
            success_rate = stats['successful'] / stats['total'] * 100
            logger.info(f"    {benchmark}:")
            logger.info(f"      样本数: {stats['total']}")
            logger.info(f"      成功率: {success_rate:.1f}%")
            logger.info(f"      平均分: {avg_score:.3f}")

        # Performance statistics
        latencies = [r['performance']['latency'] for r in records if r['performance']['latency']]
        if latencies:
            logger.info(f"\n  性能统计:")
            logger.info(f"    平均延迟: {sum(latencies)/len(latencies):.2f}秒")
            logger.info(f"    最小延迟: {min(latencies):.2f}秒")
            logger.info(f"    最大延迟: {max(latencies):.2f}秒")

if __name__ == '__main__':
    # Run tests
    asyncio.run(test_realtime_collection())
    asyncio.run(test_data_analysis())