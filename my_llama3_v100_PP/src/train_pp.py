# /Users/luogan/Code/workflow_generation/Flow_RL/my_llama3_v100_PP/src/train_pp.py
# 专为 DeepSpeed 流水线并行设计的训练脚本 - 最终修正版

import os
import json # <-- 新增
import torch
import deepspeed
import transformers
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    AutoConfig,
    HfArgumentParser
)
from dataclasses import dataclass, field
from typing import Optional
from transformers import TrainingArguments

# ... ( dataclass 定义不变 ) ...
@dataclass
class ModelArguments:
    model_name_or_path: str = field(metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"})

@dataclass
class DataArguments:
    dataset_path: str = field(metadata={"help": "Path to the training data."})
    max_seq_length: Optional[int] = field(default=1024)


def train():
    global tokenizer
    
    # --- 解析参数 ---
    # 这次 HfArgumentParser 的作用仅仅是解析我们关心的训练超参数
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    # --- DeepSpeed 分布式环境初始化 ---
    deepspeed.init_distributed()

    # ... ( Tokenizer 和数据加载部分不变 ) ...
    tokenizer = AutoTokenizer.from_pretrained(model_args.model_name_or_path, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    raw_dataset = load_dataset('json', data_files=data_args.dataset_path, split="train")
    
    def formatting_prompts_func(examples):
        output_texts = []
        for i in range(len(examples['messages'])):
            text = tokenizer.apply_chat_template(examples['messages'][i], tokenize=False, add_generation_prompt=False)
            output_texts.append(text)
        return {"text": output_texts}

    formatted_dataset = raw_dataset.map(formatting_prompts_func, batched=True, remove_columns=raw_dataset.column_names)
    
    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding=False, max_length=data_args.max_seq_length)
    
    tokenized_dataset = formatted_dataset.map(tokenize_function, batched=True, remove_columns=["text"])
    
    # --- 构建模型 ---
    print(f"Loading model CONFIG from {model_args.model_name_or_path}...")
    config = AutoConfig.from_pretrained(model_args.model_name_or_path)
    model = AutoModelForCausalLM.from_config(config)
    model.gradient_checkpointing_enable()

    # --- 使用 deepspeed.initialize (核心修改点) ---
    print("Initializing model with DeepSpeed...")
    
    # 手动加载 DeepSpeed JSON 配置文件
    # training_args.deepspeed 属性现在是我们配置文件的唯一来源
    with open(training_args.deepspeed, 'r') as f:
        ds_config = json.load(f)

    model_parameters = filter(lambda p: p.requires_grad, model.parameters())
    
    model_engine, optimizer, training_dataloader, lr_scheduler = deepspeed.initialize(
        args=training_args,
        model=model,
        model_parameters=model_parameters,
        training_data=tokenized_dataset,
        config=ds_config # <-- 将解析好的配置字典直接传给 config 参数
    )
    
    # ... (手动训练循环和保存部分不变) ...
    print("Starting Pipeline Parallel SFT training...")
    for epoch in range(int(training_args.num_train_epochs)):
        print(f"Epoch {epoch+1}/{int(training_args.num_train_epochs)}")
        for step, batch in enumerate(training_dataloader):
            batch = {k: v.to(model_engine.device) for k, v in batch.items() if isinstance(v, torch.Tensor)}
            loss = model_engine.train_batch(data_iter=iter([batch]))
            if model_engine.is_pipeline_last_stage():
                if loss is not None:
                    avg_loss = sum(l.mean() for l in loss) / len(loss) if isinstance(loss, list) else loss
                    print(f"Rank {model_engine.global_rank} Step {step+1}, Loss: {avg_loss.item()}")
            if (step + 1) % training_args.save_steps == 0:
                print(f"Saving checkpoint at step {step+1}...")
                model_engine.save_checkpoint(training_args.output_dir, tag=f"step_{step+1}")
    
    print("Training finished. Saving final model...")
    model_engine.save_checkpoint(training_args.output_dir, tag="final")
    if model_engine.global_rank == 0:
        tokenizer.save_pretrained(training_args.output_dir)
    print(f"Model saved to {training_args.output_dir}")

if __name__ == "__main__":
    train()