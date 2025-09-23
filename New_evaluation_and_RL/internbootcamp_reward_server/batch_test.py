#!/usr/bin/env python3
"""
批量测试InternBootcamp Reward Server脚本
从JSONL文件读取数据并发送批量请求
"""

import json
import asyncio
import aiohttp
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
from datetime import datetime
import csv

# 注意：Token追踪在服务器端进行，客户端通过API获取统计

# 简化的workflow模板
SIMPLIFIED_WORKFLOW = """<code>
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        # 只保留一个generate操作符
        self.generate = operator.Generate(self.llm, self.problem_text)

    async def run_workflow(self):
        \"\"\"
        使用单一generate操作符的简化工作流
        \"\"\"
        import asyncio

        # 一次性生成完整解决方案
        complete_solution = await self.generate(
            context=self.problem_text
        )

        return complete_solution
</code>"""


class BatchTester:
    def __init__(self, base_url: str, max_concurrent: int = 10):
        """
        初始化批量测试器
        
        Args:
            base_url: 服务器基础URL
            max_concurrent: 最大并发请求数
        """
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None
        self.results = []
        self.total_processed = 0
        self.total_success = 0
        self.total_failed = 0
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent, force_close=True)
        timeout = aiohttp.ClientTimeout(total=300)  # 5分钟超时
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
            await asyncio.sleep(0.1)  # 确保连接正确关闭
    
    async def health_check(self) -> bool:
        """检查服务器健康状态"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ 服务器健康检查成功: {data}")
                    return True
                else:
                    print(f"✗ 服务器健康检查失败: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"✗ 服务器健康检查错误: {e}")
            return False
    
    def prepare_request_data(self, jsonl_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备请求数据
        
        Args:
            jsonl_entry: JSONL文件中的一行数据
            
        Returns:
            准备好的请求数据
        """
        # 构建请求数据
        request_data = {
            "data_source": jsonl_entry.get("data_source", "internbootcamp"),
            "solution_str": SIMPLIFIED_WORKFLOW,  # 使用简化的workflow
            "ground_truth": jsonl_entry.get("reward_model", {}).get("ground_truth", "default")
        }
        
        # 添加extra_info
        if "extra_info" in jsonl_entry:
            request_data["extra_info"] = jsonl_entry["extra_info"]
        else:
            # 如果没有extra_info，创建一个基本的
            request_data["extra_info"] = {
                "task_name": "unknown",
                "entry_id": self.total_processed,
                "task_type": "general",
                "timestamp": datetime.now().isoformat()
            }
            
        return request_data
    
    async def compute_single_score(
        self, 
        request_data: Dict[str, Any],
        request_id: int
    ) -> Dict[str, Any]:
        """
        为单个请求计算分数
        
        Args:
            request_data: 请求数据
            request_id: 请求ID
            
        Returns:
            结果字典
        """
        async with self.semaphore:
            start_time = time.time()
            task_name = request_data.get('extra_info', {}).get('task_name', 'unknown')
            entry_id = request_data.get('extra_info', {}).get('entry_id', request_id)
            
            try:
                async with self.session.post(
                    f"{self.base_url}/compute_score",
                    json=request_data
                ) as response:
                    elapsed_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            self.total_success += 1
                            score = result.get('score', 0)
                            
                            # 立即输出每条结果的reward
                            print(f"  ✓ [ID:{entry_id:4d}] {task_name:30s} | Reward: {score:.4f} | 耗时: {elapsed_time:6.2f}秒")
                            
                            return {
                                'request_id': request_id,
                                'entry_id': entry_id,
                                'success': True,
                                'score': score,
                                'elapsed_time': elapsed_time,
                                'message': result.get('message', ''),
                                'task_name': task_name
                            }
                        else:
                            self.total_failed += 1
                            error = result.get('error', 'Unknown error')
                            
                            # 输出失败信息
                            print(f"  ✗ [ID:{entry_id:4d}] {task_name:30s} | Reward: 0.0000 | 错误: {error[:50]}")
                            
                            return {
                                'request_id': request_id,
                                'entry_id': entry_id,
                                'success': False,
                                'score': 0.0,
                                'error': error,
                                'elapsed_time': elapsed_time,
                                'task_name': task_name
                            }
                    else:
                        self.total_failed += 1
                        error_text = await response.text()
                        
                        # 输出HTTP错误
                        print(f"  ✗ [ID:{entry_id:4d}] {task_name:30s} | Reward: 0.0000 | HTTP {response.status}")
                        
                        return {
                            'request_id': request_id,
                            'entry_id': entry_id,
                            'success': False,
                            'score': 0.0,
                            'error': f"HTTP {response.status}: {error_text[:200]}",
                            'elapsed_time': elapsed_time,
                            'task_name': task_name
                        }
                        
            except asyncio.TimeoutError:
                self.total_failed += 1
                
                # 输出超时错误
                print(f"  ✗ [ID:{entry_id:4d}] {task_name:30s} | Reward: 0.0000 | 超时")
                
                return {
                    'request_id': request_id,
                    'entry_id': entry_id,
                    'success': False,
                    'score': 0.0,
                    'error': '请求超时 (超过300秒)',
                    'elapsed_time': time.time() - start_time,
                    'task_name': task_name
                }
            except Exception as e:
                self.total_failed += 1
                
                # 输出其他错误
                print(f"  ✗ [ID:{entry_id:4d}] {task_name:30s} | Reward: 0.0000 | 错误: {str(e)[:50]}")
                
                return {
                    'request_id': request_id,
                    'entry_id': entry_id,
                    'success': False,
                    'score': 0.0,
                    'error': f"请求错误: {str(e)}",
                    'elapsed_time': time.time() - start_time,
                    'task_name': task_name
                }
    
    async def process_batch(self, batch: List[Dict[str, Any]], batch_id: int):
        """
        处理一批请求
        
        Args:
            batch: 批量数据
            batch_id: 批次ID
        """
        print(f"\n处理批次 {batch_id + 1}, 包含 {len(batch)} 个请求...")
        
        # 创建所有请求的任务
        tasks = []
        for i, jsonl_entry in enumerate(batch):
            request_data = self.prepare_request_data(jsonl_entry)
            request_id = batch_id * 100 + i  # 生成唯一的请求ID
            task = self.compute_single_score(request_data, request_id)
            tasks.append(task)
            self.total_processed += 1
        
        # 并发执行所有任务
        batch_results = await asyncio.gather(*tasks)
        self.results.extend(batch_results)
        
        # 打印批次统计
        batch_success = sum(1 for r in batch_results if r['success'])
        print(f"批次 {batch_id + 1} 完成: {batch_success}/{len(batch)} 成功")
    
    async def run_test(self, jsonl_file: Path, batch_size: int = 100, max_entries: Optional[int] = None):
        """
        运行批量测试
        
        Args:
            jsonl_file: JSONL文件路径
            batch_size: 每批处理的数量
            max_entries: 最大处理条目数（None表示处理所有）
        """
        # 首先检查服务器健康状态
        print("\n检查服务器健康状态...")
        if not await self.health_check():
            print("服务器健康检查失败，终止测试")
            return []
        
        # 读取JSONL文件
        print(f"\n读取文件: {jsonl_file}")
        entries = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if max_entries and i >= max_entries:
                    break
                try:
                    entry = json.loads(line.strip())
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    print(f"警告: 第 {i+1} 行JSON解析失败: {e}")
                    continue
        
        print(f"成功读取 {len(entries)} 条数据")
        
        if not entries:
            print("没有有效数据，终止测试")
            return []
        
        # 分批处理
        total_batches = (len(entries) + batch_size - 1) // batch_size
        print(f"将分 {total_batches} 批处理，每批最多 {batch_size} 个请求")
        print(f"最大并发数: {self.max_concurrent}")
        
        start_time = time.time()
        
        for batch_id in range(total_batches):
            batch_start = batch_id * batch_size
            batch_end = min(batch_start + batch_size, len(entries))
            batch = entries[batch_start:batch_end]
            
            await self.process_batch(batch, batch_id)
            
            # 显示进度
            progress = (batch_end / len(entries)) * 100
            print(f"总进度: {batch_end}/{len(entries)} ({progress:.1f}%)")
            print(f"累计成功: {self.total_success}, 累计失败: {self.total_failed}")
        
        total_time = time.time() - start_time
        print(f"\n总耗时: {total_time:.2f}秒")
        
        return self.results


