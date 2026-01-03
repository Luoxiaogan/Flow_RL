#!/usr/bin/env python
"""
Test script for hierarchical evaluation system
"""
import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.utils.detailed_score_recorder import DetailedScoreRecorder
from core.utils.incremental_report_generator import IncrementalReportGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_detailed_score_recorder():
    """Test DetailedScoreRecorder functionality"""
    print("\n" + "="*60)
    print("测试 DetailedScoreRecorder")
    print("="*60)
    
    # Create recorder
    recorder = DetailedScoreRecorder('test_output/score_recorder_test')
    
    # Set context for model -> benchmark -> operator group
    recorder.set_context(model='TestModel-1', benchmark='GSM8K', operator_group='Group-A')
    
    # Record some sample scores
    for i in range(5):
        sample = {
            'data_source': 'workflow_gsm8k',
            'prompt': f'Test prompt {i}',
            'extra_info': {
                'test_cases': [1, 2, 3],
                'operator_group': 'Group-A'
            }
        }
        
        solution = f"Generated solution for sample {i}"
        
        score_result = {
            'success': i % 2 == 0,  # Alternate success/failure
            'score': 0.8 if i % 2 == 0 else 0.0,
            'error': None if i % 2 == 0 else 'Test error',
            'execution_time': 1.5 + i * 0.1
        }
        
        recorder.record_sample_score(sample, solution, score_result, i)
    
    # Change to a different operator group
    recorder.set_context(operator_group='Group-B')
    
    # Record more samples
    for i in range(5, 8):
        sample = {
            'data_source': 'workflow_gsm8k',
            'prompt': f'Test prompt {i}',
            'extra_info': {
                'operator_group': 'Group-B'
            }
        }
        
        solution = f"Generated solution for sample {i}"
        
        score_result = {
            'success': True,
            'score': 0.9,
            'error': None,
            'execution_time': 2.0
        }
        
        recorder.record_sample_score(sample, solution, score_result, i)
    
    # Test retrieval functions
    print("\n📊 测试数据检索:")
    
    # Get scores by operator
    group_a_scores = recorder.get_scores_by_operator('TestModel-1', 'GSM8K', 'Group-A')
    print(f"  Group-A 样本数: {len(group_a_scores)}")
    
    group_b_scores = recorder.get_scores_by_operator('TestModel-1', 'GSM8K', 'Group-B')
    print(f"  Group-B 样本数: {len(group_b_scores)}")
    
    # Calculate statistics
    stats_a = recorder.calculate_statistics(group_a_scores)
    print(f"\n  Group-A 统计:")
    print(f"    - 成功率: {stats_a['success_rate']:.1%}")
    print(f"    - 平均分: {stats_a['mean_score']:.3f}")
    
    stats_b = recorder.calculate_statistics(group_b_scores)
    print(f"\n  Group-B 统计:")
    print(f"    - 成功率: {stats_b['success_rate']:.1%}")
    print(f"    - 平均分: {stats_b['mean_score']:.3f}")
    
    # Test export functions
    print("\n💾 测试导出功能:")
    
    # Export to JSON
    json_path = recorder.export_to_json(
        model='TestModel-1',
        benchmark='GSM8K',
        operator_group='Group-A'
    )
    print(f"  导出JSON: {json_path}")
    
    # Export to CSV
    csv_path = recorder.export_to_csv(
        model='TestModel-1',
        benchmark='GSM8K'
    )
    print(f"  导出CSV: {csv_path}")
    
    # Get progress summary
    progress = recorder.get_progress_summary()
    print(f"\n📈 进度摘要:")
    print(f"  总模型数: {progress['total_models']}")
    print(f"  总样本数: {progress['total_samples']}")
    
    # Save final report
    final_path = recorder.save_final_report()
    print(f"\n✅ 最终报告已保存: {final_path}")
    
    return True

def test_incremental_report_generator():
    """Test IncrementalReportGenerator functionality"""
    print("\n" + "="*60)
    print("测试 IncrementalReportGenerator")
    print("="*60)
    
    # Create generator
    generator = IncrementalReportGenerator('test_output/report_generator_test')
    
    # Test operator report generation
    print("\n📄 生成Operator组报告:")
    
    scores = [
        {'success': True, 'score': 0.8, 'error': None},
        {'success': False, 'score': 0.0, 'error': 'Test error'},
        {'success': True, 'score': 0.9, 'error': None},
    ]
    
    samples = [
        {'data_source': 'workflow_gsm8k', 'prompt': 'Test 1', 'extra_info': {}},
        {'data_source': 'workflow_gsm8k', 'prompt': 'Test 2', 'extra_info': {}},
        {'data_source': 'workflow_gsm8k', 'prompt': 'Test 3', 'extra_info': {}},
    ]
    
    operator_report = generator.generate_operator_report(
        'TestModel', 'GSM8K', 'OperatorGroup1', scores, samples
    )
    print(f"  生成成功: {operator_report['hierarchy']}")
    
    # Test benchmark report generation
    print("\n📊 生成Benchmark报告:")
    
    operator_reports = {
        'OperatorGroup1': operator_report,
        'OperatorGroup2': {
            'statistics': {'success_rate': 0.9, 'mean_score': 0.85},
            'num_samples': 5
        }
    }
    
    all_scores = scores * 2  # Simulate more scores
    
    benchmark_report = generator.generate_benchmark_report(
        'TestModel', 'GSM8K', operator_reports, all_scores
    )
    print(f"  生成成功: {benchmark_report['hierarchy']}")
    
    # Test model summary generation
    print("\n📈 生成模型总结:")
    
    benchmark_reports = {
        'GSM8K': benchmark_report,
        'MBPP': {
            'statistics': {'success_rate': 0.7, 'mean_score': 0.75},
            'total_samples': 10
        }
    }
    
    model_summary = generator.generate_model_summary(
        'TestModel', benchmark_reports, scores * 3
    )
    print(f"  生成成功: 模型 {model_summary['model']}")
    
    # Test dashboard update
    print("\n🌐 更新评估面板:")
    generator.update_dashboard()
    dashboard_path = generator.dashboard_file
    print(f"  面板已生成: {dashboard_path}")
    
    # Check progress
    print(f"\n📊 当前进度:")
    print(f"  模型完成: {generator.current_progress['models_completed']}")
    print(f"  基准完成: {generator.current_progress['benchmarks_completed']}")
    print(f"  Operator组完成: {generator.current_progress['operator_groups_completed']}")
    print(f"  样本评估: {generator.current_progress['samples_evaluated']}")
    
    return True

