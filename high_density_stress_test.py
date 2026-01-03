import asyncio
import aiohttp
import time
import json
from datetime import datetime
import statistics
import sys
import os

# Set encoding for Windows
if sys.platform == 'win32':
    import locale
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class HighDensityStressTester:
    def __init__(self, url, api_key, model):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.model = model
        self.results = []
        self.start_time = None
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.current_rpm = 0

    async def make_request(self, session, request_id, math_problem):
        """Make a single API request with a math problem"""
        payload = {
            "model": self.model,
            "messages": [
                {"content": "You are a math tutor. Answer concisely in Chinese.", "role": "system"},
                {"content": f"计算: {math_problem}", "role": "user"}
            ],
            "max_tokens": 150,
            "temperature": 0.3  # Lower temperature for more consistent responses
        }

        start_time = time.time()
        try:
            async with session.post(self.url, headers=self.headers, json=payload, timeout=30) as response:
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
                    self.success_count += 1
                    if self.success_count % 10 == 0:
                        current_time = time.time()
                        elapsed = current_time - self.start_time
                        current_rpm = (self.success_count / elapsed) * 60
                        print(f"[{self.success_count:4d} OK] Latency: {latency:.2f}s | RPM: {current_rpm:.0f} | Tokens: {total_tokens}")
                else:
                    self.error_count += 1
                    error_msg = response_data.get('error', {}).get('message', 'Unknown error')
                    print(f"[Request {request_id:4d}] ERROR {response.status}: {error_msg}")

                self.request_count += 1
                return result

        except asyncio.TimeoutError:
            self.error_count += 1
            end_time = time.time()
            print(f"[Request {request_id:4d}] TIMEOUT after 30s")
            return {
                'request_id': request_id,
                'timestamp': start_time,
                'latency': end_time - start_time,
                'status': 0,
                'total_tokens': 0,
                'success': False,
                'error': 'Timeout'
            }
        except Exception as e:
            self.error_count += 1
            end_time = time.time()
            if self.error_count <= 5:  # Only print first 5 errors to avoid spam
                print(f"[Request {request_id:4d}] EXCEPTION: {str(e)[:100]}")
            return {
                'request_id': request_id,
                'timestamp': start_time,
                'latency': end_time - start_time,
                'status': 0,
                'total_tokens': 0,
                'success': False,
                'error': str(e)
            }

    def get_math_problems(self, count):
        """Generate simple math problems for testing"""
        import random
        problems = []
        for i in range(count):
            op_type = i % 5
            a = random.randint(1, 100)
            b = random.randint(1, 100)

            if op_type == 0:
                problems.append(f"{a} + {b}")
            elif op_type == 1:
                problems.append(f"{a} - {b}")
            elif op_type == 2:
                problems.append(f"{a} × {b}")
            elif op_type == 3:
                problems.append(f"{a} ÷ {b if b != 0 else 1}")
            else:
                problems.append(f"{a}² + {b}")

        return problems

    async def run_density_test(self, target_rpm=1000, duration_seconds=30):
        """Run high density stress test with target RPM"""

        # Calculate parameters
        target_rps = target_rpm / 60  # Convert RPM to RPS
        total_requests = int(target_rps * duration_seconds)

        # Adaptive concurrency based on target RPS
        if target_rps <= 20:
            max_concurrent = int(target_rps * 2)
        elif target_rps <= 50:
            max_concurrent = int(target_rps * 1.5)
        else:
            max_concurrent = min(100, int(target_rps))  # Cap at 100 concurrent

        request_interval = 1.0 / target_rps  # Time between request starts

        print(f"\n{'='*70}")
        print(f"高密度压力测试配置")
        print(f"{'='*70}")
        print(f"目标 RPM: {target_rpm} (约 {target_rps:.1f} RPS)")
        print(f"测试时长: {duration_seconds} 秒")
        print(f"总请求数: {total_requests}")
        print(f"最大并发: {max_concurrent}")
        print(f"请求间隔: {request_interval*1000:.1f}ms")
        print(f"API 端点: {self.url}")
        print(f"模型: {self.model}")
        print(f"{'='*70}\n")

        math_problems = self.get_math_problems(total_requests)

        # Create session with higher connection limit
        connector = aiohttp.TCPConnector(
            limit=max_concurrent,
            limit_per_host=max_concurrent,
            force_close=True
        )

        timeout = aiohttp.ClientTimeout(total=30, connect=5)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            self.start_time = time.time()
            test_start = self.start_time

            tasks = []
            request_id = 0

            print("开始发送请求...")
            print(f"{'─'*70}")

            # Send requests at calculated intervals
            while request_id < total_requests:
                current_time = time.time()
                elapsed = current_time - test_start

                # Check if test duration exceeded
                if elapsed >= duration_seconds:
                    print(f"\n达到测试时长 {duration_seconds}秒，停止发送新请求...")
                    break

                # Calculate how many requests should have been sent by now
                expected_requests = int(elapsed * target_rps)

                # Send requests to catch up to expected count
                while request_id < min(expected_requests, total_requests):
                    task = asyncio.create_task(
                        self.make_request(session, request_id + 1, math_problems[request_id])
                    )
                    tasks.append(task)
                    request_id += 1

                    # Process completed tasks when we have many pending
                    if len(tasks) >= max_concurrent:
                        done, tasks = await asyncio.wait(
                            tasks,
                            return_when=asyncio.FIRST_COMPLETED
                        )
                        for task in done:
                            result = await task
                            if result:
                                self.results.append(result)
                        tasks = list(tasks)

                # Small sleep to prevent CPU spinning
                await asyncio.sleep(0.001)

            # Wait for remaining tasks
            print(f"\n等待剩余 {len(tasks)} 个请求完成...")
            if tasks:
                done = await asyncio.gather(*tasks, return_exceptions=True)
                for result in done:
                    if isinstance(result, dict):
                        self.results.append(result)

            test_end = time.time()
            actual_duration = test_end - test_start

        print(f"{'─'*70}")
        print(f"测试完成！实际运行时间: {actual_duration:.2f}秒")

        # Calculate and display statistics
        self.calculate_statistics(actual_duration, target_rpm)

    async def progressive_test(self, rpm_levels=[1000, 2000, 3000], duration_per_level=20):
        """Progressive stress test with increasing RPM levels"""
        print(f"\n{'='*70}")
        print(f"渐进式压力测试")
        print(f"RPM 级别: {rpm_levels}")
        print(f"每级持续: {duration_per_level}秒")
        print(f"{'='*70}")

        all_results = {}

        for rpm in rpm_levels:
            print(f"\n\n[TEST] RPM = {rpm}")
            self.results = []  # Clear previous results
            self.success_count = 0
            self.error_count = 0

            await self.run_density_test(rpm, duration_per_level)

            # Store results for this level
            all_results[f"RPM_{rpm}"] = {
                'results': self.results.copy(),
                'success_count': self.success_count,
                'error_count': self.error_count,
                'actual_rpm': (self.success_count / duration_per_level) * 60
            }

            # Wait between levels
            if rpm != rpm_levels[-1]:
                print(f"\n[COOLDOWN] 冷却期 5秒...")
                await asyncio.sleep(5)

        # Save all results
        self.save_progressive_results(all_results)
        return all_results

    def calculate_statistics(self, test_duration, target_rpm):
        """Calculate and display test statistics"""
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]

        print(f"\n{'='*70}")
        print(f"测试结果统计")
        print(f"{'='*70}")

        print(f"\n== 基础统计 ==")
        print(f"  目标 RPM: {target_rpm}")
        print(f"  总测试时间: {test_duration:.2f} 秒")
        print(f"  总请求数: {len(self.results)}")
        print(f"  成功请求: {len(successful_requests)}")
        print(f"  失败请求: {len(failed_requests)}")

        if len(self.results) > 0:
            success_rate = len(successful_requests)/len(self.results)*100
            print(f"  成功率: {success_rate:.1f}%")

        # Actual throughput
        if test_duration > 0:
            actual_rps = len(self.results) / test_duration
            actual_rpm = actual_rps * 60
            successful_rps = len(successful_requests) / test_duration
            successful_rpm = successful_rps * 60

            print(f"\n== 吞吐量指标 ==")
            print(f"  实际 RPM (总): {actual_rpm:.0f} ({actual_rps:.2f} RPS)")
            print(f"  实际 RPM (成功): {successful_rpm:.0f} ({successful_rps:.2f} RPS)")
            print(f"  目标达成率: {(actual_rpm/target_rpm)*100:.1f}%")

        if successful_requests:
            # Latency statistics
            latencies = [r['latency'] for r in successful_requests]
            print(f"\n== 延迟统计 (秒) ==")
            print(f"  最小: {min(latencies):.3f}")
            print(f"  最大: {max(latencies):.3f}")
            print(f"  平均: {statistics.mean(latencies):.3f}")
            print(f"  中位数: {statistics.median(latencies):.3f}")
            if len(latencies) > 1:
                print(f"  标准差: {statistics.stdev(latencies):.3f}")

            # Token statistics
            total_tokens = sum(r['total_tokens'] for r in successful_requests)
            completion_tokens = sum(r['completion_tokens'] for r in successful_requests)

            if test_duration > 0:
                tps = total_tokens / test_duration
                completion_tps = completion_tokens / test_duration

                print(f"\n== Token 统计 ==")
                print(f"  总 Tokens: {total_tokens:,}")
                print(f"  平均 Tokens/请求: {total_tokens/len(successful_requests):.1f}")
                print(f"  总 TPS: {tps:.1f} tokens/秒")
                print(f"  生成 TPS: {completion_tps:.1f} tokens/秒")

            # Percentile analysis
            sorted_latencies = sorted(latencies)
            def get_percentile(data, percentile):
                index = int(len(data) * percentile / 100)
                return data[min(index, len(data)-1)]

            print(f"\n== 百分位延迟 ==")
            for p in [50, 75, 90, 95, 99]:
                print(f"  P{p}: {get_percentile(sorted_latencies, p):.3f}秒")

        # Error analysis
        if failed_requests:
            print(f"\n== 错误分析 ==")
            error_types = {}
            for r in failed_requests:
                error = r.get('error', 'Unknown')
                if 'Rate limit' in str(error):
                    error = 'Rate Limit'
                elif 'Timeout' in str(error):
                    error = 'Timeout'
                elif 'Connection' in str(error):
                    error = 'Connection Error'
                else:
                    error = error[:30] if len(str(error)) > 30 else error

                error_types[error] = error_types.get(error, 0) + 1

            for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {error}: {count} 次")

    def save_results(self):
        """Save detailed results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"high_density_test_{timestamp}.json"

        summary = {
            'test_time': timestamp,
            'total_requests': len(self.results),
            'successful_requests': sum(1 for r in self.results if r['success']),
            'failed_requests': sum(1 for r in self.results if not r['success']),
            'results': self.results
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n[SAVED] 详细结果已保存到: {filename}")

    def save_progressive_results(self, all_results):
        """Save progressive test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"progressive_test_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        print(f"\n[SAVED] 渐进测试结果已保存到: {filename}")


async def main():
    # New API configuration
    url = "https://api.openai-proxy.org/v1/chat/completions"
    api_key = "sk-vn8SgqS78wiQ6yVSFsKtJ122vMrzywlBxDertnI4d41PnrmN"
    model = "gpt-4o-mini-2024-07-18"

    # Create tester
    tester = HighDensityStressTester(url, api_key, model)

    # Run single RPM test
    # print("\n>>> 启动高密度压力测试...")
    # await tester.run_density_test(target_rpm=1000, duration_seconds=30)

    # Run progressive test
    print("\n>>> 启动渐进式压力测试...")
    await tester.progressive_test(rpm_levels=[1000, 1500, 2000, 2500, 3000], duration_per_level=15)


if __name__ == "__main__":
    asyncio.run(main())