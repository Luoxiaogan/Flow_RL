"""
原地评估回调，用于训练过程中自动评估模型
使用当前分布式模型权重进行评估，无需保存检查点
"""
import os
import json
import yaml
import logging
import asyncio
import torch
from pathlib import Path
from typing import Dict, Any, Optional
from transformers import TrainerCallback, TrainerControl, TrainerState, TrainingArguments

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 硬编码配置文件路径
CONFIG_PATH = "/Users/luogan/Code/workflow_generation/Flow_RL/New_evaluation_and_RL/config.yaml"

def load_reward_server_config():
    """从config.yaml读取reward server配置"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        port = config['services']['scoreflow_reward']['port']  # 8897
        host = config['services']['scoreflow_reward'].get('host', 'localhost')
        return f"http://{host}:{port}"
    except Exception as e:
        logger.warning(f"无法读取配置文件 {CONFIG_PATH}: {e}")
        logger.warning("使用默认配置: http://localhost:8897")
        return "http://localhost:8897"

class InPlaceEvaluationCallback(TrainerCallback):
    """
    训练过程中使用当前权重自动评估模型的回调
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化原地评估回调
        
        Args:
            config: 配置字典，包含：
                - test_data_path: 测试数据JSONL文件路径
                - eval_interval: 每N步评估一次（默认：50）
                - eval_batch_size: 评估批次大小（默认：4）
                - output_dir: 保存评估报告的目录
                - max_samples: 评估的最大样本数（默认：None表示全部）
        """
        self.test_data_path = config.get('test_data_path')
        self.reward_server_url = load_reward_server_config()  # 从config.yaml读取
        self.eval_interval = config.get('eval_interval', 50)  # 默认50步
        self.eval_batch_size = config.get('eval_batch_size', 4)
        self.output_dir = Path(config.get('output_dir', 'evaluation_reports'))
        self.max_samples = config.get('max_samples', None)
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 跟踪评估结果
        self.evaluation_results = {}
        
        # 初始化组件（延迟加载）
        self._server_checker = None
        self._model_evaluator = None
        self._score_collector = None
        self._report_generator = None
        
        logger.info(f"原地评估回调已初始化")
        logger.info(f"  Reward服务器URL: {self.reward_server_url}")
        logger.info(f"  评估间隔: 每{self.eval_interval}步")
        logger.info(f"  测试数据: {self.test_data_path}")
    
    def on_step_end(self, args: TrainingArguments, state: TrainerState, 
                    control: TrainerControl, model=None, tokenizer=None, **kwargs) -> TrainerControl:
        """
        在每个训练步结束时调用
        """
        # 检查是否应该在此步评估
        if state.global_step % self.eval_interval != 0:
            return control
        
        # 只在主进程（rank 0）上评估
        if not state.is_world_process_zero:
            return control
        
        logger.info(f"在步数 {state.global_step} 开始原地评估")
        
        # 同步运行评估（原地评估的推荐方式）
        self._run_evaluation_sync(model, tokenizer, state.global_step, args.output_dir)
        
        return control
    
    def on_train_end(self, args: TrainingArguments, state: TrainerState, 
                     control: TrainerControl, **kwargs) -> TrainerControl:
        """
        在训练结束时调用
        """
        # 生成最终总结报告
        if self.evaluation_results:
            self._generate_summary_report()
        
        logger.info("训练和评估已完成")
        return control
    
    def _run_evaluation_sync(self, model, tokenizer, global_step: int, output_dir: str):
        """
        使用当前模型权重同步运行评估
        """
        try:
            # 为此线程创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 运行异步评估
            result = loop.run_until_complete(
                self._run_evaluation_async(model, tokenizer, global_step, output_dir)
            )
            
            # 存储结果
            self.evaluation_results[global_step] = result
            
            # 清理
            loop.close()
            
        except Exception as e:
            logger.error(f"步数 {global_step} 的评估失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def _run_evaluation_async(self, model, tokenizer, global_step: int, output_dir: str):
        """
        使用当前模型权重异步运行评估
        """
        try:
            # 延迟加载组件
            if self._server_checker is None:
                from .reward_server_checker import RewardServerChecker
                self._server_checker = RewardServerChecker(self.reward_server_url)
            
            if self._model_evaluator is None:
                from .inplace_model_evaluator import InPlaceModelEvaluator
                self._model_evaluator = InPlaceModelEvaluator()
            
            if self._score_collector is None:
                from .score_collector import ScoreCollector
                self._score_collector = ScoreCollector(self.reward_server_url)
            
            if self._report_generator is None:
                from .report_generator import ReportGenerator
                self._report_generator = ReportGenerator(self.output_dir)
            
            # 步骤1：检查reward服务器状态
            logger.info("检查Reward服务器状态...")
            is_healthy = await self._server_checker.check_health()
            if not is_healthy:
                logger.error(f"Reward服务器不可用: {self.reward_server_url}")
                return None
            
            # 步骤2：加载测试数据
            logger.info(f"加载测试数据: {self.test_data_path}")
            with open(self.test_data_path, 'r', encoding='utf-8') as f:
                test_samples = [json.loads(line) for line in f]
            
            # 限制样本数量（如果指定）
            if self.max_samples and len(test_samples) > self.max_samples:
                test_samples = test_samples[:self.max_samples]
                logger.info(f"限制评估样本数量: {self.max_samples}")
            
            # 步骤3：使用当前模型权重生成解决方案
            logger.info(f"使用当前模型权重生成解决方案（步数 {global_step}）")
            
            # 切换到评估模式
            model.eval()
            
            solutions = await self._model_evaluator.generate_solutions_inplace(
                model, tokenizer, test_samples, 
                batch_size=self.eval_batch_size
            )
            
            # 切换回训练模式
            model.train()
            
            # 步骤4：从reward服务器收集分数
            logger.info("计算评估分数...")
            scores = await self._score_collector.batch_evaluate(
                test_samples, 
                solutions,
                batch_size=self.eval_batch_size
            )
            
            # 步骤5：生成报告
            logger.info("生成评估报告...")
            checkpoint_info = {
                'step': global_step,
                'type': 'in_place',  # 标记为原地评估
                'output_dir': output_dir
            }
            
            report = await self._report_generator.generate_report(
                scores, 
                checkpoint_info,
                test_samples
            )
            
            logger.info(f"评估完成 - 步数 {global_step}")
            logger.info(f"总体得分: {report.get('overall_score', 0):.2%}")
            
            # 打印基准测试分数
            for benchmark, stats in report.get('benchmark_scores', {}).items():
                logger.info(f"  {benchmark}: {stats['mean_score']:.2%} (n={stats['num_samples']})")
            
            # 评估后清理GPU缓存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            return report
            
        except Exception as e:
            logger.error(f"评估过程出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_summary_report(self):
        """
        生成所有评估的总结报告
        """
        logger.info("生成评估总结报告...")
        
        summary = {
            'total_evaluations': len(self.evaluation_results),
            'evaluation_type': 'in_place',
            'evaluations': []
        }
        
        for step, result in sorted(self.evaluation_results.items()):
            if result:
                summary['evaluations'].append({
                    'step': step,
                    'overall_score': result.get('overall_score', 0),
                    'benchmark_scores': result.get('benchmark_scores', {})
                })
        
        # 保存总结
        summary_path = self.output_dir / 'evaluation_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"评估总结已保存: {summary_path}")