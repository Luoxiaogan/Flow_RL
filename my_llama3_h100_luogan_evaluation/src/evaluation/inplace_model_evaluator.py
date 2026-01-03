"""
In-place model evaluator for generating workflow solutions using current model weights
"""
import re
import torch
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from tqdm import tqdm
from transformers import GenerationConfig

logger = logging.getLogger(__name__)

class InPlaceModelEvaluator:
    """
    Handles solution generation using current training model weights
    """
    
    def __init__(self, eval_config: Dict = None):
        """
        Initialize in-place model evaluator
        
        Args:
            eval_config: Evaluation configuration from evaluation_config.yaml
        """
        # 从配置中提取generation参数
        self.generation_config = eval_config.get('generation', {}) if eval_config else {}
        # 从generation配置中读取max_new_tokens，用于tokenization
        self.max_input_length = self.generation_config.get('max_new_tokens', 2048) + 1024  # 留出生成空间
        
    async def generate_solutions_inplace(self, model, tokenizer, test_samples: List[Dict], 
                                         batch_size: int = 4) -> List[str]:
        """
        Generate workflow solutions using current model weights
        
        Args:
            model: Current training model (already on correct device)
            tokenizer: Model tokenizer
            test_samples: List of test samples
            batch_size: Batch size for generation
            
        Returns:
            List of generated solution strings
        """
        solutions = []
        total_batches = (len(test_samples) + batch_size - 1) // batch_size
        
        logger.info(f"生成 {len(test_samples)} 个解决方案 (批次大小: {batch_size})")
        
        # Determine device from model
        device = next(model.parameters()).device
        logger.info(f"使用设备: {device}")
        
        with torch.no_grad():
            for i in tqdm(range(0, len(test_samples), batch_size), 
                         desc="生成解决方案", total=total_batches):
                batch_samples = test_samples[i:i + batch_size]
                
                # Generate solutions for batch
                batch_solutions = await self._generate_batch_inplace(
                    model, tokenizer, batch_samples, device
                )
                solutions.extend(batch_solutions)
                
                # Clear GPU cache periodically
                if device.type == 'cuda' and (i // batch_size) % 10 == 0:
                    torch.cuda.empty_cache()
        
        logger.info(f"✓ 生成了 {len(solutions)} 个解决方案")
        return solutions
    
    async def _generate_batch_inplace(self, model, tokenizer, batch_samples: List[Dict], 
                                      device) -> List[str]:
        """
        Generate solutions for a batch of samples using current model
        
        Args:
            model: Current model
            tokenizer: Tokenizer
            batch_samples: Batch of test samples
            device: Model device
            
        Returns:
            List of generated solutions
        """
        try:
            # Prepare prompts
            prompts = []
            for sample in batch_samples:
                # Extract prompt from sample
                if 'prompt' in sample:
                    # Check if prompt is already a list (messages format)
                    if isinstance(sample['prompt'], list):
                        # It's a messages array, apply chat template
                        prompt = tokenizer.apply_chat_template(
                            sample['prompt'],
                            tokenize=False,
                            add_generation_prompt=True
                        )
                        print("🐺 🐺 🐺 🐺 🐺\n使用apply_chat_template:\n", prompt)
                    else:
                        # It's a string prompt, use directly
                        prompt = sample['prompt']
                elif 'messages' in sample:
                    # Apply chat template if messages format
                    prompt = tokenizer.apply_chat_template(
                        sample['messages'],
                        tokenize=False,
                        add_generation_prompt=True
                    )
                else:
                    logger.warning(f"Unknown sample format: {sample.keys()}")
                    prompt = str(sample)
                
                prompts.append(prompt)
            
            # Tokenize batch (使用配置的max_length)
            inputs = tokenizer(
                prompts,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=self.max_input_length  # 从配置读取
            ).to(device)
            
            # Generate with model
            # 构建最终的generation配置
            final_config = {}
            
            # Step 1: 尝试使用模型自带的generation_config.json作为基础
            if hasattr(model, 'generation_config'):
                try:
                    # 获取模型的generation config
                    model_config = model.generation_config.to_dict()
                    final_config.update(model_config)
                    logger.info(f"Loaded model's generation_config.json: {list(model_config.keys())}")
                except Exception as e:
                    logger.warning(f"Could not load generation config from model: {e}")
            
            # Step 2: 用evaluation_config.yaml中的参数覆盖（优先级最高）
            # 这些参数来自self.generation_config
            override_params = {
                'max_new_tokens': self.generation_config.get('max_new_tokens', 2048),
                'temperature': self.generation_config.get('temperature', 0.7),
                'top_p': self.generation_config.get('top_p', 0.95),
                'do_sample': self.generation_config.get('do_sample', True),
                'pad_token_id': tokenizer.pad_token_id,
                'eos_token_id': tokenizer.eos_token_id,
            }
            
            # 添加可选参数（如果在配置中存在）
            if 'top_k' in self.generation_config:
                override_params['top_k'] = self.generation_config['top_k']
            if 'repetition_penalty' in self.generation_config:
                override_params['repetition_penalty'] = self.generation_config['repetition_penalty']
            if 'num_beams' in self.generation_config:
                override_params['num_beams'] = self.generation_config['num_beams']
            if 'early_stopping' in self.generation_config:
                override_params['early_stopping'] = self.generation_config['early_stopping']
            
            # 覆盖模型配置
            final_config.update(override_params)
            
            logger.info(f"Final generation config: max_new_tokens={final_config.get('max_new_tokens')}, "
                       f"temperature={final_config.get('temperature')}, "
                       f"top_p={final_config.get('top_p')}, "
                       f"top_k={final_config.get('top_k', 'N/A')}")
            
            # Generate outputs
            outputs = model.generate(
                **inputs,
                **final_config
            )
            
            # Decode outputs
            generated_texts = tokenizer.batch_decode(
                outputs[:, inputs['input_ids'].shape[1]:],  # Only new tokens
                skip_special_tokens=True
            )
            
            # Extract workflow code from generated text
            solutions = []
            for text in generated_texts:
                workflow_code = self._extract_workflow_code(text)
                solutions.append(workflow_code)
            
            return solutions
            
        except Exception as e:
            logger.error(f"批次生成失败: {e}")
            # Return empty solutions for failed batch
            return [""] * len(batch_samples)
    
    def _extract_workflow_code(self, text: str) -> str:
        """
        Extract workflow code from generated text
        
        Args:
            text: Generated text that may contain workflow code
            
        Returns:
            Extracted workflow code or full text if no code blocks found
        """
        # Try to extract code from markdown code blocks
        # code_pattern = r'```(?:python)?\n(.*?)```'
        # matches = re.findall(code_pattern, text, re.DOTALL)
        
        # if matches:
        #     # Return the first code block
        #     return matches[0].strip()
        
        # Try to extract code from <code> tags
        code_tag_pattern = r'<code>(.*?)</code>'
        matches = re.findall(code_tag_pattern, text, re.DOTALL)
        
        if matches:
            print("🐺 🐺 🐺 🐺 🐺\n得到被完全取出来的workflow:\n", matches[0].strip())
            return matches[0].strip()
        
        # If no code blocks found, return the full text
        # (assuming the entire response is the workflow)
        return text.strip()
    
    async def evaluate_checkpoint(self, checkpoint_path: str, test_samples: List[Dict],
                                  batch_size: int = 4) -> List[str]:
        """
        Compatibility method - not used in in-place evaluation
        Raises error if called
        """
        raise NotImplementedError(
            "InPlaceModelEvaluator does not support checkpoint loading. "
            "Use generate_solutions_inplace() with current model weights instead."
        )