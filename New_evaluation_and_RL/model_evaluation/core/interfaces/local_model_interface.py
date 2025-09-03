"""
Local model interface with LoRA support
"""
import torch
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from transformers import AutoModelForCausalLM, AutoTokenizer

from .model_interface import BaseModelInterface

logger = logging.getLogger(__name__)

class LocalModelInterface(BaseModelInterface):
    """
    Interface for local models (HuggingFace format) with LoRA support
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize local model interface
        
        Args:
            model_config: Configuration with:
                - name: Model name
                - base_model_path: Path to base model
                - lora_path: Optional path to LoRA adapter
                - load_in_8bit: Load model in 8-bit (default: False)
                - load_in_4bit: Load model in 4-bit (default: False)
                - device_map: Device mapping (default: 'auto')
                - torch_dtype: Data type (default: 'auto')
                - generation_params: Generation parameters
        """
        super().__init__(model_config)
        
        self.base_model_path = model_config.get('base_model_path')
        self.lora_path = model_config.get('lora_path')
        self.load_in_8bit = model_config.get('load_in_8bit', False)
        self.load_in_4bit = model_config.get('load_in_4bit', False)
        self.device_map = model_config.get('device_map', 'auto')
        self.torch_dtype_str = model_config.get('torch_dtype', 'auto')
        
        self.model = None
        self.tokenizer = None
        self.device = None
        
    async def initialize(self):
        """
        Load the model and tokenizer
        """
        try:
            logger.info(f"[{self.model_name}] 初始化本地模型")
            logger.info(f"  基础模型: {self.base_model_path}")
            if self.lora_path:
                logger.info(f"  LoRA适配器: {self.lora_path}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model_path,
                trust_remote_code=True
            )
            
            # Set padding token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Determine torch dtype
            if self.torch_dtype_str == 'auto':
                if torch.cuda.is_available():
                    torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
                else:
                    torch_dtype = torch.float32
            else:
                dtype_map = {
                    'float32': torch.float32,
                    'float16': torch.float16,
                    'bfloat16': torch.bfloat16,
                }
                torch_dtype = dtype_map.get(self.torch_dtype_str, torch.float32)
            
            # Load base model
            logger.info(f"[{self.model_name}] 加载基础模型...")
            
            # Model loading arguments
            model_kwargs = {
                'trust_remote_code': True,
                'torch_dtype': torch_dtype,
            }
            
            # Add quantization if specified
            if self.load_in_8bit or self.load_in_4bit:
                try:
                    import bitsandbytes as bnb
                    model_kwargs['load_in_8bit'] = self.load_in_8bit
                    model_kwargs['load_in_4bit'] = self.load_in_4bit
                    model_kwargs['device_map'] = self.device_map
                    logger.info(f"  使用量化: 8-bit={self.load_in_8bit}, 4-bit={self.load_in_4bit}")
                except ImportError:
                    logger.warning("bitsandbytes 未安装，跳过量化")
            else:
                if torch.cuda.is_available():
                    model_kwargs['device_map'] = self.device_map
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_path,
                **model_kwargs
            )
            
            # Load LoRA adapter if specified
            if self.lora_path:
                await self._load_lora_adapter()
            
            # Set to eval mode
            self.model.eval()
            
            # Determine device
            if torch.cuda.is_available():
                self.device = 'cuda'
                gpu_name = torch.cuda.get_device_name()
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"[{self.model_name}] 使用 GPU: {gpu_name} ({gpu_memory:.1f} GB)")
            else:
                self.device = 'cpu'
                logger.info(f"[{self.model_name}] 使用 CPU")
            
            logger.info(f"✓ [{self.model_name}] 模型初始化成功")
            
        except Exception as e:
            logger.error(f"[{self.model_name}] 模型初始化失败: {e}")
            raise
    
    async def _load_lora_adapter(self):
        """
        Load LoRA adapter weights
        """
        try:
            from peft import PeftModel
            
            logger.info(f"[{self.model_name}] 加载 LoRA 适配器: {self.lora_path}")
            
            # Check if the path exists
            lora_path = Path(self.lora_path)
            if not lora_path.exists():
                raise FileNotFoundError(f"LoRA path not found: {self.lora_path}")
            
            # Load LoRA adapter
            self.model = PeftModel.from_pretrained(
                self.model,
                self.lora_path,
                torch_dtype=self.model.dtype,
            )
            
            # Merge LoRA weights if not using quantization
            if not (self.load_in_8bit or self.load_in_4bit):
                logger.info(f"[{self.model_name}] 合并 LoRA 权重到基础模型")
                self.model = self.model.merge_and_unload()
            
            logger.info(f"✓ [{self.model_name}] LoRA 适配器加载成功")
            
        except ImportError:
            logger.error("PEFT 库未安装，无法加载 LoRA 适配器")
            logger.error("请运行: pip install peft")
            raise
        except Exception as e:
            logger.error(f"加载 LoRA 适配器失败: {e}")
            raise
    
    async def generate(self, 
                       prompt: Union[str, List[Dict[str, str]]],
                       max_new_tokens: int = 4096,
                       temperature: float = 0.7,
                       top_p: float = 0.9,
                       top_k: int = 50,
                       do_sample: bool = True,
                       repetition_penalty: float = 1.0,
                       **kwargs) -> str:
        """
        Generate response from the model
        
        Args:
            prompt: Input prompt (string or chat messages)
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling
            top_k: Top-k sampling
            do_sample: Whether to use sampling
            repetition_penalty: Repetition penalty
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        if self.model is None:
            raise RuntimeError(f"[{self.model_name}] Model not initialized")
        
        try:
            # Handle both message format and string format
            if isinstance(prompt, str):
                # Simple string prompt
                inputs = self.tokenizer(
                    prompt, 
                    return_tensors="pt", 
                    truncation=True,
                    max_length=8192
                )
            else:
                # Chat format with messages
                inputs = self.tokenizer.apply_chat_template(
                    prompt,
                    return_tensors="pt",
                    add_generation_prompt=True,
                    truncation=True,
                    max_length=8192
                )
                # Convert to dict format if needed
                if not isinstance(inputs, dict):
                    inputs = {'input_ids': inputs}
            
            # Move to device
            if isinstance(inputs, dict):
                inputs = {k: v.to(self.device) if hasattr(v, 'to') else v 
                         for k, v in inputs.items()}
            else:
                inputs = inputs.to(self.device)
            
            # Generate with model
            with torch.no_grad():
                with torch.cuda.amp.autocast(enabled=(self.device == 'cuda')):
                    if isinstance(inputs, dict):
                        outputs = self.model.generate(
                            **inputs,
                            max_new_tokens=max_new_tokens,
                            temperature=temperature,
                            top_p=top_p,
                            top_k=top_k,
                            do_sample=do_sample,
                            repetition_penalty=repetition_penalty,
                            pad_token_id=self.tokenizer.pad_token_id,
                            eos_token_id=self.tokenizer.eos_token_id,
                            **kwargs
                        )
                    else:
                        outputs = self.model.generate(
                            inputs,
                            max_new_tokens=max_new_tokens,
                            temperature=temperature,
                            top_p=top_p,
                            top_k=top_k,
                            do_sample=do_sample,
                            repetition_penalty=repetition_penalty,
                            pad_token_id=self.tokenizer.pad_token_id,
                            eos_token_id=self.tokenizer.eos_token_id,
                            **kwargs
                        )
            
            # Decode output (only new tokens)
            if isinstance(inputs, dict) and 'input_ids' in inputs:
                input_length = inputs['input_ids'].shape[-1]
            else:
                input_length = inputs.shape[-1] if hasattr(inputs, 'shape') else 1
            
            generated = self.tokenizer.decode(
                outputs[0][input_length:],
                skip_special_tokens=True
            )
            
            return generated
            
        except Exception as e:
            logger.error(f"[{self.model_name}] 生成失败: {e}")
            raise
    
    async def cleanup(self):
        """
        Clean up model resources
        """
        logger.info(f"[{self.model_name}] 清理模型资源")
        
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        if self.device == 'cuda':
            torch.cuda.empty_cache()
        
        logger.info(f"✓ [{self.model_name}] 资源清理完成")