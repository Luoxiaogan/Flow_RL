#!/usr/bin/env python
"""
Result Query Tool - 结果查询工具
用于根据行号、test_id等条件查询和导出特定结果
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any
import pandas as pd
from datetime import datetime


class ResultQueryTool:
    """结果查询工具类"""

    def __init__(self, results_dir: str = "results"):
        """
        初始化查询工具

        Args:
            results_dir: 结果目录路径
        """
        self.results_dir = Path(results_dir)
        self.all_results = []
        self.results_by_line = {}
        self.results_by_test_id = {}

    def load_all_results(self) -> int:
        """
        加载所有结果文件

        Returns:
            加载的结果数量
        """
        print("正在加载所有结果文件...")
        self.all_results = []

        # 优先加载新格式文件（包含完整输入）
        for result_file in self.results_dir.rglob('test_results_with_input.jsonl'):
            print(f"  加载文件: {result_file}")
            with open(result_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        result = json.loads(line)
                        self.all_results.append(result)

                        # 建立索引
                        if 'line_number' in result:
                            self.results_by_line[result['line_number']] = result
                        if 'test_id' in result:
                            self.results_by_test_id[result['test_id']] = result

                    except json.JSONDecodeError:
                        continue

        print(f"\n共加载 {len(self.all_results)} 条结果")
        print(f"  - 按行号索引: {len(self.results_by_line)} 条")
        print(f"  - 按test_id索引: {len(self.results_by_test_id)} 条")

        return len(self.all_results)

    def query_by_line_number(self, line_number: int) -> Optional[Dict]:
        """
        根据行号查询结果

        Args:
            line_number: 原始文件中的行号

        Returns:
            匹配的结果记录
        """
        if not self.all_results:
            self.load_all_results()

        result = self.results_by_line.get(line_number)
        if result:
            print(f"\n找到行号 {line_number} 的结果:")
            self._print_result_summary(result)
            return result
        else:
            print(f"\n未找到行号 {line_number} 的结果")
            return None

    def query_by_test_id(self, test_id: str) -> Optional[Dict]:
        """
        根据test_id查询结果

        Args:
            test_id: 测试ID

        Returns:
            匹配的结果记录
        """
        if not self.all_results:
            self.load_all_results()

        result = self.results_by_test_id.get(test_id)
        if result:
            print(f"\n找到test_id {test_id} 的结果:")
            self._print_result_summary(result)
            return result
        else:
            print(f"\n未找到test_id {test_id} 的结果")
            return None

    def query_by_status(self, success: bool = True) -> List[Dict]:
        """
        根据执行状态查询结果

        Args:
            success: True查询成功的，False查询失败的

        Returns:
            匹配的结果列表
        """
        if not self.all_results:
            self.load_all_results()

        filtered = [r for r in self.all_results if r.get('success') == success]

        status_str = "成功" if success else "失败"
        print(f"\n找到 {len(filtered)} 条{status_str}的结果")

        return filtered

    def query_by_data_source(self, data_source: str) -> List[Dict]:
        """
        根据data_source查询结果

        Args:
            data_source: 数据源名称

        Returns:
            匹配的结果列表
        """
        if not self.all_results:
            self.load_all_results()

        filtered = [r for r in self.all_results if r.get('data_source') == data_source]

        print(f"\n找到 {len(filtered)} 条data_source为'{data_source}'的结果")

        return filtered

    def query_by_score_range(self, min_score: float = 0.0, max_score: float = 1.0) -> List[Dict]:
        """
        根据分数范围查询结果

        Args:
            min_score: 最低分数
            max_score: 最高分数

        Returns:
            匹配的结果列表
        """
        if not self.all_results:
            self.load_all_results()

        filtered = [
            r for r in self.all_results
            if r.get('success') and min_score <= r.get('score', 0) <= max_score
        ]

        print(f"\n找到 {len(filtered)} 条分数在 [{min_score}, {max_score}] 范围的结果")

        return filtered

    def export_results(self, results: List[Dict], output_file: str,
                       include_workflow_code: bool = True):
        """
        导出查询结果

        Args:
            results: 要导出的结果列表
            output_file: 输出文件路径
            include_workflow_code: 是否包含完整的workflow代码
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 根据文件扩展名选择导出格式
        if output_file.endswith('.csv'):
            # CSV格式（简化版，不包含workflow代码）
            df_data = []
            for r in results:
                df_data.append({
                    'line_number': r.get('line_number'),
                    'test_id': r.get('test_id'),
                    'data_source': r.get('data_source'),
                    'operators_group': r.get('operators_group'),
                    'success': r.get('success'),
                    'score': r.get('score'),
                    'execution_time': r.get('execution_time'),
                    'error': r.get('error', ''),
                    'source_file': r.get('source_file')
                })

            df = pd.DataFrame(df_data)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"\n结果已导出到CSV文件: {output_path}")

        elif output_file.endswith('.jsonl'):
            # JSONL格式（完整版）
            with open(output_path, 'w', encoding='utf-8') as f:
                for r in results:
                    if not include_workflow_code:
                        # 创建副本并移除workflow代码
                        r_copy = r.copy()
                        if 'input' in r_copy and 'workflow_code' in r_copy['input']:
                            r_copy['input']['workflow_code'] = '[已移除]'
                        f.write(json.dumps(r_copy, ensure_ascii=False) + '\n')
                    else:
                        f.write(json.dumps(r, ensure_ascii=False) + '\n')

            print(f"\n结果已导出到JSONL文件: {output_path}")

        elif output_file.endswith('.json'):
            # JSON格式（完整版，格式化）
            export_data = {
                'export_time': datetime.now().isoformat(),
                'total_count': len(results),
                'results': results if include_workflow_code else [
                    self._remove_workflow_code(r) for r in results
                ]
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            print(f"\n结果已导出到JSON文件: {output_path}")

        else:
            print(f"\n不支持的文件格式: {output_file}")

    def _remove_workflow_code(self, result: Dict) -> Dict:
        """移除workflow代码（用于导出简化版）"""
        r_copy = result.copy()
        if 'input' in r_copy and 'workflow_code' in r_copy['input']:
            r_copy['input'] = r_copy['input'].copy()
            r_copy['input']['workflow_code'] = '[已移除]'
        return r_copy

    def _print_result_summary(self, result: Dict):
        """打印结果摘要"""
        print(f"  - Test ID: {result.get('test_id')}")
        print(f"  - 行号: {result.get('line_number')}")
        print(f"  - Data Source: {result.get('data_source')}")
        print(f"  - Operators: {result.get('operators_group')}")
        print(f"  - 成功: {result.get('success')}")
        print(f"  - 分数: {result.get('score', 0):.3f}")
        print(f"  - 执行时间: {result.get('execution_time', 0):.2f}秒")

        if result.get('error'):
            print(f"  - 错误: {result['error']}")

        if 'input' in result and 'workflow_code' in result['input']:
            code = result['input']['workflow_code']
            print(f"  - Workflow代码预览: {code[:100]}...")

    def get_input_output_pairs(self, line_numbers: List[int] = None) -> List[Dict]:
        """
        获取输入输出对

        Args:
            line_numbers: 指定行号列表，如果为None则返回所有

        Returns:
            输入输出对列表
        """
        if not self.all_results:
            self.load_all_results()

        if line_numbers:
            pairs = []
            for line_num in line_numbers:
                if line_num in self.results_by_line:
                    result = self.results_by_line[line_num]
                    pairs.append({
                        'line_number': line_num,
                        'input': result.get('input', {}),
                        'output': {
                            'success': result.get('success'),
                            'score': result.get('score'),
                            'error': result.get('error'),
                            'execution_time': result.get('execution_time')
                        }
                    })
        else:
            pairs = []
            for result in self.all_results:
                pairs.append({
                    'line_number': result.get('line_number'),
                    'test_id': result.get('test_id'),
                    'input': result.get('input', {}),
                    'output': {
                        'success': result.get('success'),
                        'score': result.get('score'),
                        'error': result.get('error'),
                        'execution_time': result.get('execution_time')
                    }
                })

        return pairs

    def print_statistics(self):
        """打印统计信息"""
        if not self.all_results:
            self.load_all_results()

        total = len(self.all_results)
        successful = sum(1 for r in self.all_results if r.get('success'))
        failed = total - successful

        print("\n" + "="*60)
        print("结果统计")
        print("="*60)
        print(f"总记录数: {total}")
        print(f"成功数: {successful} ({successful/total*100:.1f}%)")
        print(f"失败数: {failed} ({failed/total*100:.1f}%)")

        # 按data_source统计
        by_datasource = {}
        for r in self.all_results:
            ds = r.get('data_source', 'unknown')
            if ds not in by_datasource:
                by_datasource[ds] = {'total': 0, 'successful': 0}
            by_datasource[ds]['total'] += 1
            if r.get('success'):
                by_datasource[ds]['successful'] += 1

        print("\n按Data Source统计:")
        for ds, stats in by_datasource.items():
            success_rate = stats['successful'] / stats['total'] * 100
            print(f"  - {ds}: {stats['total']} 条, 成功率 {success_rate:.1f}%")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Workflow结果查询工具")

    # 添加命令行参数
    parser.add_argument(
        '--results-dir',
        default='results',
        help='结果目录路径'
    )

    parser.add_argument(
        '--line',
        type=int,
        help='根据行号查询'
    )

    parser.add_argument(
        '--test-id',
        help='根据test_id查询'
    )

    parser.add_argument(
        '--status',
        choices=['success', 'failed'],
        help='根据状态查询'
    )

    parser.add_argument(
        '--data-source',
        help='根据data_source查询'
    )

    parser.add_argument(
        '--score-min',
        type=float,
        default=0.0,
        help='最低分数'
    )

    parser.add_argument(
        '--score-max',
        type=float,
        default=1.0,
        help='最高分数'
    )

    parser.add_argument(
        '--export',
        help='导出文件路径 (.csv, .jsonl, .json)'
    )

    parser.add_argument(
        '--no-code',
        action='store_true',
        help='导出时不包含workflow代码'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='显示统计信息'
    )

    args = parser.parse_args()

    # 创建查询工具
    tool = ResultQueryTool(args.results_dir)

    # 执行查询
    results = []

    if args.line:
        result = tool.query_by_line_number(args.line)
        if result:
            results = [result]

    elif args.test_id:
        result = tool.query_by_test_id(args.test_id)
        if result:
            results = [result]

    elif args.status:
        success = (args.status == 'success')
        results = tool.query_by_status(success)

    elif args.data_source:
        results = tool.query_by_data_source(args.data_source)

    elif args.score_min != 0.0 or args.score_max != 1.0:
        results = tool.query_by_score_range(args.score_min, args.score_max)

    elif args.stats:
        tool.print_statistics()
        return

    else:
        # 如果没有指定查询条件，加载所有结果
        tool.load_all_results()
        results = tool.all_results

    # 导出结果
    if args.export and results:
        tool.export_results(results, args.export, not args.no_code)

    # 显示查询结果数量
    if results:
        print(f"\n共查询到 {len(results)} 条结果")


if __name__ == "__main__":
    main()