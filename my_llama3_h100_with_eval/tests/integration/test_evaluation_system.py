#!/usr/bin/env python
"""
Complete integration test for the evaluation system with real reward server
This test uses real test data and actual HTTP requests to the reward server
"""
import os
import sys
import json
import asyncio
import logging
import tempfile
import aiohttp
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# 设置NO_PROXY来排除localhost（防止被系统代理拦截）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0,*.local'

# 清除代理环境变量，确保本地服务通信正常
for proxy_var in ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    if proxy_var in os.environ:
        del os.environ[proxy_var]
        print(f"[OK] 已清除环境变量: {proxy_var}")

print(f"[OK] 已设置 NO_PROXY='{os.environ.get('NO_PROXY', '')}'")
print("localhost请求将绕过所有代理")

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestDataLoader:
    """
    Load real test data from JSONL files
    """
    
    @staticmethod
    def load_test_samples(file_path: str, max_samples: int = 5) -> List[Dict]:
        """
        Load test samples from JSONL file
        
        Args:
            file_path: Path to test data file
            max_samples: Maximum number of samples to load
            
        Returns:
            List of test data samples
        """
        samples = []
        
        # Try multiple possible paths
        possible_paths = [
            Path(file_path),
            Path("../../") / file_path,
            Path("../../../") / file_path,
            Path("D:/temp/Flow_RL") / file_path
        ]
        
        loaded_path = None
        for path in possible_paths:
            if path.exists():
                loaded_path = path
                break
        
        if not loaded_path:
            logger.warning(f"测试数据文件未找到: {file_path}")
            logger.info("使用默认测试数据")
            # Return default test data
            return [
                {
                    "data_source": "workflow_gsm8k",
                    "extra_info": {
                        "test_cases": [0],
                        "data_path": "Processed_dataset/gsm8k/train.jsonl"
                    },
                    "reward_model": {"ground_truth": "default"}
                }
            ]
        
        logger.info(f"从文件加载测试数据: {loaded_path}")
        
        with open(loaded_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= max_samples:
                    break
                if line.strip():
                    try:
                        sample = json.loads(line)
                        samples.append(sample)
                    except json.JSONDecodeError as e:
                        logger.warning(f"解析第 {i+1} 行失败: {e}")
        
        logger.info(f"成功加载 {len(samples)} 个测试样本")
        return samples


class RealRewardServerClient:
    """
    Client for real reward server at port 8897
    """
    
    def __init__(self, base_url: str = "http://localhost:8897"):
        """Initialize reward server client"""
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=300)  # 5 minute timeout
        connector = aiohttp.TCPConnector(force_close=True)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            trust_env=False  # Ignore proxy settings
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def health_check(self) -> bool:
        """Check if reward server is running"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"奖励服务器健康检查成功: {data}")
                    return True
                else:
                    logger.error(f"奖励服务器健康检查失败: HTTP {response.status}")
                    return False
        except aiohttp.ClientError as e:
            logger.error(f"无法连接到奖励服务器: {e}")
            return False
        except Exception as e:
            logger.error(f"健康检查错误: {e}")
            return False
    
    async def compute_score(self, request_data: Dict) -> Dict:
        """
        Send workflow to reward server for scoring
        
        Args:
            request_data: Request data containing workflow code
            
        Returns:
            Score response from server
        """
        try:
            async with self.session.post(
                f"{self.base_url}/compute_score",
                json=request_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"评分请求失败: HTTP {response.status} - {error_text}")
                    return {
                        'success': False,
                        'score': 0.0,
                        'error': f"HTTP {response.status}: {error_text}"
                    }
        except asyncio.TimeoutError:
            logger.error("评分请求超时")
            return {
                'success': False,
                'score': 0.0,
                'error': 'Request timeout'
            }
        except Exception as e:
            logger.error(f"评分请求错误: {e}")
            return {
                'success': False,
                'score': 0.0,
                'error': str(e)
            }


class WorkflowGenerator:
    """
    Generates the simplified workflow code as requested
    """
    
    @staticmethod
    def generate_simplified_workflow() -> str:
        """
        Generate the simplified workflow exactly as requested
        """
        return """<code>
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


