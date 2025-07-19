# /Users/luogan/Code/workflow_generation/Flow_RL/my_llama3_v100_PP/src/train_pp.py
# 专为 DeepSpeed 流水线并行设计的训练脚本

import os
import torch
import deepspeed
import transformers
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    AutoConfig, # 需要用 AutoConfig 先加载模型结构
    HfArgumentParser
)
from dataclasses import dataclass, field
from typing import Optional

# --- 定义参数类 ---
# TrainingArguments 将不再由 Trainer 使用，但我们仍可从中获取参数
from transformers import TrainingArguments

@dataclass
class ModelArguments:
    model_name_or_path: str = field(metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"})

@dataclass
class DataArguments:
    dataset_path: str = field(metadata={"help": "Path to the training data."})
    max_seq_length: Optional[int] = field(default=1024)

# --- 数据处理函数 (保持不变) ---
# ... (formatting_prompts_func 和 tokenize_function 可以直接复用) ...

# --- 主函数 ---
def train():
    global tokenizer # 全局变量以便数据处理函数使用
    
    # --- 解析参数 ---
    # 我们仍然使用 HfArgumentParser 来方便地解析命令行参数
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    # --- DeepSpeed 分布式环境初始化 ---
    # DeepSpeed 会自动处理多卡设置
    deepspeed.init_distributed()

    # --- 加载 Tokenizer ---
    tokenizer = AutoTokenizer.from_pretrained(model_args.model_name_or_path, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # --- 加载和处理数据集 ---
    # 这部分逻辑与之前基本相同
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
    
    # --- 构建模型 (适配流水线并行) ---
    print(f"Loading model CONFIG from {model_args.model_name_or_path}...")
    config = AutoConfig.from_pretrained(model_args.model_name_or_path)
    # 对于流水线并行，我们先创建一个“空”的模型结构
    model = AutoModelForCausalLM.from_config(config)

    # Gradient checkpointing 必须在模型内部开启
    model.gradient_checkpointing_enable()

    # --- 使用 deepspeed.initialize 替代 Trainer ---
    # 这是最核心的变化
    print("Initializing model with DeepSpeed...")
    # DeepSpeed 需要知道哪些参数需要被优化
    model_parameters = filter(lambda p: p.requires_grad, model.parameters())
    
    model_engine, optimizer, training_dataloader, lr_scheduler = deepspeed.initialize(
        args=training_args,
        model=model,
        model_parameters=model_parameters,
        training_data=tokenized_dataset
    )
    
    # --- 手动训练循环 ---
    print("Starting Pipeline Parallel SFT training...")
    for epoch in range(int(training_args.num_train_epochs)):
        print(f"Epoch {epoch+1}/{int(training_args.num_train_epochs)}")
        for step, batch in enumerate(training_dataloader):
            # 将数据移动到当前GPU
            batch = {k: v.to(model_engine.device) for k, v in batch.items()}
            
            # DeepSpeed 流水线并行的核心训练步骤
            loss = model_engine.train_batch(data_iter=iter([batch]))

            # loss 是一个包含了所有微批次损失的列表，我们可以取平均值
            if model_engine.is_pipeline_last_stage():
                avg_loss = sum(loss) / len(loss) if isinstance(loss, list) else loss
                print(f"Step {step+1}, Loss: {avg_loss.item()}")

            # --- 保存模型 ---
            # 可以在特定步骤保存 checkpoint
            if (step + 1) % training_args.save_steps == 0:
                print(f"Saving checkpoint at step {step+1}...")
                # client_sd 是一个包含了模型、优化器等状态的字典
                # tag 可以是步数或epoch号
                model_engine.save_checkpoint(training_args.output_dir, tag=f"step_{step+1}")

    print("Training finished. Saving final model...")
    model_engine.save_checkpoint(training_args.output_dir, tag="final")
    
    # 在主进程上保存tokenizer
    if model_engine.global_rank == 0:
        tokenizer.save_pretrained(training_args.output_dir)

    print(f"Model saved to {training_args.output_dir}")

if __name__ == "__main__":
    train()