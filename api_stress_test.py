import asyncio
import aiohttp
import time
import json
from datetime import datetime
import statistics

class APIStressTester:
    def __init__(self, url, api_key, model):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.model = model
        self.results = []

    async def make_request(self, session, request_id, math_problem):
        """Make a single API request with a math problem"""
        payload = {
            "model": self.model,
            "messages": [
                {"content": "You are a helpful assistant who answers in Chinese.", "role": "system"},
                {"content": f"请解答这道数学题：{math_problem}", "role": "user"}
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }

        start_time = time.time()
        try:
            async with session.post(self.url, headers=self.headers, json=payload) as response:
                response_data = await response.json()
                end_time = time.time()

                # Calculate metrics
                latency = end_time - start_time

                # Extract token counts
                usage = response_data.get('usage', {})
                total_tokens = usage.get('total_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                prompt_tokens = usage.get('prompt_tokens', 0)

                result = {
                    'request_id': request_id,
                    'timestamp': start_time,
                    'latency': latency,
                    'status': response.status,
                    'total_tokens': total_tokens,
                    'completion_tokens': completion_tokens,
                    'prompt_tokens': prompt_tokens,
                    'success': response.status == 200
                }

                if response.status == 200:
                    print(f"[Request {request_id:3d}] OK 延迟: {latency:.2f}s, Tokens: {total_tokens}")
                else:
                    print(f"[Request {request_id:3d}] ERROR 错误: {response.status}")

                return result

        except Exception as e:
            end_time = time.time()
            print(f"[Request {request_id:3d}] EXCEPTION 异常: {str(e)}")
            return {
                'request_id': request_id,
                'timestamp': start_time,
                'latency': end_time - start_time,
                'status': 0,
                'total_tokens': 0,
                'completion_tokens': 0,
                'prompt_tokens': 0,
                'success': False,
                'error': str(e)
            }

    def get_math_problems(self, count):
        """Generate diverse math problems for testing"""
        problems = [
            "计算 15 + 27 等于多少？",
            "解方程：2x + 5 = 15",
            "一个长方形的长是8米，宽是5米，求面积。",
            "计算 123 × 45",
            "小明有20元，买了3支笔，每支笔4元，他还剩多少钱？",
            "求解：如果 3x - 7 = 14，x等于多少？",
            "计算圆的面积，半径为6厘米（使用π=3.14）",
            "把分数 3/4 转换为小数",
            "求100以内所有质数的个数",
            "如果一辆车以60公里/小时的速度行驶，3小时能行驶多远？"
        ]
        # Repeat problems if we need more than 10
        return [problems[i % len(problems)] for i in range(count)]

    async def run_stress_test(self, total_requests=50, max_concurrent=10):
        """Run stress test with controlled concurrency"""
        print(f"\n{'='*60}")
        print(f"开始压力测试")
        print(f"总请求数: {total_requests}")
        print(f"最大并发数: {max_concurrent} (控制RPS < 20)")
        print(f"模型: {self.model}")
        print(f"{'='*60}\n")

        math_problems = self.get_math_problems(total_requests)

        # Create session with connection limit
        connector = aiohttp.TCPConnector(limit=max_concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Create tasks with controlled release
            tasks = []
            test_start = time.time()

            for i in range(total_requests):
                # Control request rate to stay under 20 RPS
                if i > 0 and i % max_concurrent == 0:
                    # Wait to maintain < 20 RPS
                    await asyncio.sleep(0.5)

                task = self.make_request(session, i+1, math_problems[i])
                tasks.append(task)

                # Process in batches
                if len(tasks) >= max_concurrent:
                    batch_results = await asyncio.gather(*tasks)
                    self.results.extend(batch_results)
                    tasks = []

            # Process remaining tasks
            if tasks:
                batch_results = await asyncio.gather(*tasks)
                self.results.extend(batch_results)

            test_end = time.time()
            test_duration = test_end - test_start

        # Calculate and display statistics
        self.calculate_statistics(test_duration)

    def calculate_statistics(self, test_duration):
        """Calculate and display test statistics"""
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]

        print(f"\n{'='*60}")
        print(f"测试结果统计")
        print(f"{'='*60}")

        print(f"\n基础统计:")
        print(f"  总测试时间: {test_duration:.2f} 秒")
        print(f"  总请求数: {len(self.results)}")
        print(f"  成功请求: {len(successful_requests)}")
        print(f"  失败请求: {len(failed_requests)}")
        print(f"  成功率: {len(successful_requests)/len(self.results)*100:.1f}%")

        # RPS (Requests Per Second)
        actual_rps = len(self.results) / test_duration
        print(f"\n吞吐量指标:")
        print(f"  实际 RPS: {actual_rps:.2f} 请求/秒")

        if successful_requests:
            # Latency statistics
            latencies = [r['latency'] for r in successful_requests]
            print(f"\n延迟统计 (秒):")
            print(f"  最小延迟: {min(latencies):.2f}")
            print(f"  最大延迟: {max(latencies):.2f}")
            print(f"  平均延迟: {statistics.mean(latencies):.2f}")
            print(f"  中位数延迟: {statistics.median(latencies):.2f}")
            if len(latencies) > 1:
                print(f"  延迟标准差: {statistics.stdev(latencies):.2f}")

            # Token statistics
            total_tokens_all = sum(r['total_tokens'] for r in successful_requests)
            completion_tokens_all = sum(r['completion_tokens'] for r in successful_requests)
            prompt_tokens_all = sum(r['prompt_tokens'] for r in successful_requests)

            # TPS (Tokens Per Second)
            tps = total_tokens_all / test_duration
            completion_tps = completion_tokens_all / test_duration

            print(f"\nToken 统计:")
            print(f"  总 Tokens 处理: {total_tokens_all}")
            print(f"  提示 Tokens: {prompt_tokens_all}")
            print(f"  完成 Tokens: {completion_tokens_all}")
            print(f"  平均 Tokens/请求: {total_tokens_all/len(successful_requests):.1f}")
            print(f"\nTPS (Tokens Per Second):")
            print(f"  总 TPS: {tps:.2f} tokens/秒")
            print(f"  生成 TPS: {completion_tps:.2f} tokens/秒")

            # Percentile analysis
            sorted_latencies = sorted(latencies)
            p50 = sorted_latencies[int(len(sorted_latencies) * 0.50)]
            p90 = sorted_latencies[int(len(sorted_latencies) * 0.90)]
            p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            p99 = sorted_latencies[min(int(len(sorted_latencies) * 0.99), len(sorted_latencies)-1)]

            print(f"\n百分位延迟:")
            print(f"  P50: {p50:.2f}秒")
            print(f"  P90: {p90:.2f}秒")
            print(f"  P95: {p95:.2f}秒")
            print(f"  P99: {p99:.2f}秒")

        # Save detailed results to file
        self.save_results()

    def save_results(self):
        """Save detailed results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stress_test_results_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n详细结果已保存到: {filename}")


async def main():
    # API configuration
    url = "http://39.96.211.155:8000/proxy/api/openai/v1/chat/completions"
    api_key = "8cf060f9e1f444858609730176542253"
    model = "gpt-4o-mini-0718-global"

    # Create tester
    tester = APIStressTester(url, api_key, model)

    # Run stress test with controlled parameters
    # Using 50 total requests with max 10 concurrent to stay under 20 RPS
    await tester.run_stress_test(total_requests=50, max_concurrent=10)


if __name__ == "__main__":
    asyncio.run(main())