#!/usr/bin/env python3
"""
测试脚本：验证SimpleTeeOutput内存泄漏修复
模拟高并发请求环境，监控内存使用和对象数量
"""

import sys
import os
import time
import gc
import threading
import tempfile
import psutil
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scoreflow_reward_utils import IndividualTestCaseLogger, SimpleTeeOutput

def get_memory_usage():
    """获取当前进程内存使用（MB）"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def count_objects():
    """统计Python对象数量"""
    return {
        'total': len(gc.get_objects()),
        'SimpleTeeOutput': sum(1 for obj in gc.get_objects() if isinstance(obj, SimpleTeeOutput)),
        'IndividualTestCaseLogger': sum(1 for obj in gc.get_objects() if hasattr(obj, '__class__') and obj.__class__.__name__ == 'IndividualTestCaseLogger')
    }

def simulate_request(request_id, duration=0.5):
    """模拟单个请求处理"""
    start_time = time.time()
    
    # 创建临时日志文件
    log_dir = Path("/tmp/test_memory_leak")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"test_{request_id}.log"
    
    try:
        # 使用IndividualTestCaseLogger（模拟真实场景）
        with IndividualTestCaseLogger(log_file, request_id):
            # 模拟大量print操作
            for i in range(100):
                print(f"Request {request_id}: Processing step {i}")
                if i % 20 == 0:
                    time.sleep(0.01)  # 模拟处理延迟
            
            # 模拟处理时间
            time.sleep(duration)
            
        # 删除临时文件
        if log_file.exists():
            log_file.unlink()
            
        return {'id': request_id, 'success': True, 'duration': time.time() - start_time}
        
    except Exception as e:
        return {
            'id': request_id, 
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc(),
            'duration': time.time() - start_time
        }

def stress_test(num_requests=600, max_workers=10, test_duration=1200):
    """
    压力测试主函数
    
    Args:
        num_requests: 总请求数（默认600，模拟20分钟的请求量）
        max_workers: 并发数（默认10，与生产环境一致）
        test_duration: 最大测试时长（秒，默认20分钟）
    """
    print("="*80)
    print("SimpleTeeOutput内存泄漏修复验证测试")
    print("="*80)
    print(f"测试参数：")
    print(f"  - 总请求数: {num_requests}")
    print(f"  - 并发度: {max_workers}")
    print(f"  - 最大测试时长: {test_duration}秒")
    print("="*80)
    
    # 初始状态
    initial_memory = get_memory_usage()
    initial_objects = count_objects()
    print(f"\n初始状态：")
    print(f"  - 内存使用: {initial_memory:.2f} MB")
    print(f"  - Python对象总数: {initial_objects['total']}")
    print(f"  - SimpleTeeOutput对象: {initial_objects['SimpleTeeOutput']}")
    print()
    
    # 统计数据
    results = []
    start_time = time.time()
    last_gc_time = start_time
    memory_samples = []
    object_samples = []
    
    # 使用线程池执行请求
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        
        # 提交所有请求
        for i in range(num_requests):
            future = executor.submit(simulate_request, i, 0.1)
            futures.append(future)
            
            # 控制提交速度（模拟真实请求流）
            if i % 10 == 0:
                time.sleep(0.5)
        
        # 等待并收集结果
        completed_count = 0
        failed_count = 0
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            if result['success']:
                completed_count += 1
            else:
                failed_count += 1
                print(f"❌ 请求 {result['id']} 失败: {result.get('error', 'Unknown')}")
            
            # 定期报告状态
            if completed_count % 50 == 0:
                current_memory = get_memory_usage()
                current_objects = count_objects()
                elapsed = time.time() - start_time
                
                memory_samples.append(current_memory)
                object_samples.append(current_objects['SimpleTeeOutput'])
                
                print(f"\n[{elapsed:.1f}s] 进度: {completed_count + failed_count}/{num_requests}")
                print(f"  内存: {current_memory:.2f} MB (Δ{current_memory - initial_memory:+.2f} MB)")
                print(f"  SimpleTeeOutput对象: {current_objects['SimpleTeeOutput']} 个")
                print(f"  Python对象总数: {current_objects['total']} 个")
                
                # 每5分钟强制GC
                if time.time() - last_gc_time > 300:
                    print("  触发手动GC...")
                    gc.collect()
                    last_gc_time = time.time()
            
            # 检查超时
            if time.time() - start_time > test_duration:
                print(f"\n⚠️ 达到最大测试时长 {test_duration}秒，停止测试")
                break
    
    # 最终统计
    print("\n" + "="*80)
    print("测试完成 - 最终统计")
    print("="*80)
    
    final_memory = get_memory_usage()
    final_objects = count_objects()
    total_duration = time.time() - start_time
    
    print(f"测试时长: {total_duration:.1f}秒")
    print(f"完成请求: {completed_count}/{num_requests}")
    print(f"失败请求: {failed_count}")
    print()
    print(f"内存变化:")
    print(f"  初始: {initial_memory:.2f} MB")
    print(f"  最终: {final_memory:.2f} MB")
    print(f"  增长: {final_memory - initial_memory:.2f} MB")
    print(f"  平均每请求: {(final_memory - initial_memory) / completed_count * 1000:.3f} KB")
    print()
    print(f"对象数量变化:")
    print(f"  SimpleTeeOutput: {initial_objects['SimpleTeeOutput']} -> {final_objects['SimpleTeeOutput']}")
    print(f"  泄漏对象数: {final_objects['SimpleTeeOutput'] - initial_objects['SimpleTeeOutput']}")
    print(f"  Python对象总数: {initial_objects['total']} -> {final_objects['total']}")
    
    # 判断是否存在泄漏
    print("\n" + "="*80)
    leak_detected = False
    
    # 检查SimpleTeeOutput对象泄漏
    leaked_objects = final_objects['SimpleTeeOutput'] - initial_objects['SimpleTeeOutput']
    if leaked_objects > 10:  # 允许小量残留
        print("❌ 检测到SimpleTeeOutput对象泄漏！")
        print(f"   泄漏数量: {leaked_objects} 个")
        leak_detected = True
    else:
        print("✅ SimpleTeeOutput对象数量正常")
    
    # 检查内存泄漏
    memory_growth = final_memory - initial_memory
    memory_growth_per_request = memory_growth / completed_count if completed_count > 0 else 0
    if memory_growth_per_request > 0.1:  # 每个请求超过100KB认为有泄漏
        print("❌ 检测到内存泄漏！")
        print(f"   每请求内存增长: {memory_growth_per_request:.3f} MB")
        leak_detected = True
    else:
        print("✅ 内存使用正常")
    
    if not leak_detected:
        print("\n🎉 恭喜！修复验证成功，未检测到资源泄漏！")
    else:
        print("\n⚠️ 警告：仍存在资源泄漏，需要进一步调查")
    
    print("="*80)
    
    # 清理临时目录
    temp_dir = Path("/tmp/test_memory_leak")
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return not leak_detected

if __name__ == "__main__":
    # 运行测试
    print(f"开始测试时间: {datetime.now().isoformat()}")
    
    # 首先运行快速测试（5分钟）
    print("\n### 快速测试（5分钟）###")
    quick_success = stress_test(num_requests=150, max_workers=10, test_duration=300)
    
    if quick_success:
        print("\n### 完整测试（20分钟）###")
        full_success = stress_test(num_requests=600, max_workers=10, test_duration=1200)
        
        if full_success:
            print("\n✅ 所有测试通过！ScoreFlow Reward Server崩溃问题已修复。")
        else:
            print("\n❌ 完整测试失败，仍存在资源泄漏。")
    else:
        print("\n❌ 快速测试失败，请检查修复代码。")
    
    print(f"\n测试结束时间: {datetime.now().isoformat()}")