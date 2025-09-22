"""
并发控制器模块 - 为Reward Server提供请求并发限制功能
完全解耦于业务逻辑，通过装饰器模式透明集成
"""

import threading
import time
import functools
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from flask import jsonify

logger = logging.getLogger(__name__)


class ConcurrencyLimiter:
    """
    并发请求限制器
    使用信号量控制同时处理的请求数量，防止资源耗尽
    """
    
    def __init__(self, max_concurrent: int = 5, queue_timeout: int = 600):
        """
        初始化并发限制器
        
        Args:
            max_concurrent: 最大并发请求数
            queue_timeout: 排队超时时间（秒）
        """
        self.max_concurrent = max_concurrent
        self.queue_timeout = queue_timeout
        self.semaphore = threading.Semaphore(max_concurrent)
        
        # 统计信息（线程安全）
        self._lock = threading.Lock()
        self._active_count = 0
        self._queued_count = 0
        self._total_processed = 0
        self._total_succeeded = 0
        self._total_failed = 0
        self._total_timeout = 0
        
        # 活跃任务追踪
        self._active_tasks = {}  # task_id -> task_info
        self._next_task_id = 1
        
        # 性能统计
        self._wait_times = []  # 最近100个请求的等待时间
        self._process_times = []  # 最近100个请求的处理时间
        self._max_history = 100
        
        logger.info(f"并发限制器初始化: max_concurrent={max_concurrent}, timeout={queue_timeout}s")
    
    def acquire(self, identifier: str = "unknown") -> Optional[int]:
        """
        尝试获取执行权限
        
        Args:
            identifier: 请求标识符（如benchmark名称）
            
        Returns:
            task_id if acquired, None if timeout
        """
        start_time = time.time()
        
        # 增加排队计数
        with self._lock:
            self._queued_count += 1
            logger.info(f"请求排队: {identifier}, 当前队列长度: {self._queued_count}")
        
        # 尝试获取信号量（带超时）
        acquired = self.semaphore.acquire(timeout=self.queue_timeout)
        
        wait_time = time.time() - start_time
        
        with self._lock:
            self._queued_count -= 1
            
            if acquired:
                # 成功获取
                self._active_count += 1
                task_id = self._next_task_id
                self._next_task_id += 1
                
                # 记录活跃任务
                self._active_tasks[task_id] = {
                    'id': task_id,
                    'identifier': identifier,
                    'start_time': time.time(),
                    'wait_time': wait_time
                }
                
                # 记录等待时间
                self._wait_times.append(wait_time)
                if len(self._wait_times) > self._max_history:
                    self._wait_times.pop(0)
                
                logger.info(f"请求获准: task_id={task_id}, {identifier}, "
                          f"等待时间: {wait_time:.2f}s, 活跃数: {self._active_count}/{self.max_concurrent}")
                return task_id
            else:
                # 超时
                self._total_timeout += 1
                logger.warning(f"请求超时: {identifier}, 等待时间: {wait_time:.2f}s")
                return None
    
    def release(self, task_id: int, success: bool = True):
        """
        释放执行权限
        
        Args:
            task_id: 任务ID
            success: 是否成功完成
        """
        with self._lock:
            if task_id in self._active_tasks:
                task_info = self._active_tasks[task_id]
                process_time = time.time() - task_info['start_time']
                
                # 更新统计
                self._active_count -= 1
                self._total_processed += 1
                if success:
                    self._total_succeeded += 1
                else:
                    self._total_failed += 1
                
                # 记录处理时间
                self._process_times.append(process_time)
                if len(self._process_times) > self._max_history:
                    self._process_times.pop(0)
                
                # 移除活跃任务
                del self._active_tasks[task_id]
                
                logger.info(f"请求完成: task_id={task_id}, {task_info['identifier']}, "
                          f"处理时间: {process_time:.2f}s, 成功: {success}, "
                          f"剩余活跃: {self._active_count}/{self.max_concurrent}")
        
        # 释放信号量
        self.semaphore.release()
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取当前状态
        
        Returns:
            包含并发状态和统计信息的字典
        """
        with self._lock:
            # 计算平均值
            avg_wait = sum(self._wait_times) / len(self._wait_times) if self._wait_times else 0
            avg_process = sum(self._process_times) / len(self._process_times) if self._process_times else 0
            
            # 构建活跃任务列表
            active_tasks_list = []
            current_time = time.time()
            for task_info in self._active_tasks.values():
                active_tasks_list.append({
                    'id': task_info['id'],
                    'benchmark': task_info['identifier'],
                    'duration': round(current_time - task_info['start_time'], 2),
                    'wait_time': round(task_info['wait_time'], 2)
                })
            
            return {
                'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'concurrency': {
                    'active_requests': self._active_count,
                    'max_concurrent': self.max_concurrent,
                    'available_slots': self.max_concurrent - self._active_count,
                    'queued_requests': self._queued_count
                },
                'statistics': {
                    'total_processed': self._total_processed,
                    'total_succeeded': self._total_succeeded,
                    'total_failed': self._total_failed,
                    'total_timeout': self._total_timeout,
                    'success_rate': round(self._total_succeeded / self._total_processed * 100, 1) 
                                   if self._total_processed > 0 else 0,
                    'average_wait_time': round(avg_wait, 2),
                    'average_process_time': round(avg_process, 2)
                },
                'active_tasks': active_tasks_list
            }
    
    def reset_statistics(self):
        """重置统计信息"""
        with self._lock:
            self._total_processed = 0
            self._total_succeeded = 0
            self._total_failed = 0
            self._total_timeout = 0
            self._wait_times.clear()
            self._process_times.clear()
            logger.info("统计信息已重置")


# 全局并发限制器实例
_global_limiter: Optional[ConcurrencyLimiter] = None


def init_limiter(max_concurrent: int = 5, queue_timeout: int = 600):
    """
    初始化全局并发限制器
    
    Args:
        max_concurrent: 最大并发数
        queue_timeout: 排队超时时间
    """
    global _global_limiter
    _global_limiter = ConcurrencyLimiter(max_concurrent, queue_timeout)
    return _global_limiter


def get_limiter() -> Optional[ConcurrencyLimiter]:
    """获取全局并发限制器实例"""
    return _global_limiter


def with_concurrency_limit(identifier_param: str = 'data_source'):
    """
    装饰器：为Flask路由函数添加并发限制
    
    Args:
        identifier_param: 从请求中提取标识符的参数名
        
    使用示例:
        @app.route('/compute_score', methods=['POST'])
        @with_concurrency_limit('data_source')
        def compute_score_endpoint():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            limiter = get_limiter()
            
            # 首先检查服务器是否正在关闭（优先级最高的检查）
            try:
                from scoreflow_reward_server import shutdown_in_progress
                if shutdown_in_progress:
                    logger.info(f"🚫 服务器正在关闭，立即拒绝新请求")
                    return jsonify({
                        'success': False,
                        'error': 'Server is shutting down for restart'
                    }), 503
            except ImportError:
                pass  # 如果无法导入，继续执行

            # 如果没有限制器，直接执行
            if not limiter:
                return func(*args, **kwargs)

            # 尝试从请求中提取标识符
            identifier = "unknown"
            try:
                from flask import request
                if request.json and identifier_param in request.json:
                    identifier = request.json[identifier_param]
            except:
                pass

            # 尝试获取执行权限
            task_id = limiter.acquire(identifier)
            
            if task_id is None:
                # 超时，返回错误
                logger.error(f"请求因排队超时被拒绝: {identifier}")
                return jsonify({
                    'success': False,
                    'error': 'Request timeout - server too busy',
                    'message': f'请求排队超时（{limiter.queue_timeout}秒），服务器繁忙，请稍后重试'
                }), 503  # Service Unavailable
            
            # 再次检查服务器是否正在关闭（获取权限后的二次确认）
            try:
                from scoreflow_reward_server import shutdown_in_progress
                if shutdown_in_progress:
                    logger.info(f"🚫 服务器正在关闭，拒绝执行任务 {task_id} ({identifier})")
                    limiter.release(task_id, False)
                    return jsonify({
                        'success': False,
                        'error': 'Server is shutting down for restart'
                    }), 503
            except ImportError:
                pass  # 如果无法导入，继续执行

            # 执行实际函数
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                logger.error(f"请求处理失败: {e}")
                raise
            finally:
                # 释放执行权限
                limiter.release(task_id, success)
        
        return wrapper
    return decorator


def with_async_concurrency_limit(identifier_param: str = 'data_source'):
    """
    异步版本的并发限制装饰器（用于异步函数）
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            limiter = get_limiter()
            
            if not limiter:
                return await func(*args, **kwargs)
            
            # 提取标识符
            identifier = "unknown"
            try:
                from flask import request
                if request.json and identifier_param in request.json:
                    identifier = request.json[identifier_param]
            except:
                pass
            
            # 获取执行权限
            task_id = limiter.acquire(identifier)
            
            if task_id is None:
                return jsonify({
                    'success': False,
                    'error': 'Request timeout - server too busy',
                    'message': f'请求排队超时，服务器繁忙'
                }), 503
            
            # 执行异步函数
            success = True
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                limiter.release(task_id, success)
        
        return wrapper
    return decorator