def print_summary(results: List[Dict[str, Any]]):
    """打印测试结果总结"""
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    # Token统计现在通过服务器API获取，在main()函数中处理
    
    if not results:
        print("没有测试结果")
        return
    
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total - successful
    
    print(f"\n总请求数: {total}")
    print(f"成功: {successful} ({successful/total*100:.1f}%)")
    print(f"失败: {failed} ({failed/total*100:.1f}%)")
    
    if successful > 0:
        success_results = [r for r in results if r['success']]
        scores = [r['score'] for r in success_results]
        times = [r['elapsed_time'] for r in success_results]
        
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n成功请求统计:")
        print(f"  【Reward统计】")
        print(f"    平均Reward: {avg_score:.4f}")
        print(f"    最低Reward: {min_score:.4f}")
        print(f"    最高Reward: {max_score:.4f}")
        print(f"  【耗时统计】")
        print(f"    平均耗时: {avg_time:.2f}秒")
        print(f"    最短耗时: {min_time:.2f}秒")
        print(f"    最长耗时: {max_time:.2f}秒")
        
        # Reward分布统计
        reward_distribution = {
            '1.0': sum(1 for s in scores if s == 1.0),
            '0.5-0.99': sum(1 for s in scores if 0.5 <= s < 1.0),
            '0.1-0.49': sum(1 for s in scores if 0.1 <= s < 0.5),
            '0.01-0.09': sum(1 for s in scores if 0.01 <= s < 0.1),
            '0.0': sum(1 for s in scores if s == 0.0)
        }
        
        print(f"  【Reward分布】")
        for range_name, count in reward_distribution.items():
            if count > 0:
                percentage = (count / len(scores)) * 100
                print(f"    {range_name:10s}: {count:4d} ({percentage:5.1f}%)")
    
    if failed > 0:
        print(f"\n失败请求摘要:")
        error_counts = {}
        for r in results:
            if not r['success']:
                error_type = r['error'].split(':')[0] if ':' in r['error'] else r['error'][:50]
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {error_type}: {count}次")
    
    # 按任务类型统计
    task_stats = {}
    for r in results:
        task_name = r.get('task_name', 'unknown')
        if task_name not in task_stats:
            task_stats[task_name] = {'total': 0, 'success': 0}
        task_stats[task_name]['total'] += 1
        if r['success']:
            task_stats[task_name]['success'] += 1
    
    if len(task_stats) > 1:
        print(f"\n按任务类型统计:")
        for task_name, stats in sorted(task_stats.items()):
            success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"  {task_name}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")


