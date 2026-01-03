"""
Model evaluator for generating workflow solutions
"""
import re
import torch
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """
    Handles model loading and solution generation
    """
    
    def __init__(self):
        """
        Initialize model evaluator
        """
        self.model = None
        self.tokenizer = None
        self.device = None
        self.model_path = None
        
    async def load_model(self, checkpoint_path: str):
        """
        Load model from checkpoint
        
        Args:
            checkpoint_path: Path to model checkpoint
        """
        try:
            self.model_path = checkpoint_path
            logger.info(f"加载模型: {checkpoint_path}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                checkpoint_path,
                trust_remote_code=True
            )
            
            # Set padding token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Determine device
            if torch.cuda.is_available():
                self.device = 'cuda'
                logger.info(f"使用 GPU: {torch.cuda.get_device_name()}")
            else:
                self.device = 'cpu'
                logger.info("使用 CPU")
            
            # Load model with appropriate dtype
            dtype = torch.bfloat16 if self.device == 'cuda' else torch.float32
            
            self.model = AutoModelForCausalLM.from_pretrained(
                checkpoint_path,
                torch_dtype=dtype,
                device_map='auto' if self.device == 'cuda' else None,
                trust_remote_code=True
            )
            
            # Set to eval mode
            self.model.eval()
            
            logger.info(f"✓ 模型加载成功: {checkpoint_path}")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    async def generate_solutions(self, test_samples: List[Dict], 
                                batch_size: int = 8) -> List[str]:
        """
        Generate workflow solutions for test samples
        
        Args:
            test_samples: List of test samples
            batch_size: Batch size for generation
            
        Returns:
            List of generated solution strings
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        solutions = []
        total_batches = (len(test_samples) + batch_size - 1) // batch_size
        
        logger.info(f"生成 {len(test_samples)} 个解决方案 (批次大小: {batch_size})")
        
        with torch.no_grad():
            for i in tqdm(range(0, len(test_samples), batch_size), 
                         desc="生成解决方案", total=total_batches):
                batch_samples = test_samples[i:i + batch_size]
                
                # Generate solutions for batch
                batch_solutions = await self._generate_batch(batch_samples)
                solutions.extend(batch_solutions)
                
                # Clear GPU cache periodically
                if self.device == 'cuda' and (i // batch_size) % 10 == 0:
                    torch.cuda.empty_cache()
        
        logger.info(f"✓ 生成了 {len(solutions)} 个解决方案")
        return solutions
    
    async def _generate_batch(self, batch_samples: List[Dict]) -> List[str]:
        """
        Generate solutions for a batch of samples
        
        Args:
            batch_samples: Batch of test samples
            
        Returns:
            List of generated solutions
        """
        batch_solutions = []
        
        for sample in batch_samples:
            try:
                # Extract prompt from sample
                prompt = sample.get('prompt', [])
                
                # Apply chat template
                inputs = self.tokenizer.apply_chat_template(
                    prompt,
                    return_tensors="pt",
                    add_generation_prompt=True
                )
                
                # Move to device
                inputs = inputs.to(self.device)
                
                # Generate
                with torch.cuda.amp.autocast(enabled=(self.device == 'cuda')):
                    outputs = self.model.generate(
                        inputs,
                        max_new_tokens=4096,
                        temperature=0.7,
                        top_p=0.9,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id
                    )
                
                # Decode output
                generated = self.tokenizer.decode(
                    outputs[0][inputs.shape[-1]:],  # Only new tokens
                    skip_special_tokens=True
                )
                
                # Extract code from response
                solution_str = self._extract_code(generated)
                batch_solutions.append(solution_str)
                
            except Exception as e:
                logger.warning(f"生成失败: {e}")
                # Return empty solution on failure
                batch_solutions.append("")
        
        return batch_solutions
    
    def _extract_code(self, text: str) -> str:
        """
        Extract workflow code from generated text
        
        Args:
            text: Generated text containing code
            
        Returns:
            Extracted code string
        """
        # Look for code blocks
        code_patterns = [
            r'<code>(.*?)</code>',  # <code>...</code>
            r'```python\n(.*?)```',  # ```python...```
            r'```\n(.*?)```',        # ```...```
        ]
        
        for pattern in code_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                code = match.group(1).strip()
                # Ensure it contains workflow class
                if 'class Workflow' in code:
                    return f"<code>\n{code}\n</code>"
        
        # If no code block found, try to extract workflow class directly
        if 'class Workflow' in text:
            # Find the start of the class
            start = text.find('class Workflow')
            # Try to find a reasonable end
            end = len(text)
            
            # Look for common end markers
            for marker in ['</code>', '```', '\n\n\n', 'Note:', 'Example:']:
                pos = text.find(marker, start)
                if pos > start:
                    end = min(end, pos)
            
            code = text[start:end].strip()
            return f"<code>\n{code}\n</code>"
        
        # Return empty if no workflow found
        logger.warning("未能从生成的文本中提取 workflow 代码")
        return ""
    
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
        
        logger.info("✓ 模型缓存已清理")


# Test function
async def test_model_evaluator():
    """
    Test the model evaluator
    """
    evaluator = ModelEvaluator()
    
    # Test loading (would need actual checkpoint)
    # await evaluator.load_model("/path/to/checkpoint")
    
    # Test code extraction
    test_text = """
    <think>Let me create a workflow...</think>
    <code>
    class Workflow:
        def __init__(self, config, problem):
            self.config = config
            self.problem_text = problem
        
        async def run_workflow(self):
            return "solution"
    </code>
    """
    
    code = evaluator._extract_code(test_text)
    print("Extracted code:", code)
    assert 'class Workflow' in code


if __name__ == "__main__":
    asyncio.run(test_model_evaluator())