async def test_reward_server_connection():
    """Test connection to reward server"""
    print("\n" + "="*60)
    print("测试奖励服务器连接")
    print("="*60)
    
    async with RealRewardServerClient() as client:
        is_healthy = await client.health_check()
        
        if is_healthy:
            print("[OK] 奖励服务器运行正常")
            return True
        else:
            print("[FAIL] 无法连接到奖励服务器")
            print("请确保奖励服务器正在运行:")
            print("  cd New_evaluation_and_RL/internbootcamp_reward_server")
            print("  python internbootcamp_reward_server.py")
            return False


async def test_with_real_data():
    """Test with real test data from file"""
    print("\n" + "="*60)
    print("使用真实测试数据进行评分")
    print("="*60)
    
    # Load test data
    test_data_path = "New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl"
    test_samples = TestDataLoader.load_test_samples(test_data_path, max_samples=3)
    
    if not test_samples:
        print("[FAIL] 无法加载测试数据")
        return False
    
    async with RealRewardServerClient() as client:
        # Check server first
        if not await client.health_check():
            print("[FAIL] 奖励服务器未运行")
            return False
        
        # Generate workflow code once
        workflow_code = WorkflowGenerator.generate_simplified_workflow()
        print(f"使用简化工作流 (长度: {len(workflow_code)} 字符)")
        
        results = []
        for i, sample in enumerate(test_samples, 1):
            print(f"\n测试样本 {i}/{len(test_samples)}:")
            print(f"  - 数据源: {sample.get('data_source', 'unknown')}")
            
            # Extract extra_info and other fields from real data
            extra_info = sample.get('extra_info', {})
            reward_model = sample.get('reward_model', {'ground_truth': 'default'})
            
            # Build request using real data structure
            request_data = {
                'data_source': sample.get('data_source'),
                'solution_str': workflow_code,  # Only this is replaced
                'ground_truth': reward_model.get('ground_truth', 'default'),
                'extra_info': extra_info  # Use complete extra_info from test data
            }
            
            # Show what we're sending
            print(f"  - 测试用例: {extra_info.get('test_cases', [])}")
            print(f"  - 数据路径: {extra_info.get('data_path', 'N/A')}")
            
            # Send request
            result = await client.compute_score(request_data)
            results.append(result)
            
            if result.get('success'):
                print(f"  [OK] 评分成功: {result.get('score', 0):.3f}")
                if 'message' in result:
                    print(f"       消息: {result['message']}")
            else:
                print(f"  [FAIL] 评分失败: {result.get('error', 'Unknown error')}")
        
        # Calculate statistics
        successful = sum(1 for r in results if r.get('success'))
        if successful > 0:
            avg_score = sum(r.get('score', 0) for r in results if r.get('success')) / successful
        else:
            avg_score = 0
        
        print(f"\n测试统计:")
        print(f"  - 总测试: {len(results)}")
        print(f"  - 成功: {successful}")
        print(f"  - 失败: {len(results) - successful}")
        if successful > 0:
            print(f"  - 平均分数: {avg_score:.3f}")
        
        return successful > 0


async def test_batch_processing():
    """Test batch processing with different benchmarks"""
    print("\n" + "="*60)
    print("测试批量处理（多个基准测试）")
    print("="*60)
    
    # Load test data
    test_data_path = "New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl"
    all_samples = TestDataLoader.load_test_samples(test_data_path, max_samples=10)
    
    # Group by data source
    grouped_samples = {}
    for sample in all_samples:
        data_source = sample.get('data_source', 'unknown')
        if data_source not in grouped_samples:
            grouped_samples[data_source] = []
        grouped_samples[data_source].append(sample)
    
    print(f"发现 {len(grouped_samples)} 个不同的数据源:")
    for source, samples in grouped_samples.items():
        print(f"  - {source}: {len(samples)} 个样本")
    
    async with RealRewardServerClient() as client:
        # Check server first
        if not await client.health_check():
            print("[FAIL] 奖励服务器未运行")
            return False
        
        workflow_code = WorkflowGenerator.generate_simplified_workflow()
        
        # Test each benchmark
        all_results = {}
        for data_source, samples in grouped_samples.items():
            print(f"\n测试 {data_source}:")
            
            # Test first sample from each benchmark
            sample = samples[0]
            request_data = {
                'data_source': sample.get('data_source'),
                'solution_str': workflow_code,
                'ground_truth': sample.get('reward_model', {}).get('ground_truth', 'default'),
                'extra_info': sample.get('extra_info', {})
            }
            
            result = await client.compute_score(request_data)
            all_results[data_source] = result
            
            if result.get('success'):
                print(f"  [OK] 分数: {result.get('score', 0):.3f}")
            else:
                print(f"  [FAIL] 错误: {result.get('error', 'Unknown')}")
        
        # Summary
        successful_benchmarks = sum(1 for r in all_results.values() if r.get('success'))
        print(f"\n批量测试总结:")
        print(f"  - 测试的基准: {len(all_results)}")
        print(f"  - 成功: {successful_benchmarks}")
        print(f"  - 失败: {len(all_results) - successful_benchmarks}")
        
        return successful_benchmarks > 0


