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
import deepspeed

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_project_root():
    """从root.yaml获取项目根路径"""
    try:
        # 获取当前文件的目录，向上两级找到项目目录
        current_dir = Path(__file__).parent.parent.parent
        root_config_path = current_dir / "configs" / "root.yaml"
        
        with open(root_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config.get('root', '/nas/ganluo/Flow_RL')
    except Exception as e:
        logger.warning(f"无法读取root.yaml: {e}")
        return '/nas/ganluo/Flow_RL'  # 默认使用服务器路径

# 动态获取配置文件路径
PROJECT_ROOT = get_project_root()
CONFIG_PATH = os.path.join(PROJECT_ROOT, "New_evaluation_and_RL/config.yaml")

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
                - eval_config_path: evaluation_config.yaml路径（可选）
        """
        self.test_data_path = config.get('test_data_path')
        self.reward_server_url = load_reward_server_config()  # 从config.yaml读取
        self.eval_interval = config.get('eval_interval', 50)  # 默认50步
        self.eval_batch_size = config.get('eval_batch_size', 4)
        self.output_dir = Path(config.get('output_dir', 'evaluation_reports'))
        self.max_samples = config.get('max_samples', None)
        
        # 读取evaluation_config.yaml（如果提供了路径）
        self.eval_config = {}
        eval_config_path = config.get('eval_config_path')
        if eval_config_path and Path(eval_config_path).exists():
            try:
                with open(eval_config_path, 'r', encoding='utf-8') as f:
                    self.eval_config = yaml.safe_load(f)
                logger.info(f"Loaded evaluation config from: {eval_config_path}")
            except Exception as e:
                logger.warning(f"Failed to load evaluation config: {e}")
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 跟踪评估结果
        self.evaluation_results = {}
        
        # 初始化组件（延迟加载）
        self._server_checker = None
        self._model_evaluator = None
        self._score_collector = None
        self._report_generator = None
        
        # 存储trainer引用以获取tokenizer
        self._trainer = None
        
        # 7卡训练+1卡推理：专用推理模型（GPU 7）
        self.inference_device = torch.device("cuda:7")
        self.inference_model = None
        self.inference_tokenizer = None
        self._weights_sync_time = 0.0  # 权重同步耗时统计
        
        logger.info(f"原地评估回调已初始化")
        logger.info(f"  Reward服务器URL: {self.reward_server_url}")
        logger.info(f"  评估间隔: 每{self.eval_interval}步")
        logger.info(f"  测试数据: {self.test_data_path}")
        logger.info(f"  推理设备: {self.inference_device} (7卡训练+1卡推理方案)")
    
    def set_trainer(self, trainer):
        """
        存储trainer引用以访问tokenizer
        
        Args:
            trainer: Hugging Face Trainer对象
        """
        self._trainer = trainer
        logger.info("✓ Trainer引用已设置，tokenizer访问已就绪")
    
    def on_train_begin(self, args: TrainingArguments, state: TrainerState, 
                       control: TrainerControl, model=None, **kwargs) -> TrainerControl:
        """
        训练开始时预加载推理模型到GPU 7
        """
        # 只在主进程加载推理模型
        if not state.is_world_process_zero:
            return control
            
        try:
            logger.info("🚀 开始在GPU 7上预加载推理模型...")
            
            # 检查GPU 7是否可用
            if not torch.cuda.is_available() or torch.cuda.device_count() < 8:
                logger.error("GPU 7不可用，回退到原有推理方案")
                return control
            
            # 获取模型路径
            if hasattr(model, 'config') and hasattr(model.config, '_name_or_path'):
                model_path = model.config._name_or_path
            else:
                # 从训练参数获取
                model_path = getattr(args, 'model_name_or_path', None)
                if not model_path:
                    logger.error("无法确定模型路径，跳过推理模型预加载")
                    return control
            
            logger.info(f"加载推理模型: {model_path}")
            
            # 加载推理模型到GPU 7
            from transformers import AutoModelForCausalLM
            
            # self.inference_model = AutoModelForCausalLM.from_pretrained(
            #     model_path,
            #     torch_dtype=torch.bfloat16,
            #     device_map={"": self.inference_device}, # 这行导致错误
            #     trust_remote_code=True,
            #     attn_implementation="flash_attention_2"
            # )

            with torch.cuda.device(self.inference_device):
                self.inference_model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.bfloat16,
                    trust_remote_code=True,
                    attn_implementation="flash_attention_2"
                    # 移除device_map参数
                )
                # 确保模型在正确设备上  
                self.inference_model = self.inference_model.to(self.inference_device)

            # 设置为评估模式
            self.inference_model.eval()
            
            # 获取tokenizer
            if self._trainer and hasattr(self._trainer, 'tokenizer'):
                self.inference_tokenizer = self._trainer.tokenizer
                logger.info("✓ Tokenizer已从trainer获取")
            else:
                logger.warning("Trainer tokenizer不可用，将在评估时动态获取")
            
            # 显示GPU内存使用情况
            if torch.cuda.is_available():
                memory_allocated = torch.cuda.memory_allocated(self.inference_device) / 1024**3
                memory_reserved = torch.cuda.memory_reserved(self.inference_device) / 1024**3
                logger.info(f"GPU 7内存使用: 已分配 {memory_allocated:.2f}GB, 已预留 {memory_reserved:.2f}GB")
            
            logger.info("✅ 推理模型预加载完成")
            
        except Exception as e:
            logger.error(f"推理模型预加载失败: {e}")
            logger.warning("将回退到原有推理方案")
            # 清理可能的部分加载资源
            self.inference_model = None
            self.inference_tokenizer = None
        
        return control
    
    def _sync_training_weights(self, training_model):
        """
        串行同步DeepSpeed ZeRO-3训练权重到推理模型
        完全阻塞训练过程，确保GPU 0-6在此期间完全暂停
        
        Args:
            training_model: 当前的训练模型（分布式）
            
        Returns:
            bool: 同步是否成功
        """
        if not self.inference_model:
            logger.warning("推理模型未初始化，跳过权重同步")
            return False
            
        import time
        sync_start = time.time()
        
        try:
            logger.info("🔄 开始串行同步训练权重到推理模型...")
            logger.info("⏸️  训练计算暂停，GPU 0-6保持状态不变，等待权重聚合")
            
            # 检查是否使用DeepSpeed
            if not hasattr(training_model, 'module') and not hasattr(training_model, '_deepspeed_engine'):
                logger.warning("未检测到DeepSpeed，尝试直接拷贝权重")
                # 直接拷贝（非DeepSpeed情况）
                state_dict = {}
                for name, param in training_model.named_parameters():
                    if param.is_floating_point():
                        # 直接拷贝到GPU 7，避免在训练GPU上操作
                        state_dict[name] = param.data.clone().to(self.inference_device)
                
                self.inference_model.load_state_dict(state_dict, strict=False)
                logger.info("✓ 非DeepSpeed权重同步完成")
                return True
            
            # DeepSpeed ZeRO-3权重聚合和同步（完全串行）
            logger.info("🔄 DeepSpeed ZeRO-3串行权重聚合...")
            logger.info(f"   所有rank ({torch.distributed.get_world_size()}) 将参与聚合")
            
            # 获取实际的模型（可能被包装在DeepSpeed引擎中）
            if hasattr(training_model, 'module'):
                actual_model = training_model.module
            else:
                actual_model = training_model
            
            # 强制同步所有进程，确保串行执行
            if torch.distributed.is_initialized():
                torch.distributed.barrier()
                logger.info("✓ 所有进程已同步，开始权重聚合")
            
            # 使用GatheredParameters聚合分片参数（阻塞式）
            with deepspeed.zero.GatheredParameters(actual_model.parameters(), modifier_rank=0):
                if torch.distributed.get_rank() == 0:  # 只在rank 0执行权重拷贝
                    logger.info("🎯 Rank 0: 开始从GPU 0拷贝完整权重到GPU 7...")
                    
                    # 构建state_dict，直接从GPU 0拷贝到GPU 7
                    gathered_state_dict = {}
                    param_count = 0
                    for name, param in actual_model.named_parameters():
                        if param.is_floating_point() and param.requires_grad:
                            # 关键：从GPU 0直接拷贝到GPU 7
                            # 只同步需要训练的参数，避免frozen参数
                            with torch.no_grad():
                                gathered_state_dict[name] = param.data.clone().to(
                                    device=self.inference_device,  # GPU 7
                                    dtype=param.dtype,
                                    non_blocking=False
                                )
                            param_count += 1
                    
                    logger.info(f"✓ 已拷贝 {param_count} 个训练参数从GPU 0到GPU 7")
                    
                    # 同步到推理模型
                    missing_keys, unexpected_keys = self.inference_model.load_state_dict(
                        gathered_state_dict, strict=False
                    )
                    
                    if missing_keys:
                        logger.warning(f"推理模型缺少键: {len(missing_keys)} 个")
                    if unexpected_keys:
                        logger.warning(f"推理模型多余键: {len(unexpected_keys)} 个")
                    
                    # 清理临时字典，释放GPU 7内存
                    del gathered_state_dict
                    torch.cuda.empty_cache()
                    
                    logger.info("✅ Rank 0: 权重已成功同步到推理模型（GPU 7）")
                else:
                    logger.info(f"⚙️  Rank {torch.distributed.get_rank()}: 等待权重同步完成")
            
            # 再次同步所有进程，确保权重同步完全完成
            if torch.distributed.is_initialized():
                torch.distributed.barrier()
                logger.info("🎯 权重同步完成，所有进程已同步")
            
            # 记录耗时
            sync_time = time.time() - sync_start
            self._weights_sync_time = sync_time
            logger.info(f"✅ ZeRO-3分片权重同步完成，总耗时: {sync_time:.2f}秒")
            logger.info("▶️  训练计算即将恢复，GPU 0-6状态完整保留")
            
            return True
            
        except Exception as e:
            sync_time = time.time() - sync_start
            logger.error(f"❌ ZeRO-3权重同步失败 (耗时: {sync_time:.2f}秒): {e}")
            logger.error("▶️  训练将恢复，推理回退到原方案")
            import traceback
            traceback.print_exc()
            return False
    
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
        
        # 使用稳健的tokenizer获取方式
        if tokenizer is None:
            if self._trainer and hasattr(self._trainer, 'tokenizer'):
                tokenizer = self._trainer.tokenizer
                logger.info(f"✓ 从存储的trainer获取tokenizer: {type(tokenizer)}")
            else:
                logger.error("无法获取tokenizer - trainer引用未设置或trainer无tokenizer")
                return control
        else:
            logger.info(f"✓ 直接获取到tokenizer: {type(tokenizer)}")

        
        # 同步运行评估（原地评估的推荐方式）
        self._run_evaluation_sync(model, tokenizer, state.global_step, args.output_dir)
        
        return control
    
    def on_train_end(self, args: TrainingArguments, state: TrainerState, 
                     control: TrainerControl, **kwargs) -> TrainerControl:
        """
        在训练结束时调用，清理资源
        """
        # 生成最终总结报告
        if self.evaluation_results:
            self._generate_summary_report()
        
        # 清理推理模型资源
        if state.is_world_process_zero and self.inference_model is not None:
            logger.info("🧹 清理推理模型资源...")
            try:
                # 清理GPU内存
                del self.inference_model
                self.inference_model = None
                self.inference_tokenizer = None
                
                # 清理GPU缓存
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    logger.info("✓ GPU缓存已清理")
                
                logger.info("✅ 推理模型资源清理完成")
            except Exception as e:
                logger.warning(f"资源清理时出现警告: {e}")
        
        logger.info("🎯 训练和评估已完成")
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
                self._model_evaluator = InPlaceModelEvaluator(eval_config=self.eval_config)
            
            if self._score_collector is None:
                from .score_collector import ScoreCollector
                self._score_collector = ScoreCollector(self.reward_server_url)
            
            if self._report_generator is None:
                from .report_generator import ReportGenerator
                self._report_generator = ReportGenerator(self.output_dir)
            
            # 步骤1：检查reward服务器状态
            logger.info("检查Reward服务器状态...")
            is_healthy = await self._server_checker.check_server()
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
            
            # 步骤3：权重同步和推理（7卡训练+1卡推理方案）
            logger.info(f"开始7卡训练+1卡推理评估（步数 {global_step}）")
            
            # 决定使用哪种推理方式
            use_dedicated_inference = (
                self.inference_model is not None and 
                self.inference_tokenizer is not None
            )
            
            if use_dedicated_inference:
                logger.info("✅ 使用专用推理模型（GPU 7）进行串行评估")
                logger.info("⏸️  训练计算暂停，GPU 0-6保持内存状态，开始权重同步和推理")
                
                # 串行同步训练权重到推理模型
                sync_success = self._sync_training_weights(model)
                
                if sync_success:
                    # 使用专用推理模型（完全在GPU 7上）
                    eval_model = self.inference_model
                    eval_tokenizer = self.inference_tokenizer
                    logger.info(f"✅ 权重同步成功，推理将在 {self.inference_device} 上执行")
                    logger.info("📍 GPU 0-6保持训练状态，只有GPU 7执行推理计算")
                else:
                    logger.warning("⚠️  权重同步失败，回退到原有方案")
                    use_dedicated_inference = False
            
            if not use_dedicated_inference:
                logger.info("⚠️ 回退到原有推理方案（训练模型）")
                # 回退到原有方案
                model.eval()
                eval_model = model
                eval_tokenizer = tokenizer
            
            # 生成解决方案（串行执行）
            if use_dedicated_inference:
                logger.info("🎯 开始在GPU 7上串行生成解决方案...")
                logger.info("📍 GPU 0-6维持训练状态，无计算活动，等待推理完成")
            
            solutions = await self._model_evaluator.generate_solutions_inplace(
                eval_model, eval_tokenizer, test_samples, 
                batch_size=self.eval_batch_size
            )
            
            # 如果使用训练模型进行推理，恢复训练模式
            if not use_dedicated_inference:
                logger.info("▶️  恢复训练模式")
                model.train()
            else:
                logger.info("✅ GPU 7推理完成，准备恢复训练")
            
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
            
            # 性能监控报告
            logger.info("📊 串行评估性能统计:")
            if use_dedicated_inference:
                logger.info(f"  ✅ 推理方案: 7卡训练 + 1卡串行推理 (GPU 7)")
                logger.info(f"  ⏱️  权重同步耗时: {self._weights_sync_time:.2f}秒")
                logger.info(f"  🔄 评估期间GPU 0-6保持训练状态，无计算操作")
                logger.info("  ▶️  训练计算即将恢复，所有状态完整保留")
            else:
                logger.info(f"  ⚠️  推理方案: 回退到原有方案 (训练模型)")
            
            # GPU内存使用统计
            if torch.cuda.is_available() and use_dedicated_inference:
                memory_allocated = torch.cuda.memory_allocated(self.inference_device) / 1024**3
                memory_reserved = torch.cuda.memory_reserved(self.inference_device) / 1024**3
                logger.info(f"  💾 GPU 7内存: 已分配 {memory_allocated:.2f}GB, 已预留 {memory_reserved:.2f}GB")
            
            # 确保所有进程同步，然后恢复训练
            if torch.distributed.is_initialized():
                torch.distributed.barrier()
                logger.info("✅ 所有进程已同步，训练即将恢复")
            
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