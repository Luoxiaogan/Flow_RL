"""
Model evaluator for generating workflow solutions
"""
import re
import torch
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """
    Handles model loading and solution generation
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize model evaluator
        
        Args:
            model_name: Optional name identifier for this model
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = None
        self.model_path = None
        
    async def load_model(self, model_path: Union[str, Path]):
        """
        Load model from checkpoint or pretrained path
        
        Args:
            model_path: Path to model checkpoint or HuggingFace model ID
        """
        try:
            self.model_path = str(model_path)
            logger.info(f"加载模型 [{self.model_name or 'unnamed'}]: {model_path}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            # Set padding token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Determine device
            if torch.cuda.is_available():
                self.device = 'cuda'
                gpu_name = torch.cuda.get_device_name()
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"使用 GPU: {gpu_name} ({gpu_memory:.1f} GB)")
            else:
                self.device = 'cpu'
                logger.info("使用 CPU")
            
            # Load model with appropriate dtype
            dtype = torch.bfloat16 if self.device == 'cuda' else torch.float32
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=dtype,
                device_map='auto' if self.device == 'cuda' else None,
                trust_remote_code=True
            )
            
            # Set to eval mode
            self.model.eval()
            
            logger.info(f"✓ 模型加载成功: {self.model_name or model_path}")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    async def generate_solutions(self, test_samples: List[Dict], 
                                batch_size: int = 8,
                                max_new_tokens: int = 4096,
                                temperature: float = 0.7,
                                top_p: float = 0.9) -> List[str]:
        """
        Generate workflow solutions for test samples
        
        Args:
            test_samples: List of test samples
            batch_size: Batch size for generation
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            List of generated solution strings
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        solutions = []
        total_batches = (len(test_samples) + batch_size - 1) // batch_size
        
        logger.info(f"[{self.model_name}] 生成 {len(test_samples)} 个解决方案 (批次大小: {batch_size})")
        
        with torch.no_grad():
            for i in tqdm(range(0, len(test_samples), batch_size), 
                         desc=f"生成解决方案 [{self.model_name}]", 
                         total=total_batches):
                batch_samples = test_samples[i:i + batch_size]
                
                # Generate solutions for batch
                batch_solutions = await self._generate_batch(
                    batch_samples,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p
                )
                solutions.extend(batch_solutions)
                
                # Clear GPU cache periodically
                if self.device == 'cuda' and (i // batch_size) % 10 == 0:
                    torch.cuda.empty_cache()
        
        logger.info(f"✓ [{self.model_name}] 生成了 {len(solutions)} 个解决方案")
        return solutions
    
    async def _generate_batch(self, batch_samples: List[Dict],
                             max_new_tokens: int = 4096,
                             temperature: float = 0.7,
                             top_p: float = 0.9) -> List[str]:
        """
        Generate solutions for a batch of samples
        """
        batch_solutions = []
        
        for sample in batch_samples:
            try:
                # Extract prompt from sample
                prompt = sample.get('prompt', [])
                
                # Handle both message format and string format
                if isinstance(prompt, str):
                    # Simple string prompt
                    inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
                else:
                    # Chat format with messages
                    inputs = self.tokenizer.apply_chat_template(
                        prompt,
                        return_tensors="pt",
                        add_generation_prompt=True
                    )
                
                # Move to device
                if isinstance(inputs, dict):
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                else:
                    inputs = inputs.to(self.device)
                
                # Generate
                with torch.cuda.amp.autocast(enabled=(self.device == 'cuda')):
                    if isinstance(inputs, dict):
                        outputs = self.model.generate(
                            **inputs,
                            max_new_tokens=max_new_tokens,
                            temperature=temperature,
                            top_p=top_p,
                            do_sample=True,
                            pad_token_id=self.tokenizer.pad_token_id,
                            eos_token_id=self.tokenizer.eos_token_id
                        )
                    else:
                        outputs = self.model.generate(
                            inputs,
                            max_new_tokens=max_new_tokens,
                            temperature=temperature,
                            top_p=top_p,
                            do_sample=True,
                            pad_token_id=self.tokenizer.pad_token_id,
                            eos_token_id=self.tokenizer.eos_token_id
                        )
                
                # Decode output (only new tokens)
                if isinstance(inputs, dict) and 'input_ids' in inputs:
                    input_length = inputs['input_ids'].shape[-1]
                else:
                    input_length = inputs.shape[-1]
                    
                generated = self.tokenizer.decode(
                    outputs[0][input_length:],
                    skip_special_tokens=True
                )
                
                # Return complete response - reward_server will extract code
                batch_solutions.append(generated)
                
            except Exception as e:
                logger.warning(f"[{self.model_name}] 生成失败: {e}")
                batch_solutions.append("")
        
        return batch_solutions
    
    
    def clear_cache(self):
        """
        Clear model from memory
        """
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        if self.device == 'cuda':
            torch.cuda.empty_cache()
        
        logger.info(f"✓ [{self.model_name}] 模型缓存已清理")