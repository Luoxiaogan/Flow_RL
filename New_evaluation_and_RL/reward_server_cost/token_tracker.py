"""
Token Tracker Module
使用MetaGPT原生功能追踪token使用情况
"""
import asyncio
import json
import time
from typing import Dict, Optional, List, Any
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import threading

# MetaGPT imports
try:
    from metagpt.context import Context
    from metagpt.utils.cost_manager import CostManager, Costs
except ImportError:
    print("Warning: MetaGPT not installed. Token tracking will be disabled.")
    Context = None
    CostManager = None
    Costs = None


class MetaGPTTokenTracker:
    """
    使用MetaGPT原生功能的Token追踪器
    
    Features:
    - 为每个workflow创建独立的Context和CostManager
    - 线程安全的统计收集
    - 支持批量统计汇总
    - 实时费用计算
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化Token追踪器
        
        Args:
            config: 配置字典，包含pricing等信息
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', True) and Context is not None
        
        # 存储workflow的context和统计信息
        self.workflow_contexts = {}  # workflow_id -> Context
        self.workflow_stats = {}     # workflow_id -> stats
        
        # 线程安全锁
        self.lock = threading.Lock()
        
        # 全局统计
        self.total_stats = {
            'total_workflows': 0,
            'total_prompt_tokens': 0,
            'total_completion_tokens': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'start_time': datetime.now().isoformat(),
            'workflows': [],
            'model_breakdown': defaultdict(lambda: {
                'count': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'total_cost': 0.0
            })
        }
        
        # 缓存设置
        cache_config = self.config.get('cache', {})
        self.cache_enabled = cache_config.get('enabled', True)
        self.cache_ttl = cache_config.get('ttl', 3600)
        self.max_cache_entries = cache_config.get('max_entries', 10000)
        
        if self.enabled:
            print(f"✅ MetaGPT Token追踪器已初始化")
            print(f"   - 缓存: {'启用' if self.cache_enabled else '禁用'}")
            print(f"   - 最大缓存条目: {self.max_cache_entries}")
        else:
            print(f"⚠️ Token追踪器未启用（MetaGPT未安装或配置禁用）")
    
    def create_workflow_context(self, workflow_id: str, model_name: str = None) -> Optional[Context]:
        """
        为workflow创建独立的Context和CostManager
        
        Args:
            workflow_id: workflow唯一标识
            model_name: 使用的模型名称
        
        Returns:
            Context对象，如果追踪器未启用则返回None
        """
        if not self.enabled:
            return None
        
        try:
            # 创建新的Context和CostManager
            context = Context()
            cost_manager = CostManager()
            
            # 设置预算上限（可配置）
            max_budget = self.config.get('max_budget', 100.0)
            cost_manager.max_budget = max_budget
            
            # 关联CostManager到Context
            context.cost_manager = cost_manager
            
            # 线程安全地存储
            with self.lock:
                self.workflow_contexts[workflow_id] = context
                
                # 初始化统计信息
                self.workflow_stats[workflow_id] = {
                    'workflow_id': workflow_id,
                    'model_name': model_name or 'unknown',
                    'start_time': datetime.now().isoformat(),
                    'status': 'running'
                }
            
            return context
            
        except Exception as e:
            print(f"⚠️ 创建workflow context失败: {e}")
            return None
    
    def get_workflow_context(self, workflow_id: str) -> Optional[Context]:
        """
        获取workflow的context
        
        Args:
            workflow_id: workflow唯一标识
        
        Returns:
            Context对象，如果不存在则返回None
        """
        with self.lock:
            return self.workflow_contexts.get(workflow_id)
    
    def get_workflow_stats(self, workflow_id: str) -> Dict:
        """
        获取workflow的token统计信息
        
        Args:
            workflow_id: workflow唯一标识
        
        Returns:
            统计信息字典
        """
        if not self.enabled:
            return {}
        
        with self.lock:
            context = self.workflow_contexts.get(workflow_id)
            if not context or not hasattr(context, 'cost_manager'):
                return self.workflow_stats.get(workflow_id, {})
            
            try:
                # 从CostManager获取费用信息
                costs = context.cost_manager.get_costs()
                
                # 获取模型名称
                model_name = self.workflow_stats.get(workflow_id, {}).get('model_name', 'unknown')
                
                # 计算费用
                cost_details = self._calculate_cost(
                    costs.total_prompt_tokens,
                    costs.total_completion_tokens,
                    model_name
                )
                
                # 构建完整的统计信息
                stats = {
                    'workflow_id': workflow_id,
                    'model_name': model_name,
                    'prompt_tokens': costs.total_prompt_tokens,
                    'completion_tokens': costs.total_completion_tokens,
                    'total_tokens': costs.total_prompt_tokens + costs.total_completion_tokens,
                    'total_cost': cost_details['total_cost'],
                    'cost_breakdown': cost_details,
                    'api_calls': 1 if costs.total_prompt_tokens > 0 else 0,
                    'start_time': self.workflow_stats.get(workflow_id, {}).get('start_time'),
                    'end_time': datetime.now().isoformat()
                }
                
                # 更新缓存
                self.workflow_stats[workflow_id] = stats
                
                return stats
                
            except Exception as e:
                print(f"⚠️ 获取workflow统计失败: {e}")
                return self.workflow_stats.get(workflow_id, {})
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model_name: str) -> Dict:
        """
        计算token费用
        
        Args:
            prompt_tokens: 输入token数
            completion_tokens: 输出token数
            model_name: 模型名称
        
        Returns:
            费用详情字典
        """
        # 获取价格配置
        pricing_config = self.config.get('pricing', {})
        models = pricing_config.get('models', {})
        default_model = pricing_config.get('default_model', 'qwen-turbo')
        
        # 获取模型价格（如果找不到则使用默认）
        model_pricing = models.get(model_name, models.get(default_model, {
            'input_price': 0.5,
            'output_price': 1.5
        }))
        
        # 计算费用（价格是per million tokens）
        input_cost = (prompt_tokens / 1_000_000) * model_pricing.get('input_price', 0.5)
        output_cost = (completion_tokens / 1_000_000) * model_pricing.get('output_price', 1.5)
        total_cost = input_cost + output_cost
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'input_price_per_million': model_pricing.get('input_price', 0.5),
            'output_price_per_million': model_pricing.get('output_price', 1.5),
            'model_used_for_pricing': model_name if model_name in models else default_model
        }
    
    def print_workflow_stats(self, workflow_id: str):
        """
        打印workflow的token统计信息
        
        Args:
            workflow_id: workflow唯一标识
        """
        if not self.config.get('reporting', {}).get('print_stats', True):
            return
        
        stats = self.get_workflow_stats(workflow_id)
        
        if stats and stats.get('total_tokens', 0) > 0:
            print(f"\n{'='*60}")
            print(f"📊 Token统计 - Workflow: {workflow_id}")
            print(f"   模型: {stats.get('model_name', 'unknown')}")
            print(f"   输入Token: {stats.get('prompt_tokens', 0):,}")
            print(f"   输出Token: {stats.get('completion_tokens', 0):,}")
            print(f"   总计Token: {stats.get('total_tokens', 0):,}")
            print(f"   总费用: ${stats.get('total_cost', 0):.6f}")
            
            # 显示费用明细
            cost_breakdown = stats.get('cost_breakdown', {})
            if cost_breakdown:
                print(f"   费用明细:")
                print(f"     - 输入费用: ${cost_breakdown.get('input_cost', 0):.6f}")
                print(f"     - 输出费用: ${cost_breakdown.get('output_cost', 0):.6f}")
            print(f"{'='*60}\n")
    
    def update_total_stats(self, workflow_id: str):
        """
        更新总体统计信息
        
        Args:
            workflow_id: workflow唯一标识
        """
        stats = self.get_workflow_stats(workflow_id)
        if not stats or stats.get('total_tokens', 0) == 0:
            return
        
        with self.lock:
            # 更新总体统计
            self.total_stats['total_workflows'] += 1
            self.total_stats['total_prompt_tokens'] += stats.get('prompt_tokens', 0)
            self.total_stats['total_completion_tokens'] += stats.get('completion_tokens', 0)
            self.total_stats['total_tokens'] += stats.get('total_tokens', 0)
            self.total_stats['total_cost'] += stats.get('total_cost', 0)
            
            # 添加到workflow列表（限制大小）
            if len(self.total_stats['workflows']) < self.max_cache_entries:
                self.total_stats['workflows'].append(stats)
            
            # 更新模型分类统计
            model_name = stats.get('model_name', 'unknown')
            model_stats = self.total_stats['model_breakdown'][model_name]
            model_stats['count'] += 1
            model_stats['prompt_tokens'] += stats.get('prompt_tokens', 0)
            model_stats['completion_tokens'] += stats.get('completion_tokens', 0)
            model_stats['total_tokens'] += stats.get('total_tokens', 0)
            model_stats['total_cost'] += stats.get('total_cost', 0)
    
    def get_total_stats(self) -> Dict:
        """
        获取总体统计信息
        
        Returns:
            总体统计字典
        """
        with self.lock:
            # 计算平均值
            total_workflows = self.total_stats['total_workflows']
            if total_workflows > 0:
                avg_tokens = self.total_stats['total_tokens'] / total_workflows
                avg_cost = self.total_stats['total_cost'] / total_workflows
            else:
                avg_tokens = 0
                avg_cost = 0
            
            return {
                **self.total_stats,
                'average_tokens_per_workflow': avg_tokens,
                'average_cost_per_workflow': avg_cost,
                'current_time': datetime.now().isoformat(),
                'model_breakdown': dict(self.total_stats['model_breakdown'])
            }
    
    def reset_stats(self):
        """重置所有统计信息"""
        with self.lock:
            self.workflow_contexts.clear()
            self.workflow_stats.clear()
            self.total_stats = {
                'total_workflows': 0,
                'total_prompt_tokens': 0,
                'total_completion_tokens': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'start_time': datetime.now().isoformat(),
                'workflows': [],
                'model_breakdown': defaultdict(lambda: {
                    'count': 0,
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': 0,
                    'total_cost': 0.0
                })
            }
            print("✅ Token统计已重置")
    
    def save_stats_report(self, filepath: Path = None):
        """
        保存统计报告到文件
        
        Args:
            filepath: 保存路径，如果为None则使用默认路径
        """
        if not self.config.get('reporting', {}).get('save_to_file', True):
            return
        
        # 确定保存路径
        if filepath is None:
            report_dir = Path(self.config.get('reporting', {}).get('report_dir', 'token_reports'))
            report_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = report_dir / f"token_report_{timestamp}.json"
        
        # 获取统计数据
        stats = self.get_total_stats()
        
        # 保存为JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"📝 Token统计报告已保存: {filepath}")
    
    def cleanup_old_contexts(self, max_age_seconds: int = 3600):
        """
        清理过期的context（释放内存）
        
        Args:
            max_age_seconds: 最大保留时间（秒）
        """
        if not self.cache_enabled:
            return
        
        current_time = time.time()
        expired_workflows = []
        
        with self.lock:
            for workflow_id, stats in self.workflow_stats.items():
                if 'end_time' in stats:
                    # 解析结束时间
                    end_time = datetime.fromisoformat(stats['end_time'])
                    age = current_time - end_time.timestamp()
                    
                    if age > max_age_seconds:
                        expired_workflows.append(workflow_id)
            
            # 清理过期的workflow
            for workflow_id in expired_workflows:
                self.workflow_contexts.pop(workflow_id, None)
                # 保留统计信息，只清理context
        
        if expired_workflows:
            print(f"🧹 清理了 {len(expired_workflows)} 个过期的workflow context")


# 创建全局实例（延迟初始化）
_global_tracker = None


def get_global_tracker(config: Dict = None) -> MetaGPTTokenTracker:
    """
    获取全局Token追踪器实例
    
    Args:
        config: 配置字典
    
    Returns:
        MetaGPTTokenTracker实例
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = MetaGPTTokenTracker(config)
    return _global_tracker