# Auto-Evaluation Implementation Plan for Model Training

## 1. Executive Summary

This plan outlines the implementation of automatic model evaluation during the training process in `my_llama3_h100_with_eval`. The system will automatically evaluate checkpoint performance using the ScoreFlow reward server after each checkpoint save.

## 2. System Architecture

### 2.1 High-Level Design

```
Training Pipeline
    |
    +-- Trainer (HuggingFace)
    |     |
    |     +-- EvaluationCallback
    |           |
    |           +-- Checkpoint Detection
    |           +-- Model Evaluation Pipeline
    |           +-- Report Generation
    |
    +-- Reward Server (Port 8899)
          |
          +-- ScoreFlow Evaluation
          +-- Benchmark Scoring
```

### 2.2 Component Overview

**Core Components:**
1. **EvaluationCallback** - Monitors checkpoint saves and triggers evaluation
2. **RewardServerManager** - Manages reward server lifecycle
3. **ModelEvaluator** - Handles model loading and inference
4. **ScoreCollector** - Interfaces with reward server API
5. **ReportGenerator** - Creates evaluation reports

## 3. Implementation Details

### 3.1 Evaluation Callback Module

**File:** `src/evaluation/evaluation_callback.py`

```python
from transformers import TrainerCallback
import asyncio
import json
from pathlib import Path

class EvaluationCallback(TrainerCallback):
    """
    Callback to evaluate model checkpoints during training
    """
    def __init__(self, eval_config):
        self.test_data_path = eval_config.get('test_data_path')
        self.reward_server_url = eval_config.get('reward_server_url', 'http://localhost:8899')
        self.eval_interval = eval_config.get('eval_interval', 1)
        self.async_eval = eval_config.get('async_eval', True)
        self.eval_batch_size = eval_config.get('batch_size', 8)
        
    def on_save(self, args, state, control, **kwargs):
        """Triggered when checkpoint is saved"""
        if state.global_step % self.eval_interval == 0:
            checkpoint_dir = f"{args.output_dir}/checkpoint-{state.global_step}"
            self._run_evaluation(checkpoint_dir, state.global_step)
```

### 3.2 Reward Server Manager

**File:** `src/evaluation/reward_server_manager.py`

```python
import socket
import subprocess
import time
import requests

class RewardServerManager:
    """
    Manages the reward server lifecycle
    """
    def __init__(self, server_url='http://localhost:8899'):
        self.server_url = server_url
        self.port = 8899
        
    def is_server_running(self):
        """Check if reward server is accessible"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def start_server(self):
        """Start the reward server if not running"""
        if not self.is_server_running():
            cmd = ["python", "New_evaluation_and_RL/reward_server/scoreflow_reward_server.py"]
            subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(10)  # Wait for server to start
```

### 3.3 Model Evaluator

**File:** `src/evaluation/model_evaluator.py`

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json

class ModelEvaluator:
    """
    Handles model loading and solution generation
    """
    def __init__(self, checkpoint_path, device='cuda'):
        self.checkpoint_path = checkpoint_path
        self.device = device
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """Load model from checkpoint"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.checkpoint_path,
            torch_dtype=torch.bfloat16,
            device_map='auto'
        )
        
    def generate_solution(self, prompt):
        """Generate workflow solution from prompt"""
        inputs = self.tokenizer.apply_chat_template(
            prompt, 
            return_tensors="pt",
            add_generation_prompt=True
        ).to(self.device)
        
        outputs = self.model.generate(
            inputs,
            max_new_tokens=4096,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        
        solution = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self._extract_code(solution)
```

### 3.4 Score Collector

**File:** `src/evaluation/score_collector.py`

```python
import aiohttp
import asyncio
import json
from typing import List, Dict

class ScoreCollector:
    """
    Collects evaluation scores from reward server
    """
    def __init__(self, server_url='http://localhost:8899'):
        self.server_url = server_url
        
    async def compute_score(self, request_data):
        """Send evaluation request to reward server"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.server_url}/compute_score",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                result = await response.json()
                return result
                
    async def batch_evaluate(self, test_samples, solutions):
        """Evaluate multiple samples in parallel"""
        tasks = []
        for sample, solution in zip(test_samples, solutions):
            request_data = {
                'data_source': sample['data_source'],
                'solution_str': solution,
                'ground_truth': sample['reward_model']['ground_truth'],
                'extra_info': sample['extra_info']
            }
            tasks.append(self.compute_score(request_data))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
```

### 3.5 Report Generator

**File:** `src/evaluation/report_generator.py`

```python
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