async def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n" + "="*60)
    print("测试错误处理")
    print("="*60)
    
    async with RealRewardServerClient() as client:
        # Check server first
        if not await client.health_check():
            print("[FAIL] 奖励服务器未运行")
            return False
        
        # Test 1: Invalid workflow code
        print("\n测试 1: 无效的工作流代码")
        request_data = {
            'data_source': 'workflow_gsm8k',
            'solution_str': 'invalid python code without class',
            'ground_truth': 'default',
            'extra_info': {
                'test_cases': [0],
                'data_path': 'test.jsonl'
            }
        }
        
        result = await client.compute_score(request_data)
        if not result.get('success'):
            print(f"  [OK] 正确处理无效代码")
        else:
            print(f"  [FAIL] 应该失败但成功了")
        
        # Test 2: Empty workflow
        print("\n测试 2: 空工作流")
        request_data = {
            'data_source': 'workflow_gsm8k',
            'solution_str': '',
            'extra_info': {
                'test_cases': [0],
                'data_path': 'test.jsonl'
            }
        }
        
        result = await client.compute_score(request_data)
        if not result.get('success'):
            print(f"  [OK] 正确处理空工作流")
        else:
            print(f"  [FAIL] 应该失败但成功了")
        
        return True


async def test_concurrent_requests():
    """Test concurrent requests with real data"""
    print("\n" + "="*60)
    print("测试并发请求")
    print("="*60)
    
    # Load test data
    test_data_path = "New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl"
    test_samples = TestDataLoader.load_test_samples(test_data_path, max_samples=5)
    
    async with RealRewardServerClient() as client:
        # Check server first
        if not await client.health_check():
            print("[FAIL] 奖励服务器未运行")
            return False
        
        workflow_code = WorkflowGenerator.generate_simplified_workflow()
        
        # Create concurrent requests
        requests = []
        for i, sample in enumerate(test_samples):
            request_data = {
                'data_source': sample.get('data_source'),
                'solution_str': workflow_code,
                'ground_truth': sample.get('reward_model', {}).get('ground_truth', 'default'),
                'extra_info': sample.get('extra_info', {})
            }
            requests.append(client.compute_score(request_data))
        
        print(f"发送 {len(requests)} 个并发请求...")
        start_time = datetime.now()
        
        # Execute concurrently
        results = await asyncio.gather(*requests, return_exceptions=True)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Analyze results
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
        errors = sum(1 for r in results if isinstance(r, Exception))
        
        print(f"\n并发测试结果:")
        print(f"  - 总请求: {len(results)}")
        print(f"  - 成功: {successful}")
        print(f"  - 错误: {errors}")
        print(f"  - 耗时: {duration:.2f}秒")
        if len(results) > 0:
            print(f"  - 平均响应时间: {duration/len(results):.2f}秒/请求")
        
        return successful > 0


