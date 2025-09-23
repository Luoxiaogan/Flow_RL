#!/usr/bin/env python
"""
Workflow Executor - Workflow执行器
用于执行workflow测试并调用reward server获取评分
"""

import asyncio
import aiohttp
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import traceback


class WorkflowExecutor:
    """Workflow执行器类"""

    def __init__(self, config: Dict):
        """
        初始化执行器

        Args:
            config: 配置字典
        """
        self.config = config
        self.reward_server_url = config.get('reward_server', {}).get('url', 'http://localhost:8899')
        self.timeout = config.get('reward_server', {}).get('timeout', 300)
        self.max_retries = config.get('reward_server', {}).get('max_retries', 3)
        self.retry_delay = config.get('reward_server', {}).get('retry_delay', 5)

        # 测试配置
        self.num_test_cases = config.get('test', {}).get('num_test_cases', 200)
        self.random_seed = config.get('test', {}).get('random_seed', 42)
        self.benchmark_mapping_file = config.get('test', {}).get('benchmark_mapping_file', '../benchmark_mapping_test.jsonl')

        # 加载benchmark映射
        self.benchmark_mapping = self._load_benchmark_mapping()

        # 执行统计
        self.total_executed = 0
        self.successful = 0
        self.failed = 0
        self.execution_times = []

        # 设置随机种子
        random.seed(self.random_seed)

    def _load_benchmark_mapping(self) -> Dict:
        """
        加载benchmark映射文件

        Returns:
            benchmark映射字典
        """
        mapping = {}
        mapping_file = Path(self.benchmark_mapping_file)

        if not mapping_file.exists():
            print(f"警告: benchmark映射文件不存在: {self.benchmark_mapping_file}")
            return mapping

        print(f"加载benchmark映射: {self.benchmark_mapping_file}")
        with open(mapping_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    benchmark = entry.get('benchmark', '')
                    mapping[benchmark] = {
                        'data_test_dir': entry.get('data_test_dir', ''),
                        'data_test_max_num': entry.get('data_test_max_num', 100)
                    }
                except json.JSONDecodeError:
                    continue

        print(f"  已加载 {len(mapping)} 个benchmark映射")
        return mapping

    def _get_random_test_cases(self, benchmark: str) -> List[int]:
        """
        为指定benchmark随机选择测试用例

        Args:
            benchmark: benchmark名称

        Returns:
            随机选择的测试用例索引列表
        """
        # 获取最大测试用例数
        max_num = self.benchmark_mapping.get(benchmark, {}).get('data_test_max_num', 100)

        # 确定要选择的数量
        num_to_select = min(self.num_test_cases, max_num)

        # 随机选择测试用例索引
        all_indices = list(range(max_num))
        selected_indices = random.sample(all_indices, num_to_select)

        return selected_indices

    async def check_reward_server_health(self) -> bool:
        """
        检查Reward Server健康状态

        Returns:
            服务器是否健康
        """
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.reward_server_url}/health") as response:
                    if response.status == 200:
                        print("✓ Reward Server运行正常")
                        return True
                    else:
                        print(f"⚠️ Reward Server响应异常: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 无法连接到Reward Server: {e}")
            return False

    def _prepare_request_data(self, test_record: Dict) -> Dict:
        """
        准备请求数据

        Args:
            test_record: 测试记录

        Returns:
            准备好的请求数据
        """
        # 提取必要信息
        workflow_code = test_record.get('input', {}).get('response', '')
        data_source = test_record.get('data_source', '')

        # 获取原始的extra_info（如果有的话）
        original_extra_info = test_record.get('input', {}).get('extra_info', {})

        # data_source已经是正确的benchmark名称
        benchmark = data_source

        # 从benchmark映射中获取数据路径和测试用例
        if benchmark in self.benchmark_mapping:
            data_test_dir = self.benchmark_mapping[benchmark]['data_test_dir']
            test_cases = self._get_random_test_cases(benchmark)

            # 构建新的extra_info，包含data_path和test_cases
            extra_info = {
                **original_extra_info,  # 保留原始的extra_info
                'test_cases': test_cases,
                'data_path': data_test_dir
            }

            print(f"  - 测试数据路径: {data_test_dir}")
            print(f"  - 测试用例数量: {len(test_cases)}")
        else:
            # 如果没有映射，使用原始的extra_info
            extra_info = original_extra_info
            print(f"  警告: 未找到{benchmark}的映射，使用默认配置")
        
        # 构建请求数据
        request_data = {
            'data_source': benchmark,
            'solution_str': workflow_code,
            'ground_truth': 'default',
            'extra_info': extra_info
        }
        # print(request_data)

        return request_data

    async def execute_single_workflow(self, test_record: Dict, retry_count: int = 0) -> Dict:
        """
        执行单个workflow测试

        Args:
            test_record: 测试记录
            retry_count: 当前重试次数

        Returns:
            执行结果
        """
        test_id = test_record.get('test_id', 'unknown')
        line_number = test_record.get('line_number', None)

        print(f"\n执行测试: {test_id}")
        if line_number:
            print(f"  - 原始文件行号: {line_number}")
        print(f"  - Data Source: {test_record.get('data_source')}")
        print(f"  - Operators: {test_record.get('operators_group')}")

        start_time = time.time()
        result = {
            'test_id': test_id,
            'line_number': line_number,  # 保留原始文件行号
            'source_file': test_record.get('source_file'),  # 保留源文件路径
            'timestamp': datetime.now().isoformat(),
            'data_source': test_record.get('data_source'),
            'operators_group': test_record.get('operators_group'),
            'input': {  # 保存完整的输入信息
                'workflow_code': test_record.get('input', {}).get('workflow_code', ''),
                'prompt': test_record.get('input', {}).get('prompt', ''),
                'benchmark': test_record.get('input', {}).get('benchmark', ''),
                'extra_info': test_record.get('input', {}).get('extra_info', {})
            },
            'metadata': test_record.get('metadata', {}),  # 保留元数据
            'success': False,
            'score': 0.0,
            'execution_time': 0,
            'error': None,
            'retry_count': retry_count
        }

        try:
            # 准备请求数据
            request_data = self._prepare_request_data(test_record)

            # 发送请求到Reward Server
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.reward_server_url}/compute_score",
                    json=request_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    response_data = await response.json()

                    # 更新结果
                    result['success'] = response_data.get('success', False)
                    result['score'] = response_data.get('score', 0.0)
                    result['message'] = response_data.get('message', '')
                    result['details'] = response_data.get('details', {})

                    if result['success']:
                        print(f"  ✓ 执行成功，得分: {result['score']:.2f}")
                        self.successful += 1
                    else:
                        error_msg = response_data.get('error', '未知错误')
                        print(f"  ❌ 执行失败: {error_msg}")
                        result['error'] = error_msg
                        self.failed += 1

        except asyncio.TimeoutError:
            error_msg = f"请求超时 ({self.timeout}秒)"
            print(f"  ⚠️ {error_msg}")
            result['error'] = error_msg

            # 重试逻辑
            if retry_count < self.max_retries - 1:
                print(f"  正在重试... ({retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
                return await self.execute_single_workflow(test_record, retry_count + 1)
            else:
                self.failed += 1

        except Exception as e:
            error_msg = f"执行异常: {str(e)}"
            print(f"  ❌ {error_msg}")
            result['error'] = error_msg
            result['traceback'] = traceback.format_exc()
            self.failed += 1

        finally:
            # 计算执行时间
            execution_time = time.time() - start_time
            result['execution_time'] = round(execution_time, 2)
            self.execution_times.append(execution_time)
            self.total_executed += 1

        return result

    async def execute_batch_grouped(self, test_records: List[Dict], concurrency: int = 5,
                                    output_dir: str = "results") -> List[Dict]:
        """
        按data_source和operator_group分组执行workflow测试

        Args:
            test_records: 测试记录列表
            concurrency: 并发数量
            output_dir: 输出目录

        Returns:
            执行结果列表
        """
        all_results = []
        output_dir = Path(output_dir)

        # 首先按data_source分组
        grouped_by_datasource = {}
        for record in test_records:
            data_source = record.get('data_source', 'unknown')
            if data_source not in grouped_by_datasource:
                grouped_by_datasource[data_source] = []
            grouped_by_datasource[data_source].append(record)

        print(f"\n" + "="*60)
        print(f"开始分组执行 {len(test_records)} 个workflow测试")
        print(f"并发数: {concurrency}")
        print(f"分组数: {len(grouped_by_datasource)} 个data_source")
        print("="*60)

        # 按data_source执行
        for ds_idx, (data_source, ds_records) in enumerate(grouped_by_datasource.items(), 1):
            print(f"\n{'='*40}")
            print(f"[{ds_idx}/{len(grouped_by_datasource)}] Data Source: {data_source}")
            print(f"共 {len(ds_records)} 个workflow")
            print(f"{'='*40}")

            # 在每个data_source内按operator_group分组
            grouped_by_operators = {}
            for record in ds_records:
                operators_group = record.get('operators_group', 'unknown')
                if operators_group not in grouped_by_operators:
                    grouped_by_operators[operators_group] = []
                grouped_by_operators[operators_group].append(record)

            # 按operator_group执行
            for op_idx, (operators_group, op_records) in enumerate(grouped_by_operators.items(), 1):
                print(f"\n  [{op_idx}/{len(grouped_by_operators)}] Operators: {operators_group}")
                print(f"      共 {len(op_records)} 个测试")

                group_results = []

                # 分批并发执行
                for i in range(0, len(op_records), concurrency):
                    batch = op_records[i:i+concurrency]
                    batch_num = i // concurrency + 1
                    total_batches = (len(op_records) + concurrency - 1) // concurrency

                    print(f"      执行批次 {batch_num}/{total_batches}")

                    # 并发执行当前批次
                    batch_tasks = [self.execute_single_workflow(record) for record in batch]
                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                    # 处理结果
                    for idx, result in enumerate(batch_results):
                        if isinstance(result, Exception):
                            # 如果是异常，创建错误结果
                            error_result = {
                                'test_id': batch[idx].get('test_id', 'unknown'),
                                'data_source': data_source,
                                'operators_group': operators_group,
                                'success': False,
                                'error': str(result),
                                'traceback': traceback.format_exc()
                            }
                            group_results.append(error_result)
                        else:
                            group_results.append(result)

                    success_count = sum(1 for r in batch_results if isinstance(r, dict) and r.get('success'))
                    print(f"      批次完成: 成功 {success_count}/{len(batch)}")

                # 立即保存该组的结果
                self._save_group_results(group_results, data_source, operators_group, output_dir)
                all_results.extend(group_results)

                print(f"      ✓ {data_source}/{operators_group} 组结果已保存")

        return all_results

    def _save_group_results(self, results: List[Dict], data_source: str,
                           operators_group: str, output_dir: Path):
        """
        保存单个组的执行结果

        Args:
            results: 该组的执行结果
            data_source: data_source名称
            operators_group: operators组合名称
            output_dir: 输出目录
        """
        # 创建分类目录
        category_dir = output_dir / data_source / operators_group
        category_dir.mkdir(parents=True, exist_ok=True)

        # 保存测试结果（包含完整输入输出）
        result_file = category_dir / 'test_results_with_input.jsonl'
        with open(result_file, 'a', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

        # 创建输入输出映射文件（简化版，便于快速查看对应关系）
        mapping_file = category_dir / 'input_output_mapping.jsonl'
        with open(mapping_file, 'a', encoding='utf-8') as f:
            for result in results:
                mapping_record = {
                    'line_number': result.get('line_number'),
                    'test_id': result.get('test_id'),
                    'source_file': result.get('source_file'),
                    'workflow_code_snippet': result.get('input', {}).get('workflow_code', '')[:200] + '...',  # 前200字符
                    'success': result.get('success'),
                    'score': result.get('score'),
                    'error': result.get('error')
                }
                f.write(json.dumps(mapping_record, ensure_ascii=False) + '\n')

        # 保存失败案例（包含完整输入）
        failed_results = [r for r in results if not r.get('success', False)]
        if failed_results:
            failed_file = category_dir / 'failed_cases_with_input.jsonl'
            with open(failed_file, 'a', encoding='utf-8') as f:
                for result in failed_results:
                    f.write(json.dumps(result, ensure_ascii=False) + '\n')

        # 计算并保存统计信息
        stats = {
            'data_source': data_source,
            'operators_group': operators_group,
            'total': len(results),
            'successful': sum(1 for r in results if r.get('success', False)),
            'failed': sum(1 for r in results if not r.get('success', False)),
            'success_rate': sum(1 for r in results if r.get('success', False)) / len(results) if results else 0,
            'average_score': sum(r.get('score', 0) for r in results if r.get('success', False)) /
                           sum(1 for r in results if r.get('success', False)) if any(r.get('success', False) for r in results) else 0,
            'timestamp': datetime.now().isoformat()
        }

        stats_file = category_dir / 'statistics.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

    async def execute_batch(self, test_records: List[Dict], batch_size: int = 5) -> List[Dict]:
        """
        批量执行workflow测试（保留旧接口，内部调用新的分组执行方法）

        Args:
            test_records: 测试记录列表
            batch_size: 批次大小（作为并发数使用）

        Returns:
            执行结果列表
        """
        # 调用新的分组执行方法
        return await self.execute_batch_grouped(test_records, concurrency=batch_size)

    def save_results(self, results: List[Dict], output_dir: str = "results"):
        """
        保存执行结果，按data_source和operators_group分类

        Args:
            results: 执行结果列表
            output_dir: 输出目录
        """
        output_dir = Path(output_dir)

        # 按分类保存结果
        for result in results:
            data_source = result.get('data_source', 'unknown')
            operators_group = result.get('operators_group', 'unknown')

            # 创建分类目录
            category_dir = output_dir / data_source / operators_group
            category_dir.mkdir(parents=True, exist_ok=True)

            # 保存完整结果（包含输入）
            result_file = category_dir / 'test_results_with_input.jsonl'
            with open(result_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

            # 保存输入输出映射（简化版）
            mapping_file = category_dir / 'input_output_mapping.jsonl'
            with open(mapping_file, 'a', encoding='utf-8') as f:
                mapping_record = {
                    'line_number': result.get('line_number'),
                    'test_id': result.get('test_id'),
                    'source_file': result.get('source_file'),
                    'workflow_code_snippet': result.get('input', {}).get('workflow_code', '')[:200] + '...',
                    'success': result.get('success'),
                    'score': result.get('score'),
                    'error': result.get('error')
                }
                f.write(json.dumps(mapping_record, ensure_ascii=False) + '\n')

            # 如果是失败的案例，保存到failed_cases_with_input.jsonl
            if not result.get('success', False):
                failed_file = category_dir / 'failed_cases_with_input.jsonl'
                with open(failed_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(result, ensure_ascii=False) + '\n')

        # 保存完整结果到raw目录（包含所有信息）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        raw_file = output_dir / 'raw' / f'execution_results_complete_{timestamp}.jsonl'
        raw_file.parent.mkdir(parents=True, exist_ok=True)

        with open(raw_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

        # 创建索引文件，记录行号和test_id的对应关系
        index_file = output_dir / 'raw' / f'result_index_{timestamp}.jsonl'
        with open(index_file, 'w', encoding='utf-8') as f:
            for result in results:
                index_record = {
                    'line_number': result.get('line_number'),
                    'test_id': result.get('test_id'),
                    'data_source': result.get('data_source'),
                    'operators_group': result.get('operators_group'),
                    'success': result.get('success'),
                    'score': result.get('score')
                }
                f.write(json.dumps(index_record, ensure_ascii=False) + '\n')

        print(f"\n结果已保存至: {output_dir}")
        print(f"  - 完整结果: test_results_with_input.jsonl")
        print(f"  - 映射关系: input_output_mapping.jsonl")
        print(f"  - 索引文件: raw/result_index_{timestamp}.jsonl")

    def print_statistics(self):
        """打印执行统计信息"""
        print("\n" + "="*60)
        print("执行统计")
        print("="*60)
        print(f"总执行数: {self.total_executed}")
        print(f"成功数: {self.successful}")
        print(f"失败数: {self.failed}")

        if self.total_executed > 0:
            success_rate = (self.successful / self.total_executed) * 100
            print(f"成功率: {success_rate:.1f}%")

        if self.execution_times:
            avg_time = sum(self.execution_times) / len(self.execution_times)
            min_time = min(self.execution_times)
            max_time = max(self.execution_times)
            print(f"\n执行时间统计:")
            print(f"  - 平均: {avg_time:.2f}秒")
            print(f"  - 最短: {min_time:.2f}秒")
            print(f"  - 最长: {max_time:.2f}秒")


async def main():
    """主函数 - 用于测试"""
    import yaml
    from data_processor import DataProcessor

    # 加载配置
    config_path = Path('config.yaml')
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    # 创建执行器
    executor = WorkflowExecutor(config)

    # 检查服务器健康
    if not await executor.check_reward_server_health():
        print("请确保Reward Server正在运行")
        return

    # 加载测试数据
    processor = DataProcessor(config)
    input_file = '../baseline/test_IMO_0922_QZH_with_responses.jsonl'

    if Path(input_file).exists():
        # 处理数据
        test_records = processor.process_file(input_file)

        # 执行测试（只测试前5个）
        test_subset = test_records[:5]
        results = await executor.execute_batch(test_subset, batch_size=2)

        # 保存结果
        executor.save_results(results)

        # 打印统计
        executor.print_statistics()
    else:
        print(f"输入文件不存在: {input_file}")


if __name__ == "__main__":
    asyncio.run(main())