def save_rewards_csv(results: List[Dict[str, Any]], csv_path: Path):
    """
    保存reward详情到CSV文件
    
    Args:
        results: 结果列表
        csv_path: CSV文件路径
    """
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(['Entry_ID', 'Task_Name', 'Success', 'Reward', 'Elapsed_Time', 'Error'])
        
        # 写入数据
        for r in results:
            writer.writerow([
                r.get('entry_id', ''),
                r.get('task_name', ''),
                'Yes' if r.get('success') else 'No',
                f"{r.get('score', 0):.4f}",
                f"{r.get('elapsed_time', 0):.2f}",
                r.get('error', '') if not r.get('success') else ''
            ])
    
    print(f"Reward详情已保存到CSV: {csv_path}")


async def fetch_and_print_token_stats(base_url: str):
    """
    从服务器获取并打印Token统计
    
    Args:
        base_url: 服务器基础URL
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/token_stats") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('summary', {}).get('total_tokens', 0) > 0:
                        summary = data['summary']
                        details = data.get('details', {})
                        
                        print(f"\n{'💎'*30}")
                        print("="*80)
                        print("🏆 服务器端Token使用统计 (从API获取)")
                        print("="*80)
                        print(f"  📝 总Prompt Tokens:      {summary['total_prompt_tokens']:,}")
                        print(f"  💬 总Completion Tokens:  {summary['total_completion_tokens']:,}")
                        print(f"  🎯 总Tokens:             {summary['total_tokens']:,}  🔥🔥🔥")
                        print(f"  🔄 总API调用次数:        {summary['total_api_calls']}")
                        print(f"  📊 处理的Workflows数:    {summary['workflows_processed']}")
                        
                        if 'avg_tokens_per_workflow' in details:
                            print(f"  平均每个Workflow Tokens: {details['avg_tokens_per_workflow']:.0f}")
                        
                        if 'avg_tokens_per_call' in details:
                            print(f"  平均每次API调用Tokens: {details['avg_tokens_per_call']:.0f}")
                        
                        if 'estimated_cost_usd' in details:
                            print(f"  估算成本: ${details['estimated_cost_usd']:.4f}")
                        
                        print("="*80)
                        print(f"{'💎'*30}\n")
                        
                        # 返回数据以便保存
                        return data
                    else:
                        print(f"\n{'❌'*30}")
                        print("="*80)
                        print("⚠️ 服务器端没有Token统计数据！")
                        print("="*80)
                        print("  可能的原因:")
                        print("  1. API代理未返回usage字段")
                        print("  2. 所有workflow执行都失败了")
                        print("  3. Token追踪器未正确初始化")
                        print("="*80)
                        print(f"{'❌'*30}\n")
                        return None
                else:
                    print(f"\n⚠️ 无法获取Token统计: HTTP {response.status}")
                    return None
    except Exception as e:
        print(f"\n⚠️ 获取Token统计失败: {e}")
        return None


async def main():
    parser = argparse.ArgumentParser(description='批量测试InternBootcamp Reward Server')
    parser.add_argument('--host', type=str, default='localhost',
                       help='服务器主机地址 (默认: localhost)')
    parser.add_argument('--port', type=int, default=8900,
                       help='服务器端口 (默认: 8900)')
    parser.add_argument('--file', type=str,
                       default='../generate_parquet_and_jsonl/internbootcamp_data_test/train.jsonl',
                       help='JSONL文件路径')
    parser.add_argument('--max-concurrent', type=int, default=10,
                       help='最大并发请求数 (默认: 10)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='每批处理的数量 (默认: 100)')
    parser.add_argument('--max-entries', type=int,
                       help='最大处理条目数 (默认: 处理所有)')
    parser.add_argument('--output', type=str,
                       help='保存结果到JSON文件')
    parser.add_argument('--csv', type=str,
                       help='保存reward详情到CSV文件')
    
    args = parser.parse_args()
    
    # 构建服务器URL
    base_url = f"http://{args.host}:{args.port}"
    print(f"测试服务器: {base_url}")
    
    # 检查文件是否存在
    jsonl_file = Path(args.file)
    if not jsonl_file.exists():
        # 尝试相对路径
        jsonl_file = Path(__file__).parent / args.file
    
    if not jsonl_file.exists():
        print(f"✗ JSONL文件不存在: {args.file}")
        return 1
    
    # 创建测试器并运行测试
    async with BatchTester(base_url, args.max_concurrent) as tester:
        results = await tester.run_test(
            jsonl_file, 
            batch_size=args.batch_size,
            max_entries=args.max_entries
        )
    
    # 打印总结
    print_summary(results)
    
    # 从服务器获取token统计
    await fetch_and_print_token_stats(base_url)
    
    # 保存结果（如果指定）
    if results:
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {output_path}")
        
        if args.csv:
            csv_path = Path(args.csv)
            save_rewards_csv(results, csv_path)
        
        # 保存Token统计（从服务器获取）
        if args.output or args.csv:
            token_data = await fetch_and_print_token_stats(base_url)
            if token_data and token_data.get('summary', {}).get('total_tokens', 0) > 0:
                # 使用输出文件的目录
                if args.output:
                    output_dir = Path(args.output).parent
                else:
                    output_dir = Path(args.csv).parent
                
                # 保存到文件
                token_stats_file = output_dir / f"token_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(token_stats_file, 'w', encoding='utf-8') as f:
                    json.dump(token_data, f, ensure_ascii=False, indent=2)
                print(f"Token统计已保存到: {token_stats_file}")
    
    # 返回状态码
    all_success = all(r['success'] for r in results) if results else False
    return 0 if all_success else 1


if __name__ == '__main__':
    # Windows环境下的事件循环策略
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)