"""
Cost Calculator Module
费用计算与惩罚逻辑实现
"""
import math
import yaml
from typing import Dict, Tuple, Optional, Any
from pathlib import Path
from datetime import datetime


class CostCalculator:
    """
    Token费用计算与惩罚逻辑
    
    Features:
    - 多模型价格配置支持
    - 多种惩罚模式（线性/平方/指数）
    - 费用阈值警报
    - 详细的费用报告生成
    """
    
    def __init__(self, config_path: Path = None):
        """
        初始化费用计算器
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 提取关键配置
        self.token_config = self.config.get('token_tracking', {})
        self.pricing_config = self.token_config.get('pricing', {})
        self.penalty_config = self.token_config.get('penalty', {})
        self.alerts_config = self.token_config.get('alerts', {})
        
        # 初始化统计
        self.total_cost_accumulated = 0.0
        self.hourly_costs = {}
        self.daily_costs = {}
        
        print(f"✅ 费用计算器已初始化")
        print(f"   - 惩罚模式: {self.penalty_config.get('mode', 'linear')}")
        print(f"   - 惩罚率: {self.penalty_config.get('rate', 0.1)}")
        print(f"   - 最大惩罚: {self.penalty_config.get('max_penalty', 0.3)}")
    
    def _load_config(self, config_path: Path = None) -> Dict:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
        
        Returns:
            配置字典
        """
        if config_path is None:
            # 使用默认配置文件
            config_path = Path(__file__).parent / "config_cost.yaml"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            print(f"⚠️ 配置文件不存在: {config_path}，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'token_tracking': {
                'enabled': True,
                'pricing': {
                    'models': {
                        'qwen-turbo': {
                            'input_price': 0.5,
                            'output_price': 1.5
                        }
                    },
                    'default_model': 'qwen-turbo'
                },
                'penalty': {
                    'enabled': False,
                    'mode': 'linear',
                    'rate': 0.1,
                    'max_penalty': 0.3,
                    'thresholds': {
                        'warning': 0.5,
                        'critical': 1.0
                    }
                },
                'alerts': {
                    'enabled': True,
                    'thresholds': {
                        'workflow_cost': 2.0,
                        'hourly_cost': 10.0,
                        'daily_cost': 100.0
                    }
                }
            }
        }
    
    def calculate_token_cost(self, 
                            prompt_tokens: int, 
                            completion_tokens: int, 
                            model_name: str = None) -> Dict[str, float]:
        """
        计算token的费用
        
        Args:
            prompt_tokens: 输入token数
            completion_tokens: 输出token数
            model_name: 模型名称
        
        Returns:
            费用详情字典
        """
        # 获取模型价格
        models = self.pricing_config.get('models', {})
        default_model = self.pricing_config.get('default_model', 'qwen-turbo')
        
        # 使用指定模型或默认模型的价格
        if model_name and model_name in models:
            model_pricing = models[model_name]
            used_model = model_name
        else:
            model_pricing = models.get(default_model, {
                'input_price': 0.5,
                'output_price': 1.5
            })
            used_model = default_model
        
        # 计算费用（价格是per million tokens）
        input_price = model_pricing.get('input_price', 0.5)
        output_price = model_pricing.get('output_price', 1.5)
        
        input_cost = (prompt_tokens / 1_000_000) * input_price
        output_cost = (completion_tokens / 1_000_000) * output_price
        total_cost = input_cost + output_cost
        
        # 更新累计费用
        self.total_cost_accumulated += total_cost
        
        # 更新时间段费用
        self._update_time_based_costs(total_cost)
        
        # 检查警报
        self._check_cost_alerts(total_cost, 'workflow')
        
        return {
            'input_tokens': prompt_tokens,
            'output_tokens': completion_tokens,
            'total_tokens': prompt_tokens + completion_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'input_price_per_million': input_price,
            'output_price_per_million': output_price,
            'model_used': used_model,
            'model_description': model_pricing.get('description', '')
        }
    
    def apply_cost_penalty(self, 
                          base_score: float, 
                          token_stats: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        根据token使用量对分数进行惩罚
        
        Args:
            base_score: 原始分数（0-1之间）
            token_stats: token统计信息
        
        Returns:
            (final_score, penalty_details) 元组
        """
        # 检查是否启用惩罚
        if not self.penalty_config.get('enabled', False):
            return base_score, {'penalty_applied': False}
        
        # 获取总费用
        total_cost = token_stats.get('total_cost', 0.0)
        if total_cost == 0:
            return base_score, {'penalty_applied': False, 'reason': 'No cost'}
        
        # 获取惩罚参数
        mode = self.penalty_config.get('mode', 'linear')
        rate = self.penalty_config.get('rate', 0.1)
        max_penalty = self.penalty_config.get('max_penalty', 0.3)
        
        # 根据模式计算惩罚值
        if mode == 'linear':
            # 线性惩罚：penalty = cost * rate
            penalty = total_cost * rate
            
        elif mode == 'square':
            # 平方惩罚：penalty = cost^2 * rate
            penalty = (total_cost ** 2) * rate
            
        elif mode == 'exponential':
            # 指数惩罚：penalty = (e^cost - 1) * rate
            penalty = (math.exp(total_cost) - 1) * rate
            
        elif mode == 'logarithmic':
            # 对数惩罚：penalty = log(1 + cost) * rate
            penalty = math.log(1 + total_cost) * rate
            
        elif mode == 'threshold':
            # 阈值惩罚：超过阈值才惩罚
            thresholds = self.penalty_config.get('thresholds', {})
            warning_threshold = thresholds.get('warning', 0.5)
            critical_threshold = thresholds.get('critical', 1.0)
            
            if total_cost < warning_threshold:
                penalty = 0
            elif total_cost < critical_threshold:
                penalty = (total_cost - warning_threshold) * rate
            else:
                penalty = (total_cost - warning_threshold) * rate * 2  # 双倍惩罚
        else:
            # 未知模式，不惩罚
            penalty = 0.0
        
        # 应用最大惩罚限制
        penalty = min(penalty, max_penalty)
        
        # 计算最终分数（确保不低于0）
        final_score = max(0.0, base_score * (1 - penalty))
        
        # 构建惩罚详情
        penalty_details = {
            'penalty_applied': True,
            'base_score': base_score,
            'final_score': final_score,
            'total_cost': total_cost,
            'penalty_mode': mode,
            'penalty_rate': rate,
            'penalty_value': penalty,
            'penalty_percentage': penalty * 100,
            'score_reduction': base_score - final_score,
            'max_penalty': max_penalty,
            'input_tokens': token_stats.get('input_tokens', 0),
            'output_tokens': token_stats.get('output_tokens', 0),
            'total_tokens': token_stats.get('total_tokens', 0)
        }
        
        # 添加阈值信息（如果使用阈值模式）
        if mode == 'threshold':
            thresholds = self.penalty_config.get('thresholds', {})
            penalty_details['thresholds'] = {
                'warning': thresholds.get('warning', 0.5),
                'critical': thresholds.get('critical', 1.0),
                'exceeded': 'critical' if total_cost >= thresholds.get('critical', 1.0) 
                          else 'warning' if total_cost >= thresholds.get('warning', 0.5)
                          else 'none'
            }
        
        return final_score, penalty_details
    
    def _update_time_based_costs(self, cost: float):
        """
        更新基于时间的费用统计
        
        Args:
            cost: 本次费用
        """
        now = datetime.now()
        hour_key = now.strftime("%Y-%m-%d %H:00")
        day_key = now.strftime("%Y-%m-%d")
        
        # 更新小时费用
        if hour_key not in self.hourly_costs:
            self.hourly_costs[hour_key] = 0.0
        self.hourly_costs[hour_key] += cost
        
        # 更新日费用
        if day_key not in self.daily_costs:
            self.daily_costs[day_key] = 0.0
        self.daily_costs[day_key] += cost
        
        # 检查时间段警报
        self._check_cost_alerts(self.hourly_costs[hour_key], 'hourly')
        self._check_cost_alerts(self.daily_costs[day_key], 'daily')
    
    def _check_cost_alerts(self, cost: float, alert_type: str):
        """
        检查费用警报
        
        Args:
            cost: 费用金额
            alert_type: 警报类型 (workflow/hourly/daily)
        """
        if not self.alerts_config.get('enabled', True):
            return
        
        thresholds = self.alerts_config.get('thresholds', {})
        threshold_key = f"{alert_type}_cost"
        threshold = thresholds.get(threshold_key, float('inf'))
        
        if cost > threshold:
            self._trigger_alert(alert_type, cost, threshold)
    
    def _trigger_alert(self, alert_type: str, cost: float, threshold: float):
        """
        触发费用警报
        
        Args:
            alert_type: 警报类型
            cost: 实际费用
            threshold: 阈值
        """
        methods = self.alerts_config.get('methods', {})
        
        alert_msg = f"⚠️ 费用警报 [{alert_type.upper()}]: ${cost:.4f} 超过阈值 ${threshold:.4f}"
        
        # 控制台输出
        if methods.get('console', True):
            print(f"\n{alert_msg}\n")
        
        # 写入文件
        if methods.get('file', True):
            log_file = Path('cost_alerts.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} - {alert_msg}\n")
        
        # Webhook通知（如果配置）
        if methods.get('webhook', False):
            webhook_url = self.alerts_config.get('webhook_url', '')
            if webhook_url:
                # 这里可以实现webhook通知逻辑
                pass
    
    def generate_cost_report(self) -> Dict[str, Any]:
        """
        生成费用报告
        
        Returns:
            费用报告字典
        """
        return {
            'report_time': datetime.now().isoformat(),
            'total_cost_accumulated': self.total_cost_accumulated,
            'hourly_costs': self.hourly_costs,
            'daily_costs': self.daily_costs,
            'current_hour_cost': self.hourly_costs.get(
                datetime.now().strftime("%Y-%m-%d %H:00"), 0.0
            ),
            'current_day_cost': self.daily_costs.get(
                datetime.now().strftime("%Y-%m-%d"), 0.0
            ),
            'configuration': {
                'penalty_enabled': self.penalty_config.get('enabled', False),
                'penalty_mode': self.penalty_config.get('mode', 'linear'),
                'penalty_rate': self.penalty_config.get('rate', 0.1),
                'alerts_enabled': self.alerts_config.get('enabled', True),
                'alert_thresholds': self.alerts_config.get('thresholds', {})
            }
        }
    
    def format_cost_summary(self, cost_details: Dict[str, Any]) -> str:
        """
        格式化费用摘要为可读字符串
        
        Args:
            cost_details: 费用详情字典
        
        Returns:
            格式化的字符串
        """
        lines = [
            "💰 费用摘要",
            f"  模型: {cost_details.get('model_used', 'unknown')}",
            f"  输入Token: {cost_details.get('input_tokens', 0):,}",
            f"  输出Token: {cost_details.get('output_tokens', 0):,}",
            f"  总Token: {cost_details.get('total_tokens', 0):,}",
            f"  输入费用: ${cost_details.get('input_cost', 0):.6f}",
            f"  输出费用: ${cost_details.get('output_cost', 0):.6f}",
            f"  总费用: ${cost_details.get('total_cost', 0):.6f}"
        ]
        
        if cost_details.get('model_description'):
            lines.append(f"  模型说明: {cost_details['model_description']}")
        
        return "\n".join(lines)
    
    def format_penalty_summary(self, penalty_details: Dict[str, Any]) -> str:
        """
        格式化惩罚摘要为可读字符串
        
        Args:
            penalty_details: 惩罚详情字典
        
        Returns:
            格式化的字符串
        """
        if not penalty_details.get('penalty_applied', False):
            return "📊 未应用费用惩罚"
        
        lines = [
            "📊 费用惩罚详情",
            f"  原始分数: {penalty_details.get('base_score', 0):.3f}",
            f"  最终分数: {penalty_details.get('final_score', 0):.3f}",
            f"  分数减少: {penalty_details.get('score_reduction', 0):.3f}",
            f"  惩罚模式: {penalty_details.get('penalty_mode', 'unknown')}",
            f"  惩罚率: {penalty_details.get('penalty_rate', 0):.2f}",
            f"  惩罚值: {penalty_details.get('penalty_percentage', 0):.1f}%",
            f"  总费用: ${penalty_details.get('total_cost', 0):.6f}"
        ]
        
        # 添加阈值信息（如果有）
        if 'thresholds' in penalty_details:
            thresholds = penalty_details['thresholds']
            lines.append(f"  阈值状态: {thresholds.get('exceeded', 'none')}")
            lines.append(f"  警告阈值: ${thresholds.get('warning', 0):.2f}")
            lines.append(f"  严重阈值: ${thresholds.get('critical', 0):.2f}")
        
        return "\n".join(lines)