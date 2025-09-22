#!/usr/bin/env python
"""
Main test script for evaluating CoT and Self-Consistency workflows
on GSM8K, MBPP, and HumanEval benchmarks using the reward server.
"""

import os
import sys
import json
import yaml
import random
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from workflow_templates import get_workflow_template


class WorkflowEvaluator:
    """Evaluator for CoT and Self-Consistency workflows"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the evaluator with configuration"""
        self.config = self._load_config(config_path)
        self.reward_server_url = self.config['reward_server']['url']
        self.timeout = self.config['reward_server']['timeout']
        self.samples_per_benchmark = self.config['test']['samples_per_benchmark']
        self.results_dir = Path(self.config['output']['results_dir'])
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Load benchmark mapping
        self.benchmark_mapping = self._load_benchmark_mapping()

        print(f"初始化评估器...")
        print(f"  Reward Server: {self.reward_server_url}")
        print(f"  每个benchmark测试样本数: {self.samples_per_benchmark}")
        print(f"  结果目录: {self.results_dir}")

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            # Create default config if not exists
            default_config = {
                'reward_server': {
                    'url': 'http://localhost:8899',
                    'timeout': 300
                },
                'test': {
                    'samples_per_benchmark': 200,
                    'benchmarks': ['gsm8k', 'mbpp', 'humaneval']
                },
                'data': {
                    'base_path': '../Processed_dataset'
                },
                'output': {
                    'results_dir': './results',
                    'save_intermediate': True
                }
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            print(f"已创建默认配置文件: {config_path}")
            return default_config

        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_benchmark_mapping(self) -> Dict[str, Dict]:
        """Load benchmark mapping from ScoreFlow/benchmark_mapping.jsonl"""
        mapping_file = Path("../ScoreFlow/bm_local.jsonl")
        benchmark_map = {}

        if not mapping_file.exists():
            print(f"警告: benchmark_mapping.jsonl 不存在，使用默认路径")
            return {}

        with open(mapping_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                benchmark_map[entry['benchmark']] = entry

        return benchmark_map

    def load_random_samples(self, benchmark: str, n_samples: int) -> Tuple[List[Dict], List[int]]:
        """
        Load random samples from benchmark test data

        Args:
            benchmark: Benchmark name (gsm8k, mbpp, humaneval)
            n_samples: Number of samples to load

        Returns:
            Tuple of (samples, indices)
        """
        # Get data path from benchmark mapping
        if benchmark in self.benchmark_mapping:
            data_path = Path(self.benchmark_mapping[benchmark]['data_test_dir'])
        else:
            # Fallback to default paths
            print(f"警告: {benchmark} 不在 benchmark_mapping 中，使用默认路径")
            benchmark_map = {
                'humaneval': 'human_eval',
                'gsm8k': 'gsm8k',
                'mbpp': 'mbpp'
            }
            if benchmark in benchmark_map:
                data_path = Path("../Processed_dataset") / benchmark_map[benchmark] / 'test.jsonl'
            else:
                raise ValueError(f"未知的benchmark: {benchmark}")

        if not data_path.exists():
            raise FileNotFoundError(f"测试数据文件不存在: {data_path}")

        # Load all samples
        samples = []
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                samples.append(json.loads(line))

        # Random sample
        total_samples = len(samples)
        original_n_samples = n_samples
        n_samples = min(n_samples, total_samples)

        # 如果请求的样本数大于可用样本数，发出警告
        if original_n_samples > total_samples:
            print(f"  ⚠️ 警告: 请求{original_n_samples}个样本，但只有{total_samples}个可用")
            print(f"  将使用所有{total_samples}个样本")

        indices = random.sample(range(total_samples), n_samples)
        selected_samples = [samples[i] for i in indices]

        print(f"  从 {total_samples} 个样本中随机选择了 {n_samples} 个")

        return selected_samples, indices

    async def call_reward_server(self, workflow_code: str, benchmark: str, sample_indices: List[int]) -> Dict:
        """
        Call reward server to evaluate workflow

        Args:
            workflow_code: The workflow code to evaluate
            benchmark: Benchmark name
            sample_indices: Indices of test samples

        Returns:
            Evaluation result from reward server
        """
        # Get the correct data path from benchmark mapping
        if benchmark in self.benchmark_mapping:
            data_path = self.benchmark_mapping[benchmark]['data_test_dir']
        else:
            # Fallback for unmapped benchmarks
            benchmark_map = {
                'humaneval': 'human_eval',
                'gsm8k': 'gsm8k',
                'mbpp': 'mbpp'
            }
            if benchmark in benchmark_map:
                data_path = str(Path("../Processed_dataset") / benchmark_map[benchmark] / "test.jsonl")
            else:
                data_path = str(Path("../Processed_dataset") / benchmark / "test.jsonl")

        request_data = {
            "data_source": benchmark,
            "solution_str": workflow_code,
            "ground_truth": "default",
            "extra_info": {
                "test_cases": sample_indices,
                "data_path": data_path
            }
        }

        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.reward_server_url}/compute_score",
                    json=request_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    result = await response.json()
                    return {
                        "score": result.get("score", 0.0),
                        "success": result.get("success", False),
                        "message": result.get("message", ""),
                        "error": result.get("error", None)
                    }
        except asyncio.TimeoutError:
            print(f"    ⚠️ 请求超时 ({self.timeout}秒)")
            return {"score": 0.0, "success": False, "message": "Timeout", "error": "Request timeout"}
        except Exception as e:
            print(f"    ❌ 请求失败: {e}")
            return {"score": 0.0, "success": False, "message": str(e), "error": str(e)}

    async def evaluate_benchmark(self, benchmark: str) -> Dict:
        """
        Evaluate both workflows on a single benchmark

        Args:
            benchmark: Benchmark name

        Returns:
            Evaluation results dictionary
        """
        print(f"\n{'='*50}")
        print(f"测试 {benchmark.upper()}")
        print(f"{'='*50}")

        # Load random samples
        print(f"加载测试样本...")
        samples, indices = self.load_random_samples(benchmark, self.samples_per_benchmark)

        results = {
            "benchmark": benchmark,
            "n_samples": len(samples),
            "sample_indices": indices,
            "timestamp": datetime.now().isoformat()
        }

        # Test CoT workflow
        print(f"\n测试 Chain-of-Thought (CoT) workflow...")
        cot_workflow = get_workflow_template('cot')
        cot_result = await self.call_reward_server(cot_workflow, benchmark, indices)

        if cot_result['success']:
            print(f"  ✓ CoT准确率: {cot_result['score']*100:.1f}%")
        else:
            print(f"  ❌ CoT评估失败: {cot_result.get('error', 'Unknown error')}")

        results['cot'] = cot_result

        # Test Self-Consistency workflow
        print(f"\n测试 Self-Consistency workflow...")
        sc_workflow = get_workflow_template('self_consistency')
        sc_result = await self.call_reward_server(sc_workflow, benchmark, indices)

        if sc_result['success']:
            print(f"  ✓ Self-Consistency准确率: {sc_result['score']*100:.1f}%")
        else:
            print(f"  ❌ Self-Consistency评估失败: {sc_result.get('error', 'Unknown error')}")

        results['self_consistency'] = sc_result

        # Calculate improvement
        if cot_result['success'] and sc_result['success']:
            improvement = sc_result['score'] - cot_result['score']
            results['improvement'] = improvement
            print(f"\n📊 提升: {improvement*100:+.1f}%")
        else:
            results['improvement'] = None

        # Save intermediate results
        if self.config['output']['save_intermediate']:
            result_file = self.results_dir / f"{benchmark}_results.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 结果已保存至: {result_file}")

        return results

    async def run_all_benchmarks(self) -> List[Dict]:
        """Run evaluation on all configured benchmarks"""
        benchmarks = self.config['test']['benchmarks']
        all_results = []

        print(f"\n开始评估 {len(benchmarks)} 个benchmark: {', '.join(benchmarks)}")
        print(f"每个benchmark测试 {self.samples_per_benchmark} 个样本")

        for i, benchmark in enumerate(benchmarks, 1):
            print(f"\n[{i}/{len(benchmarks)}] {benchmark}")
            try:
                result = await self.evaluate_benchmark(benchmark)
                all_results.append(result)
            except Exception as e:
                print(f"  ❌ 评估失败: {e}")
                all_results.append({
                    "benchmark": benchmark,
                    "error": str(e),
                    "cot": {"success": False},
                    "self_consistency": {"success": False}
                })

        return all_results

    def generate_report(self, results: List[Dict]) -> str:
        """Generate final evaluation report"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("     CoT vs Self-Consistency 评估报告")
        report_lines.append("=" * 60)
        report_lines.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Reward Server: {self.reward_server_url}")
        report_lines.append(f"每个benchmark样本数: {self.samples_per_benchmark}")
        report_lines.append("")

        # Individual benchmark results
        successful_benchmarks = []
        for result in results:
            benchmark = result['benchmark']
            report_lines.append("-" * 60)
            report_lines.append(f"Benchmark: {benchmark.upper()}")
            report_lines.append("-" * 60)

            if result.get('error'):
                report_lines.append(f"❌ 评估失败: {result['error']}")
                continue

            cot = result.get('cot', {})
            sc = result.get('self_consistency', {})

            if cot.get('success'):
                cot_score = cot['score'] * 100
                report_lines.append(f"CoT准确率:              {cot_score:.1f}%")
            else:
                report_lines.append(f"CoT准确率:              失败")

            if sc.get('success'):
                sc_score = sc['score'] * 100
                report_lines.append(f"Self-Consistency准确率: {sc_score:.1f}%")
            else:
                report_lines.append(f"Self-Consistency准确率: 失败")

            if result.get('improvement') is not None:
                improvement = result['improvement'] * 100
                report_lines.append(f"提升:                   {improvement:+.1f}%")
                successful_benchmarks.append(result)

            report_lines.append("")

        # Overall statistics
        if successful_benchmarks:
            report_lines.append("=" * 60)
            report_lines.append("总体统计")
            report_lines.append("-" * 60)

            avg_cot = sum(r['cot']['score'] for r in successful_benchmarks) / len(successful_benchmarks)
            avg_sc = sum(r['self_consistency']['score'] for r in successful_benchmarks) / len(successful_benchmarks)
            avg_improvement = avg_sc - avg_cot

            report_lines.append(f"平均CoT准确率:          {avg_cot*100:.1f}%")
            report_lines.append(f"平均Self-Consistency:   {avg_sc*100:.1f}%")
            report_lines.append(f"平均提升:               {avg_improvement*100:+.1f}%")
            report_lines.append("")

            if avg_improvement > 0:
                report_lines.append("结论: Self-Consistency方法在测试的benchmark上")
                report_lines.append(f"     平均优于CoT方法 {avg_improvement*100:.1f} 个百分点")
            else:
                report_lines.append("结论: CoT方法在测试的benchmark上表现更好")

        report_lines.append("=" * 60)
        return "\n".join(report_lines)

    async def run(self):
        """Main execution function"""
        print("\n" + "="*60)
        print("   CoT vs Self-Consistency Workflow 评估系统")
        print("="*60)

        # Check reward server health
        print("\n检查Reward Server状态...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.reward_server_url}/health") as response:
                    if response.status == 200:
                        print("  ✓ Reward Server运行正常")
                    else:
                        print(f"  ⚠️ Reward Server响应异常: {response.status}")
        except Exception as e:
            print(f"  ❌ 无法连接到Reward Server: {e}")
            print("  请确保Reward Server正在运行")
            return

        # Run evaluations
        all_results = await self.run_all_benchmarks()

        # Generate and save report
        report = self.generate_report(all_results)
        print("\n" + report)

        # Save report to file
        report_file = self.results_dir / "summary_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 报告已保存至: {report_file}")

        # Save all results as JSON
        all_results_file = self.results_dir / "all_results.json"
        with open(all_results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"📊 完整结果已保存至: {all_results_file}")

        print("\n✅ 评估完成!")


async def main():
    """Main entry point"""
    evaluator = WorkflowEvaluator()
    await evaluator.run()


if __name__ == "__main__":
    asyncio.run(main())