#!/usr/bin/env python
"""
Result Analyzer - 结果分析器
用于分析测试结果，生成统计数据和分类报告
"""

import json
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from datetime import datetime
import pandas as pd


class ResultAnalyzer:
    """结果分析器类"""

    def __init__(self, config: Dict):
        """
        初始化分析器

        Args:
            config: 配置字典
        """
        self.config = config
        self.results_dir = Path(config.get('io', {}).get('output_dir', './results'))

        # 分析结果存储
        self.all_results = []
        self.statistics_by_datasource = {}
        self.statistics_by_operators = {}
        self.overall_statistics = {}

    def load_results(self, results_path: Optional[str] = None) -> List[Dict]:
        """
        加载测试结果

        Args:
            results_path: 结果文件路径，如果为None则加载所有结果

        Returns:
            结果列表
        """
        results = []

        if results_path:
            # 加载指定文件
            with open(results_path, 'r', encoding='utf-8') as f:
                for line in f:
                    results.append(json.loads(line))
        else:
            # 递归加载所有test_results_with_input.jsonl文件（新格式）
            for result_file in self.results_dir.rglob('test_results_with_input.jsonl'):
                with open(result_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            results.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

            # 如果没有新格式文件，尝试加载旧格式
            if not results:
                for result_file in self.results_dir.rglob('test_results.jsonl'):
                    with open(result_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                results.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue

        self.all_results = results
        print(f"加载了 {len(results)} 条测试结果")

        # 显示是否包含输入信息
        if results and 'input' in results[0] and 'workflow_code' in results[0]['input']:
            print("  ✓ 结果包含完整的输入信息和workflow代码")
        if results and 'line_number' in results[0]:
            print("  ✓ 结果包含原始文件行号")

        return results

    def analyze_by_data_source(self) -> Dict[str, Dict]:
        """
        按data_source分析结果

        Returns:
            按data_source分组的统计数据
        """
        stats = defaultdict(lambda: {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'scores': [],
            'execution_times': [],
            'operators_breakdown': defaultdict(lambda: {
                'total': 0,
                'successful': 0,
                'scores': []
            })
        })

        for result in self.all_results:
            data_source = result.get('data_source', 'unknown')
            operators_group = result.get('operators_group', 'unknown')

            # 更新总体统计
            stats[data_source]['total'] += 1

            if result.get('success', False):
                stats[data_source]['successful'] += 1
                score = result.get('score', 0.0)
                stats[data_source]['scores'].append(score)
            else:
                stats[data_source]['failed'] += 1

            execution_time = result.get('execution_time', 0)
            stats[data_source]['execution_times'].append(execution_time)

            # 更新operator组合统计
            stats[data_source]['operators_breakdown'][operators_group]['total'] += 1
            if result.get('success', False):
                stats[data_source]['operators_breakdown'][operators_group]['successful'] += 1
                stats[data_source]['operators_breakdown'][operators_group]['scores'].append(result.get('score', 0.0))

        # 计算汇总指标
        for data_source, stat in stats.items():
            # 成功率
            if stat['total'] > 0:
                stat['success_rate'] = stat['successful'] / stat['total']
            else:
                stat['success_rate'] = 0

            # 平均分数
            if stat['scores']:
                stat['average_score'] = statistics.mean(stat['scores'])
                stat['score_std'] = statistics.stdev(stat['scores']) if len(stat['scores']) > 1 else 0
                stat['max_score'] = max(stat['scores'])
                stat['min_score'] = min(stat['scores'])
            else:
                stat['average_score'] = 0
                stat['score_std'] = 0
                stat['max_score'] = 0
                stat['min_score'] = 0

            # 执行时间统计
            if stat['execution_times']:
                stat['avg_execution_time'] = statistics.mean(stat['execution_times'])
                stat['max_execution_time'] = max(stat['execution_times'])
                stat['min_execution_time'] = min(stat['execution_times'])
            else:
                stat['avg_execution_time'] = 0
                stat['max_execution_time'] = 0
                stat['min_execution_time'] = 0

            # 计算每个operator组合的汇总指标
            for op_group, op_stat in stat['operators_breakdown'].items():
                if op_stat['total'] > 0:
                    op_stat['success_rate'] = op_stat['successful'] / op_stat['total']
                else:
                    op_stat['success_rate'] = 0

                if op_stat['scores']:
                    op_stat['average_score'] = statistics.mean(op_stat['scores'])
                else:
                    op_stat['average_score'] = 0

        self.statistics_by_datasource = dict(stats)
        return self.statistics_by_datasource

    def analyze_by_operators(self) -> Dict[str, Dict]:
        """
        按operators_group分析结果

        Returns:
            按operators_group分组的统计数据
        """
        stats = defaultdict(lambda: {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'scores': [],
            'execution_times': [],
            'datasource_breakdown': defaultdict(lambda: {
                'total': 0,
                'successful': 0,
                'scores': []
            })
        })

        for result in self.all_results:
            operators_group = result.get('operators_group', 'unknown')
            data_source = result.get('data_source', 'unknown')

            # 更新总体统计
            stats[operators_group]['total'] += 1

            if result.get('success', False):
                stats[operators_group]['successful'] += 1
                score = result.get('score', 0.0)
                stats[operators_group]['scores'].append(score)
            else:
                stats[operators_group]['failed'] += 1

            execution_time = result.get('execution_time', 0)
            stats[operators_group]['execution_times'].append(execution_time)

            # 更新data_source breakdown
            stats[operators_group]['datasource_breakdown'][data_source]['total'] += 1
            if result.get('success', False):
                stats[operators_group]['datasource_breakdown'][data_source]['successful'] += 1
                stats[operators_group]['datasource_breakdown'][data_source]['scores'].append(result.get('score', 0.0))

        # 计算汇总指标
        for operators_group, stat in stats.items():
            # 成功率
            if stat['total'] > 0:
                stat['success_rate'] = stat['successful'] / stat['total']
            else:
                stat['success_rate'] = 0

            # 平均分数
            if stat['scores']:
                stat['average_score'] = statistics.mean(stat['scores'])
                stat['score_std'] = statistics.stdev(stat['scores']) if len(stat['scores']) > 1 else 0
            else:
                stat['average_score'] = 0
                stat['score_std'] = 0

            # 执行时间
            if stat['execution_times']:
                stat['avg_execution_time'] = statistics.mean(stat['execution_times'])
            else:
                stat['avg_execution_time'] = 0

            # 计算每个data_source的汇总指标
            for ds, ds_stat in stat['datasource_breakdown'].items():
                if ds_stat['total'] > 0:
                    ds_stat['success_rate'] = ds_stat['successful'] / ds_stat['total']
                else:
                    ds_stat['success_rate'] = 0

                if ds_stat['scores']:
                    ds_stat['average_score'] = statistics.mean(ds_stat['scores'])
                else:
                    ds_stat['average_score'] = 0

        self.statistics_by_operators = dict(stats)
        return self.statistics_by_operators

    def analyze_overall(self) -> Dict:
        """
        生成整体统计

        Returns:
            整体统计数据
        """
        overall = {
            'total_tests': len(self.all_results),
            'total_successful': sum(1 for r in self.all_results if r.get('success', False)),
            'total_failed': sum(1 for r in self.all_results if not r.get('success', False)),
            'unique_datasources': len(set(r.get('data_source') for r in self.all_results)),
            'unique_operators': len(set(r.get('operators_group') for r in self.all_results))
        }

        # 计算总体成功率
        if overall['total_tests'] > 0:
            overall['overall_success_rate'] = overall['total_successful'] / overall['total_tests']
        else:
            overall['overall_success_rate'] = 0

        # 收集所有分数
        all_scores = [r.get('score', 0.0) for r in self.all_results if r.get('success', False)]
        if all_scores:
            overall['overall_average_score'] = statistics.mean(all_scores)
            overall['overall_score_std'] = statistics.stdev(all_scores) if len(all_scores) > 1 else 0
            overall['overall_max_score'] = max(all_scores)
            overall['overall_min_score'] = min(all_scores)
        else:
            overall['overall_average_score'] = 0
            overall['overall_score_std'] = 0
            overall['overall_max_score'] = 0
            overall['overall_min_score'] = 0

        # 执行时间统计
        all_times = [r.get('execution_time', 0) for r in self.all_results]
        if all_times:
            overall['avg_execution_time'] = statistics.mean(all_times)
            overall['total_execution_time'] = sum(all_times)
        else:
            overall['avg_execution_time'] = 0
            overall['total_execution_time'] = 0

        self.overall_statistics = overall
        return overall

    def get_top_performers(self, n: int = 5) -> Dict:
        """
        获取表现最好的组合

        Args:
            n: 返回前n个

        Returns:
            最佳表现组合
        """
        performers = []

        # 收集所有data_source + operators组合的表现
        for data_source, ds_stats in self.statistics_by_datasource.items():
            for op_group, op_stats in ds_stats.get('operators_breakdown', {}).items():
                if op_stats['total'] > 0:
                    performers.append({
                        'data_source': data_source,
                        'operators_group': op_group,
                        'average_score': op_stats['average_score'],
                        'success_rate': op_stats['success_rate'],
                        'total_tests': op_stats['total']
                    })

        # 按平均分数排序
        performers.sort(key=lambda x: x['average_score'], reverse=True)

        return {
            'top_by_score': performers[:n],
            'bottom_by_score': performers[-n:] if len(performers) >= n else performers
        }

    def get_error_analysis(self) -> Dict:
        """
        分析错误案例

        Returns:
            错误分析结果
        """
        errors = defaultdict(list)
        error_types = defaultdict(int)

        for result in self.all_results:
            if not result.get('success', False):
                error = result.get('error', 'Unknown error')
                data_source = result.get('data_source', 'unknown')
                operators_group = result.get('operators_group', 'unknown')

                errors[data_source].append({
                    'operators_group': operators_group,
                    'error': error,
                    'test_id': result.get('test_id', 'unknown')
                })

                # 分类错误类型
                if 'timeout' in error.lower():
                    error_types['timeout'] += 1
                elif 'connection' in error.lower():
                    error_types['connection'] += 1
                elif 'syntax' in error.lower():
                    error_types['syntax'] += 1
                else:
                    error_types['other'] += 1

        return {
            'errors_by_datasource': dict(errors),
            'error_types': dict(error_types),
            'total_errors': sum(error_types.values())
        }

    def save_statistics(self):
        """保存统计结果到文件"""
        # 创建统计目录
        stats_dir = self.results_dir / 'summaries' / 'statistics'
        stats_dir.mkdir(parents=True, exist_ok=True)

        # 保存按data_source的统计
        with open(stats_dir / 'statistics_by_datasource.json', 'w', encoding='utf-8') as f:
            json.dump(self.statistics_by_datasource, f, indent=2, ensure_ascii=False, default=str)

        # 保存按operators的统计
        with open(stats_dir / 'statistics_by_operators.json', 'w', encoding='utf-8') as f:
            json.dump(self.statistics_by_operators, f, indent=2, ensure_ascii=False, default=str)

        # 保存整体统计
        with open(stats_dir / 'overall_statistics.json', 'w', encoding='utf-8') as f:
            json.dump(self.overall_statistics, f, indent=2, ensure_ascii=False, default=str)

        print(f"统计结果已保存至: {stats_dir}")

    def export_to_dataframe(self) -> pd.DataFrame:
        """
        导出结果为DataFrame

        Returns:
            包含所有结果的DataFrame
        """
        df = pd.DataFrame(self.all_results)
        return df

    def print_summary(self):
        """打印分析摘要"""
        print("\n" + "="*60)
        print("结果分析摘要")
        print("="*60)

        # 整体统计
        print("\n整体统计:")
        print(f"  - 总测试数: {self.overall_statistics.get('total_tests', 0)}")
        print(f"  - 成功: {self.overall_statistics.get('total_successful', 0)}")
        print(f"  - 失败: {self.overall_statistics.get('total_failed', 0)}")
        print(f"  - 成功率: {self.overall_statistics.get('overall_success_rate', 0)*100:.1f}%")
        print(f"  - 平均分数: {self.overall_statistics.get('overall_average_score', 0):.3f}")

        # 按data_source统计
        print("\n按Data Source统计:")
        for ds, stats in self.statistics_by_datasource.items():
            print(f"\n  {ds}:")
            print(f"    - 测试数: {stats['total']}")
            print(f"    - 成功率: {stats['success_rate']*100:.1f}%")
            print(f"    - 平均分: {stats['average_score']:.3f}")

        # 最佳表现
        top_performers = self.get_top_performers(3)
        print("\n最佳表现组合 (按平均分):")
        for idx, perf in enumerate(top_performers['top_by_score'], 1):
            print(f"  {idx}. {perf['data_source']} + {perf['operators_group']}")
            print(f"     分数: {perf['average_score']:.3f}, 成功率: {perf['success_rate']*100:.1f}%")


def main():
    """主函数 - 用于测试"""
    import yaml

    # 加载配置
    config_path = Path('config.yaml')
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    # 创建分析器
    analyzer = ResultAnalyzer(config)

    # 加载结果
    analyzer.load_results()

    if analyzer.all_results:
        # 执行分析
        analyzer.analyze_overall()
        analyzer.analyze_by_data_source()
        analyzer.analyze_by_operators()

        # 保存统计
        analyzer.save_statistics()

        # 打印摘要
        analyzer.print_summary()
    else:
        print("没有找到测试结果")


if __name__ == "__main__":
    main()