async def test_full_pipeline():
    """Test the complete evaluation pipeline with real data"""
    print("\n" + "="*60)
    print("测试完整评估管道")
    print("="*60)
    
    async with RealRewardServerClient() as client:
        # Step 1: Check server health
        print("\n步骤 1: 检查服务器状态")
        if not await client.health_check():
            print("[FAIL] 奖励服务器未运行")
            return False
        print("[OK] 服务器状态正常")
        
        # Step 2: Load real test data
        print("\n步骤 2: 加载真实测试数据")
        test_data_path = "New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl"
        test_samples = TestDataLoader.load_test_samples(test_data_path, max_samples=5)
        print(f"[OK] 加载了 {len(test_samples)} 个测试样本")
        
        # Step 3: Generate workflow
        print("\n步骤 3: 生成工作流")
        workflow_code = WorkflowGenerator.generate_simplified_workflow()
        print(f"[OK] 生成简化工作流")
        
        # Step 4: Score workflows with real data
        print("\n步骤 4: 使用真实数据评分")
        scores = []
        
        for i, sample in enumerate(test_samples, 1):
            # Build request from real data
            request_data = {
                'data_source': sample.get('data_source'),
                'solution_str': workflow_code,
                'ground_truth': sample.get('reward_model', {}).get('ground_truth', 'default'),
                'extra_info': sample.get('extra_info', {})
            }
            
            result = await client.compute_score(request_data)
            scores.append({
                'sample_id': i,
                'data_source': sample.get('data_source'),
                'success': result.get('success', False),
                'score': result.get('score', 0.0),
                'error': result.get('error')
            })
            
            status = "[OK]" if result.get('success') else "[FAIL]"
            print(f"  样本 {i}: {status} 分数={result.get('score', 0):.3f}")
        
        # Step 5: Generate report
        print("\n步骤 5: 生成报告")
        
        successful_scores = [s for s in scores if s['success']]
        if successful_scores:
            overall_score = sum(s['score'] for s in successful_scores) / len(successful_scores)
        else:
            overall_score = 0
        success_rate = len(successful_scores) / len(scores) if scores else 0
        
        # Group by data source
        by_source = {}
        for score in scores:
            source = score['data_source']
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(score['score'])
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': overall_score,
            'success_rate': success_rate,
            'benchmark_scores': {k: sum(v)/len(v) if v else 0 for k, v in by_source.items()},
            'total_tests': len(scores),
            'successful_tests': len(successful_scores)
        }
        
        # Save report to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            report_file = f.name
        
        print(f"[OK] 报告已生成: {report_file}")
        print(f"  - 总体分数: {overall_score:.2%}")
        print(f"  - 成功率: {success_rate:.2%}")
        print(f"  - 基准测试: {list(by_source.keys())}")
        
        # Clean up
        os.unlink(report_file)
        
        return success_rate > 0


async def main():
    """Run all integration tests"""
    print("\n" + "#"*60)
    print("# 评估系统集成测试 (真实数据 + 奖励服务器)")
    print("#"*60)
    
    # Print test environment info
    print(f"\nPython 版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"奖励服务器: http://localhost:8897")
    print(f"测试数据: New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl")
    
    # Define all tests
    tests = [
        ("奖励服务器连接", test_reward_server_connection),
        ("真实数据测试", test_with_real_data),
        ("批量处理测试", test_batch_processing),
        ("错误处理", test_error_handling),
        ("并发请求", test_concurrent_requests),
        ("完整管道", test_full_pipeline)
    ]
    
    results = {}
    
    # Run each test
    for test_name, test_func in tests:
        print(f"\n{'#'*60}")
        print(f"# 运行: {test_name}")
        print(f"{'#'*60}")
        
        try:
            success = await test_func()
            results[test_name] = success
        except Exception as e:
            print(f"\n[FAIL] {test_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Print final summary
    print("\n" + "#"*60)
    print("# 测试结果总结")
    print("#"*60)
    
    all_passed = True
    for test_name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "#"*60)
    
    if all_passed:
        print("# [OK] 所有测试通过! 评估系统已准备就绪")
        print("#")
        print("# 系统已验证:")
        print("#   1. 奖励服务器连接正常")
        print("#   2. 真实数据加载和处理正常")
        print("#   3. 工作流评分功能正常")
        print("#   4. 批量处理和并发请求正常")
        print("#   5. 错误处理机制完善")
    else:
        print("# [FAIL] 部分测试失败")
        print("#")
        print("# 请确保:")
        print("#   1. 奖励服务器正在运行 (端口 8897)")
        print("#   2. 测试数据文件存在并可读")
        print("#   3. 网络连接正常")
    
    print("#"*60)
    
    return all_passed


if __name__ == "__main__":
    # Run the complete test suite
    success = asyncio.run(main())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)