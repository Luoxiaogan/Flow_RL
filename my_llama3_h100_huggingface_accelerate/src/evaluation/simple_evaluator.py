# -*- coding: utf-8 -*-
"""
简化的模型评估器 - 基于Accelerate架构
从复杂的7+1卡系统简化而来，支持标准8卡分布式训练中的原地评估
"""
import re
import torch
# import asyncio  # 不再需要异步支持
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
        print(f"🐺 🐺 🐺 🐺 🐺 : eval_config = \n{eval_config}\n")

        # 从配置中提取generation参数
        self.generation_config = eval_config.get('generation', {}) if eval_config else {}

        print(f"🐺 🐺 🐺 🐺 🐺 : generation_config = \n{self.generation_config}\n")
        
        # 从配置中提取tokenization参数（独立的输入长度控制）
        self.tokenization_config = eval_config.get('tokenization', {}) if eval_config else {}
        # 正确读取输入长度（不要和生成长度混淆）
        self.max_input_length = self.tokenization_config.get('max_input_length', 5476)

        print(f"🐺 🐺 🐺 🐺 🐺 : tokenization_config = \n{self.tokenization_config}\n")
        print(f"🐺 🐺 🐺 🐺 🐺 : max_input_length = \n{self.max_input_length}\n")
        
        # 性能优化配置
        self.optimization_config = eval_config.get('optimization', {}) if eval_config else {}

        print(f"🐺 🐺 🐺 🐺 🐺 : optimization_config = \n{self.optimization_config}\n")

        self.clear_cache = self.optimization_config.get('clear_cache', True)

        print(f"🐺 🐺 🐺 🐺 🐺 : 是否clear_cache = {self.clear_cache}")
        
        logger.info(f"✓ 简化评估器初始化完成")
        logger.info(f"  最大输入长度: {self.max_input_length} tokens")
        logger.info(f"  最大生成长度: {self.generation_config.get('max_new_tokens', 8192)} tokens")
        logger.info(f"  总长度约束: {self.max_input_length + self.generation_config.get('max_new_tokens', 8192)} tokens")
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
        print(f"🐺 🐺 🐺 🐺 🐺 : 测试数据文件路径 = {test_data_path}")

        if not test_data_path or not Path(test_data_path).exists():
            logger.error(f"测试数据文件不存在: {test_data_path}")
            return []
        
        test_samples = []
        
        try:
            with open(test_data_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        sample = json.loads(line.strip())

                        print(f"🐺 🐺 🐺 🐺 🐺 : sample = \n\n{sample}\n\n")

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
    
    def evaluate_during_training(self, model, tokenizer, test_samples: List[Dict],
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

        print(f"🐺 🐺 🐺 🐺 🐺 : 测试样本(可能多个) = \n\n{test_samples}\n\n")

        if not test_samples:
            logger.warning("没有测试样本，跳过评估")
            return []
        
        # 确定推理设备：在主进程GPU上执行推理
        inference_device = accelerator.device if accelerator else next(model.parameters()).device
        print(f"🐺 🐺 🐺 🐺 🐺 : 推理设备 = \n\n{inference_device}\n\n")
        
        logger.info(f"开始原地评估: {len(test_samples)} 个样本")
        logger.info(f"评估批次大小: {batch_size}")
        logger.info(f"推理设备: {inference_device} （DDP主进程推理模式）")
        
        # 将模型设为评估模式
        original_training_mode = model.training
        model.eval()
        
        solutions = []
        
        try:
            # 生成解决方案 - 使用主进程推理策略
            solutions = self._generate_solutions_batch(
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
    
    def _generate_solutions_batch(self, model, tokenizer, test_samples: List[Dict],
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
        print(f"🐺 🐺 🐺 🐺 🐺 使用推理设备: {device} （主进程推理模式）")
        
        with torch.no_grad():
            for i in tqdm(range(0, len(test_samples), batch_size), desc="生成解决方案", total=total_batches):
                batch_samples = test_samples[i:i + batch_size]
                
                # 为批次生成解决方案
                try:
                    batch_solutions = self._generate_single_batch(
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
    
    def _generate_single_batch(self, model, tokenizer, batch_samples: List[Dict],
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
        # print(f"🐺 🐺 🐺 🐺 🐺 batch_samples: \n\n{batch_samples}\n\n")
        for sample in batch_samples:
            # 提取prompt
            # print(f"🐺 🐺 🐺 🐺 🐺 sample: \n\n{sample}\n\n")
            # print(f"🐺 🐺 🐺 🐺 🐺 sample['prompt']: \n\n{sample['prompt']}\n\n")
            if 'prompt' in sample:
                # 检查prompt是否已经是列表（messages格式）
                if isinstance(sample['prompt'], list):
                    # 应用聊天模板
                    prompt = tokenizer.apply_chat_template(
                        sample['prompt'],
                        tokenize=False,
                        add_generation_prompt=True,
                        enable_thinking=True # 显式设置
                    )
                    # print(f"🐺 🐺 🐺 🐺 🐺 应用聊天模板之后的prompt: \n\n{prompt}\n\n")
                else:
                    # 直接使用字符串prompt
                    prompt = sample['prompt']
                    # print("🐺 🐺 🐺 🐺 🐺 使用字符串prompt")
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
        # print(f"🐺 🐺 🐺 🐺 🐺 generation_kwargs = \n\n{generation_kwargs}\n\n")
        
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
            # print(f"🐺 🐺 🐺 🐺 🐺 解码为文本,outputs = \n\n{solutions}\n\n")
            
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
        
        # Step 1: 从evaluation_config.yaml读取参数作为基础
        # 精简版：只添加配置中实际存在的参数，避免添加无效的默认值
        base_params = {}
        
        # 必要参数（带默认值）
        base_params['max_new_tokens'] = 4096
        # base_params['do_sample'] = self.generation_config.get('do_sample', True)
        # base_params['pad_token_id'] = getattr(model.config, 'pad_token_id', None) or getattr(model.config, 'eos_token_id', None)
        
        # 可选参数：只在配置中明确设置时才添加
        # optional_params = ['temperature', 'top_p', 'top_k', 'repetition_penalty', 'num_beams', 'early_stopping']
        # for param in optional_params:
        #     if param in self.generation_config:
        #         base_params[param] = self.generation_config[param]
        
        generation_kwargs.update(base_params)
        print(f"🐺 🐺 🐺 🐺 🐺 从配置文件(self.generation_config)读取的基础参数 = \n\n{generation_kwargs}\n\n")
        
        # Step 2: 如果模型有自带的generation_config.json，让模型配置覆盖基础配置
        # 注意：现在是无条件尝试加载模型配置（不再需要use_model_config标志）
        # if hasattr(model, 'generation_config') and model.generation_config:
        #     try:
        #         # 获取模型的generation config
        #         model_gen_config = model.generation_config.to_dict()
        #         logger.info(f"加载模型generation_config.json: {list(model_gen_config.keys())}")
                
        #         # 模型配置覆盖evaluation配置（模型参数优先级更高）
        #         for key, value in model_gen_config.items():
        #             if key not in ['transformers_version', 'pad_token_id'] and key in ['top_k', 'top_p', 'temperature']:  # 跳过特殊键
        #                 generation_kwargs[key] = value
        #                 logger.info(f"使用模型的{key}: {value}")
                
        #         print(f"🐺 🐺 🐺 🐺 🐺 模型配置覆盖后的参数 = \n\n{generation_kwargs}\n\n")
        #     except Exception as e:
        #         logger.warning(f"无法加载模型generation config: {e}")
        
        # # Step 3: 确保关键参数存在（特别是max_new_tokens）
        # if 'max_new_tokens' not in generation_kwargs or generation_kwargs.get('max_new_tokens') is None:
        #     generation_kwargs['max_new_tokens'] = self.generation_config.get('max_new_tokens', 8192)
        #     logger.info(f"使用evaluation config的max_new_tokens: {generation_kwargs['max_new_tokens']}")
        
        # logger.debug(f"生成配置: {generation_kwargs}")
        print(f"🐺 🐺 🐺 🐺 🐺 生成配置: {generation_kwargs}")
        return generation_kwargs


# 测试函数
def test_simple_evaluator():
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
    test_simple_evaluator()  # 直接调用，不再需要asyncio