class ReportGenerator:
    """
    Generates evaluation reports
    """
    def __init__(self, output_dir='evaluation_reports'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_report(self, scores, checkpoint_info):
        """Generate evaluation report"""
        # Calculate statistics by benchmark
        benchmark_stats = self._calculate_benchmark_stats(scores)
        
        # Create report
        report = {
            'checkpoint': checkpoint_info,
            'timestamp': datetime.now().isoformat(),
            'overall_score': self._calculate_overall_score(scores),
            'benchmark_scores': benchmark_stats,
            'total_samples': len(scores),
            'successful_samples': sum(1 for s in scores if s.get('success', False))
        }
        
        # Save as JSON
        json_path = self.output_dir / f"eval_checkpoint_{checkpoint_info['step']}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Generate markdown report
        self._generate_markdown_report(report)
        
        return report
        
    def _calculate_benchmark_stats(self, scores):
        """Calculate statistics for each benchmark"""
        df = pd.DataFrame(scores)
        stats = {}
        
        for benchmark in df['data_source'].unique():
            benchmark_data = df[df['data_source'] == benchmark]
            stats[benchmark] = {
                'mean_score': benchmark_data['score'].mean(),
                'max_score': benchmark_data['score'].max(),
                'min_score': benchmark_data['score'].min(),
                'std_score': benchmark_data['score'].std(),
                'num_samples': len(benchmark_data)
            }
            
        return stats
```

## 4. Integration with Training Script

### 4.1 Modified Training Script

**File:** `src/train.py` (additions)

```python
# Add evaluation arguments
@dataclass
class EvaluationArguments:
    enable_auto_eval: bool = field(
        default=False,
        metadata={"help": "Enable automatic evaluation during training"}
    )
    eval_test_data_path: str = field(
        default="New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl",
        metadata={"help": "Path to test data for evaluation"}
    )
    reward_server_url: str = field(
        default="http://localhost:8899",
        metadata={"help": "URL of the reward server"}
    )
    eval_batch_size: int = field(
        default=8,
        metadata={"help": "Batch size for evaluation"}
    )
    async_evaluation: bool = field(
        default=True,
        metadata={"help": "Run evaluation asynchronously"}
    )

# In the train() function
def train():
    # Parse arguments
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainingArguments, EvaluationArguments))
    model_args, data_args, training_args, eval_args = parser.parse_args_into_dataclasses()
    
    # ... existing code ...
    
    # Add evaluation callback if enabled
    callbacks = []
    if eval_args.enable_auto_eval:
        from evaluation.evaluation_callback import EvaluationCallback
        eval_callback = EvaluationCallback({
            'test_data_path': eval_args.eval_test_data_path,
            'reward_server_url': eval_args.reward_server_url,
            'batch_size': eval_args.eval_batch_size,
            'async_eval': eval_args.async_evaluation
        })
        callbacks.append(eval_callback)
    
    # Initialize trainer with callbacks
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=data_collator,
        callbacks=callbacks
    )
```

### 4.2 Launch Script

**File:** `run_finetune_with_eval.sh`

```bash
#!/bin/bash

# Training with automatic evaluation
python -m accelerate.commands.launch \
    --config_file accelerate_config.yaml \
    src/train.py \
    --model_name_or_path /nas/models/Meta-Llama-3-8B-Instruct \
    --dataset_path /path/to/training_data.jsonl \
    --output_dir ./output \
    --enable_auto_eval True \
    --eval_test_data_path New_evaluation_and_RL/generate_parquet_and_jsonl/test_scoreflow_data/train.jsonl \
    --reward_server_url http://localhost:8899 \
    --eval_batch_size 8 \
    --async_evaluation True \
    # ... other training arguments
```

## 5. Data Flow

### 5.1 Evaluation Pipeline

```
1. Checkpoint Saved
        |
2. EvaluationCallback.on_save() triggered
        |
3. Check/Start Reward Server
        |
4. Load Checkpoint Model
        |
5. Load Test Data (JSONL)
        |
6. For each test sample:
   - Extract prompt
   - Generate solution
   - Prepare request data
        |
7. Batch send to Reward Server
        |
8. Collect scores
        |
9. Generate report
        |