def test_integration():
    """Test integration of components"""
    print("\n" + "="*60)
    print("测试组件集成")
    print("="*60)
    
    # Create both components
    recorder = DetailedScoreRecorder('test_output/integration_test')
    generator = IncrementalReportGenerator('test_output/integration_test')
    
    # Simulate evaluation workflow
    model_name = 'IntegrationTestModel'
    benchmark_name = 'TestBenchmark'
    operator_groups = ['GroupA', 'GroupB']
    
    print(f"\n🚀 模拟评估工作流:")
    print(f"  模型: {model_name}")
    print(f"  基准: {benchmark_name}")
    print(f"  Operator组: {operator_groups}")
    
    # Process each operator group
    for group in operator_groups:
        print(f"\n  处理 {group}...")
        
        # Set context
        recorder.set_context(model=model_name, benchmark=benchmark_name, operator_group=group)
        
        # Generate and record scores
        scores = []
        samples = []
        
        for i in range(3):
            sample = {
                'data_source': f'workflow_{benchmark_name.lower()}',
                'prompt': f'Test prompt for {group} sample {i}',
                'extra_info': {'operator_group': group}
            }
            
            solution = f"Solution for {group} sample {i}"
            
            score_result = {
                'success': True,
                'score': 0.7 + i * 0.1,
                'error': None,
                'execution_time': 1.0 + i * 0.2
            }
            
            recorder.record_sample_score(sample, solution, score_result, i)
            scores.append(score_result)
            samples.append(sample)
        
        # Generate operator report
        operator_report = generator.generate_operator_report(
            model_name, benchmark_name, group, scores, samples
        )
        
        print(f"    ✓ 完成: 成功率 {operator_report['statistics']['success_rate']:.1%}")
    
    # Get all scores for benchmark
    benchmark_data = recorder.get_scores_by_benchmark(model_name, benchmark_name)
    
    # Generate benchmark report
    print(f"\n  生成基准报告...")
    all_scores = []
    operator_reports = {}
    
    for group in operator_groups:
        group_scores = recorder.get_scores_by_operator(model_name, benchmark_name, group)
        scores = [s['evaluation'] for s in group_scores]
        all_scores.extend(scores)
        
        operator_reports[group] = {
            'statistics': recorder.calculate_statistics(group_scores),
            'num_samples': len(group_scores)
        }
    
    benchmark_report = generator.generate_benchmark_report(
        model_name, benchmark_name, operator_reports, all_scores
    )
    
    print(f"    ✓ 基准报告完成")
    
    # Generate model summary
    print(f"\n  生成模型总结...")
    
    benchmark_reports = {benchmark_name: benchmark_report}
    model_summary = generator.generate_model_summary(
        model_name, benchmark_reports, all_scores
    )
    
    print(f"    ✓ 模型总结完成")
    
    # Save final report
    final_path = recorder.save_final_report()
    print(f"\n✅ 集成测试完成")
    print(f"  最终报告: {final_path}")
    print(f"  评估面板: {generator.dashboard_file}")
    
    return True

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("分层评估系统测试")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    tests = [
        ("DetailedScoreRecorder", test_detailed_score_recorder),
        ("IncrementalReportGenerator", test_incremental_report_generator),
        ("组件集成", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n运行测试: {test_name}")
            success = test_func()
            results.append((test_name, success))
            print(f"\n✅ {test_name} 测试{'成功' if success else '失败'}")
        except Exception as e:
            print(f"\n❌ {test_name} 测试失败: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for test_name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    success_count = sum(1 for _, s in results if s)
    total_count = len(results)
    print(f"\n总计: {success_count}/{total_count} 测试通过")
    
    if success_count == total_count:
        print("\n🎉 所有测试通过! 分层评估系统工作正常。")
    else:
        print(f"\n⚠️  有 {total_count - success_count} 个测试失败，请检查问题。")
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()