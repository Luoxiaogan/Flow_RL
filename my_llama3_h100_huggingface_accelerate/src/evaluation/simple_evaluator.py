# -*- coding: utf-8 -*-
"""
简化的模型评估器 - 基于Accelerate架构
从复杂的7+1卡系统简化而来，支持标准8卡分布式训练中的原地评估
"""
import re
import torch
import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from tqdm import tqdm
from transformers import GenerationConfig

logger = logging.getLogger(__name__)

class SimpleEvaluator:
    """
    简化的原地模型评估器
    支持在Accelerate分布式训练过程中进行评估
    """
    
    def __init__(self, eval_config: Dict = None):
        """
        初始化简化的评估器
        
        Args:
            eval_config: 从evaluation_config.yaml读取的评估配置
        """
        # 从配置中提取generation参数
        self.generation_config = eval_config.get('generation', {}) if eval_config else {}
        
        # 从generation配置中读取max_new_tokens
        self.max_input_length = self.generation_config.get('max_new_tokens', 1024) + 1024  # 留出生成空间
        
        # 性能优化配置
        self.optimization_config = eval_config.get('optimization', {}) if eval_config else {}
        self.clear_cache = self.optimization_config.get('clear_cache', True)
        
        logger.info(f"✓ 简化评估器初始化完成")
        logger.info(f"  最大生成长度: {self.generation_config.get('max_new_tokens', 1024)}")
        logger.info(f"  缓存清理: {self.clear_cache}")
    
    def load_test_data(self, test_data_path: str, max_samples: Optional[int] = None) -> List[Dict]:
        """
        加载测试数据
        
        Args:
            test_data_path: 测试数据文件路径
            max_samples: 最大样本数限制
            
        Returns:
            测试样本列表
        """
        if not test_data_path or not Path(test_data_path).exists():
            logger.error(f"测试数据文件不存在: {test_data_path}")
            return []
        
        test_samples = []
        
        try:
            with open(test_data_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        sample = json.loads(line.strip())
                        test_samples.append(sample)
                        
                        # 限制样本数
                        if max_samples and len(test_samples) >= max_samples:
                            break
            
            logger.info(f"✓ 成功加载 {len(test_samples)} 个测试样本")
            if max_samples and len(test_samples) >= max_samples:
                logger.info(f"  （限制为最多 {max_samples} 个样本）")
                
        except Exception as e:
            logger.error(f"❌ 加载测试数据失败: {e}")
            return []
        
        return test_samples
    
    async def evaluate_during_training(self, model, tokenizer, test_samples: List[Dict],
                                     batch_size: int = 1, accelerator=None) -> List[str]:
        """
        在训练过程中进行原地评估
        DDP优化版本：在主进程GPU（通常GPU 0）上执行推理，其他GPU保持idle
        
        Args:
            model: 当前训练模型（Accelerate管理）
            tokenizer: 模型tokenizer
            test_samples: 测试样本列表
            batch_size: 评估批次大小
            accelerator: Accelerate加速器对象（用于设备管理）
            
        Returns:
            生成的解决方案列表
        """
        if not test_samples:
            logger.warning("没有测试样本，跳过评估")
            return []
        
        # 确定推理设备：在主进程GPU上执行推理
        inference_device = accelerator.device if accelerator else next(model.parameters()).device
        
        logger.info(f"开始原地评估: {len(test_samples)} 个样本")
        logger.info(f"评估批次大小: {batch_size}")
        logger.info(f"推理设备: {inference_device} （DDP主进程推理模式）")
        
        # 将模型设为评估模式
        original_training_mode = model.training
        model.eval()
        
        solutions = []
        
        try:
            # 生成解决方案 - 使用主进程推理策略
            solutions = await self._generate_solutions_batch(
                model, tokenizer, test_samples, batch_size, inference_device
            )
            
            logger.info(f"✓ 评估完成，生成了 {len(solutions)} 个解决方案")
            logger.info(f"  其他GPU (1-7) 在推理期间保持idle状态")
            
        except Exception as e:
            logger.error(f"❌ 评估过程中发生错误: {e}")
            solutions = [""] * len(test_samples)  # 返回空解决方案
            
        finally:
            # 恢复原始训练模式
            model.train(original_training_mode)
            
            # 清理GPU缓存
            if self.clear_cache and torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.debug("GPU缓存已清理")
        
        return solutions
    
    async def _generate_solutions_batch(self, model, tokenizer, test_samples: List[Dict],
                                       batch_size: int, inference_device=None) -> List[str]:
        """
        批量生成解决方案 - DDP主进程推理优化
        
        Args:
            model: 训练模型
            tokenizer: 分词器
            test_samples: 测试样本
            batch_size: 批次大小
            inference_device: 推理设备（通常是主进程GPU）
            
        Returns:
            生成的解决方案列表
        """
        solutions = []
        total_batches = (len(test_samples) + batch_size - 1) // batch_size
        
        # 使用指定的推理设备或从模型自动检测
        device = inference_device if inference_device else next(model.parameters()).device
        logger.debug(f"使用推理设备: {device} （主进程推理模式）")
        
        with torch.no_grad():
            for i in tqdm(range(0, len(test_samples), batch_size), 
                         desc="生成解决方案", total=total_batches):
                batch_samples = test_samples[i:i + batch_size]
                
                # 为批次生成解决方案
                try:
                    batch_solutions = await self._generate_single_batch(
                        model, tokenizer, batch_samples, device
                    )
                    solutions.extend(batch_solutions)
                    
                except Exception as e:
                    logger.error(f"批次 {i//batch_size} 生成失败: {e}")
                    # 添加空解决方案
                    solutions.extend([""] * len(batch_samples))
                
                # 定期清理缓存
                if self.clear_cache and i % (batch_size * 5) == 0:
                    torch.cuda.empty_cache()
        
        return solutions
    
    async def _generate_single_batch(self, model, tokenizer, batch_samples: List[Dict],
                                    device) -> List[str]:
        """
        为单个批次生成解决方案
        
        Args:
            model: 模型
            tokenizer: 分词器
            batch_samples: 批次样本
            device: 设备
            
        Returns:
            解决方案列表
        """
        # 准备提示词
        prompts = []
        for sample in batch_samples:
            # 提取prompt
            if 'prompt' in sample:
                # 检查prompt是否已经是列表（messages格式）
                if isinstance(sample['prompt'], list):
                    # 应用聊天模板
                    prompt = tokenizer.apply_chat_template(
                        sample['prompt'],
                        tokenize=False,
                        add_generation_prompt=True
                    )
                else:
                    # 直接使用字符串prompt
                    prompt = sample['prompt']
                prompts.append(prompt)
            else:
                logger.warning("样本缺少prompt字段，使用空字符串")
                prompts.append("")
        
        # 批量编码
        try:
            inputs = tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.max_input_length
            ).to(device)
            
        except Exception as e:
            logger.error(f"编码输入失败: {e}")
            return [""] * len(batch_samples)
        
        # 准备生成配置
        generation_kwargs = self._prepare_generation_config(model)
        
        # 生成
        try:
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    **generation_kwargs
                )
            
            # 解码生成的部分（去除输入部分）
            input_length = inputs['input_ids'].shape[1]
            generated_tokens = outputs[:, input_length:]
            
            # 解码为文本
            solutions = tokenizer.batch_decode(
                generated_tokens, 
                skip_special_tokens=True
            )
            
            return solutions
            
        except Exception as e:
            logger.error(f"生成失败: {e}")
            return [""] * len(batch_samples)
    
    def _prepare_generation_config(self, model) -> Dict:
        """
        准备生成配置
        
        Args:
            model: 模型
            
        Returns:
            生成配置字典
        """
        generation_kwargs = {}
        
        # 从配置文件读取参数
        generation_kwargs.update({
            'max_new_tokens': self.generation_config.get('max_new_tokens', 1024),
            'temperature': self.generation_config.get('temperature', 0.6),
            'top_p': self.generation_config.get('top_p', 0.95),
            'top_k': self.generation_config.get('top_k', 20),
            'do_sample': self.generation_config.get('do_sample', True),
            'repetition_penalty': self.generation_config.get('repetition_penalty', 1.0),
            'early_stopping': self.generation_config.get('early_stopping', False),
            'num_beams': self.generation_config.get('num_beams', 1),
            'pad_token_id': getattr(model.config, 'pad_token_id', None) or getattr(model.config, 'eos_token_id', None)
        })
        
        # 如果配置要求使用模型自带配置作为基础
        if self.generation_config.get('use_model_config', False):
            if hasattr(model, 'generation_config') and model.generation_config:
                # 合并模型配置和自定义配置
                model_gen_config = model.generation_config.to_dict()
                # 自定义配置优先级更高
                for key, value in generation_kwargs.items():
                    model_gen_config[key] = value
                generation_kwargs = model_gen_config
        
        logger.debug(f"生成配置: {generation_kwargs}")
        return generation_kwargs


# 测试函数
async def test_simple_evaluator():
    """
    测试简化评估器
    """
    # 模拟配置
    eval_config = {
        'generation': {
            'max_new_tokens': 512,
            'temperature': 0.7,
            'top_p': 0.9,
            'do_sample': True
        },
        'optimization': {
            'clear_cache': True
        }
    }
    
    evaluator = SimpleEvaluator(eval_config)
    
    # 模拟测试样本
    test_samples = [
        {
            'prompt': [
                {'role': 'system', 'content': '你是一个有用的助手。'},
                {'role': 'user', 'content': '编写一个Python函数来计算斐波那契数。'}
            ]
        }
    ]
    
    print("✓ 简化评估器测试完成")


if __name__ == "__main__":
    asyncio.run(test_simple_evaluator())