10. Save results
```

### 5.2 Request/Response Format

**Request to Reward Server:**
```json
{
    "data_source": "workflow_gsm8k",
    "solution_str": "<generated_workflow_code>",
    "ground_truth": "default",
    "extra_info": {
        "test_cases": [1, 2, 3],
        "data_path": "path/to/data.jsonl",
        "raw_data": 10
    }
}
```

**Response from Reward Server:**
```json
{
    "success": true,
    "score": 0.85,
    "message": "Score computed successfully"
}
```

## 6. Report Format

### 6.1 JSON Report Structure

```json
{
    "checkpoint": {
        "step": 1000,
        "path": "./output/checkpoint-1000"
    },
    "timestamp": "2024-01-15T10:30:00",
    "overall_score": 0.75,
    "benchmark_scores": {
        "workflow_gsm8k": {
            "mean_score": 0.82,
            "max_score": 1.0,
            "min_score": 0.4,
            "std_score": 0.15,
            "num_samples": 100
        },
        "workflow_drop": {
            "mean_score": 0.68,
            "max_score": 0.95,
            "min_score": 0.3,
            "std_score": 0.18,
            "num_samples": 80
        }
    },
    "total_samples": 180,
    "successful_samples": 175
}
```

### 6.2 Markdown Report Template

```markdown
# Evaluation Report - Checkpoint 1000

## Summary
- **Date**: 2024-01-15 10:30:00
- **Checkpoint**: checkpoint-1000
- **Overall Score**: 75.0%
- **Success Rate**: 97.2% (175/180)

## Benchmark Performance

### workflow_gsm8k
- Mean Score: 82.0%
- Best Score: 100.0%
- Worst Score: 40.0%
- Samples: 100

### workflow_drop
- Mean Score: 68.0%
- Best Score: 95.0%
- Worst Score: 30.0%
- Samples: 80

## Details
[Additional analysis and insights]
```

## 7. Error Handling

### 7.1 Common Error Scenarios

1. **Reward Server Unavailable**
   - Attempt to start server
   - Retry with exponential backoff
   - Skip evaluation if persistent failure

2. **Model Generation Failure**
   - Log error with sample details
   - Continue with next sample
   - Mark as failed in report

3. **GPU OOM**
   - Reduce batch size dynamically
   - Clear cache between batches
   - Use gradient checkpointing

4. **Timeout Issues**
   - Set reasonable timeouts (5 min per sample)
   - Implement retry mechanism
   - Log timeout occurrences

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# test_evaluation.py
def test_reward_server_manager():
    manager = RewardServerManager()
    assert manager.is_server_running() in [True, False]

def test_model_evaluator():
    evaluator = ModelEvaluator("./test_checkpoint")
    solution = evaluator.generate_solution(test_prompt)
    assert isinstance(solution, str)

def test_report_generator():
    generator = ReportGenerator()
    report = generator.generate_report(test_scores, test_info)
    assert 'overall_score' in report
```

### 8.2 Integration Tests

1. Test full evaluation pipeline with mock data
2. Test with real reward server
3. Test error recovery mechanisms

## 9. Performance Optimization

### 9.1 Optimization Strategies

1. **Parallel Processing**
   - Batch inference for multiple samples
   - Concurrent reward server requests
   - Async evaluation to not block training

2. **Memory Management**
   - Clear GPU cache after evaluation
   - Use half precision (bfloat16)
   - Stream processing for large datasets

3. **Caching**
   - Cache evaluated samples
   - Reuse model if same checkpoint

## 10. Monitoring and Logging

### 10.1 Logging Configuration

```python
import logging

# Configure evaluation logger
eval_logger = logging.getLogger('evaluation')
eval_logger.setLevel(logging.INFO)

handler = logging.FileHandler('evaluation.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
eval_logger.addHandler(handler)
```

### 10.2 Metrics to Track

- Evaluation duration per checkpoint
- Success rate per benchmark
- Average scores over time
- Error frequency and types

## 11. Dependencies

### 11.1 Python Packages

```txt
transformers>=4.35.0
torch>=2.0.0
aiohttp>=3.8.0
pandas>=1.5.0
tqdm>=4.65.0
requests>=2.28.0
matplotlib>=3.6.0
```

### 11.2 System Requirements

- GPU with sufficient memory (>24GB recommended)
- Python 3.8+
- Network access to reward server

## 12. Deployment Checklist

- [ ] Install all dependencies
- [ ] Configure evaluation parameters
- [ ] Test reward server connectivity
- [ ] Verify test data availability
- [ ] Run integration tests
- [ ] Set up logging
- [ ] Configure output directories
- [ ] Test with small dataset
- [ ] Monitor first evaluation run
- [ ] Verify report generation

## 13. Future Enhancements

1. **Web Dashboard** - Real-time evaluation monitoring
2. **Distributed Evaluation** - Multi-GPU evaluation
3. **Advanced Analytics** - Trend analysis, prediction
4. **Auto-tuning** - Adjust training based on evaluation
5. **Model Comparison** - Compare multiple checkpoints

## 14. Conclusion

This implementation provides a robust, scalable solution for automatic model evaluation during training. The modular design allows for easy maintenance and future enhancements while the async architecture ensures training performance is not impacted.

---

**Document Version**: 1.0  
**Last Updated**: 2024-08-24  
**Status**: Ready for Implementation