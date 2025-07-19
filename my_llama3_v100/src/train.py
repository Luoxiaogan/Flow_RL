# /Users/luogan/Code/workflow_generation/Flow_RL/my_llama3_v100/src/train.py
import os
import torch
import transformers
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    HfArgumentParser,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from dataclasses import dataclass, field
from typing import Optional

# --- 定义参数类 ---
# 这些 dataclass 与原始文件保持一致
@dataclass
class ModelArguments:
    model_name_or_path: str = field(metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"})
    use_flash_attention_2: bool = field(default=True, metadata={"help": "Enable Flash Attention 2."})

@dataclass
class DataArguments:
    dataset_path: str = field(metadata={"help": "Path to the training data."})
    max_seq_length: Optional[int] = field(default=2048)

def formatting_prompts_func(examples):
    """格式化数据集中的聊天数据"""
    output_texts = []
    for i in range(len(examples['messages'])):
        text = tokenizer.apply_chat_template(
            examples['messages'][i], 
            tokenize=False, 
            add_generation_prompt=False
        )
        output_texts.append(text)
    return {"text": output_texts}

# --- 主函数 ---
def train():
    global tokenizer
    
    # --- 解析参数 ---
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    # --- 设置 W&B ---
    if training_args.report_to == "wandb":
        os.environ["WANDB_LOG_MODEL"] = "checkpoint"

    # --- 加载 Tokenizer ---
    tokenizer = AutoTokenizer.from_pretrained(model_args.model_name_or_path, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # --- 加载模型 ---
    print(f"Loading model from {model_args.model_name_or_path}...")
    
    # ========================== [核心修改点] ==========================
    # 动态确定模型加载时的数据类型(torch_dtype)
    # 这使得代码可以根据传入的 --fp16 或 --bf16 参数自动适应V100或A800
    if training_args.fp16:
        torch_dtype = torch.float16
        print("Data type for model loading set to: torch.float16 (FP16)")
    elif training_args.bf16:
        torch_dtype = torch.bfloat16
        print("Data type for model loading set to: torch.bfloat16 (BF16)")
    else:
        # 如果未指定混合精度，则默认为全精度
        torch_dtype = torch.float32
        print("No mixed precision specified. Data type for model loading set to: torch.float32")

    model_kwargs = {
        "torch_dtype": torch_dtype,
    }
    
    # 根据命令行参数动态决定是否使用 Flash Attention 2
    if model_args.use_flash_attention_2:
        print("Enabling Flash Attention 2.")
        model_kwargs["attn_implementation"] = "flash_attention_2"
    else:
        print("Flash Attention 2 is disabled.")
    # =================================================================

    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        **model_kwargs
    )
    
    # --- 加载和处理数据集 ---
    raw_dataset = load_dataset('json', data_files=data_args.dataset_path, split="train")
    
    formatted_dataset = raw_dataset.map(
        formatting_prompts_func,
        batched=True,
        remove_columns=raw_dataset.column_names
    )
    
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding=False,
            max_length=data_args.max_seq_length,
            return_overflowing_tokens=False,
        )
    
    tokenized_dataset = formatted_dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text"]
    )
    
    # --- 初始化 Trainer ---
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(
            tokenizer=tokenizer, 
            mlm=False,
        ),
    )
    
    if hasattr(model.config, "use_cache"):
        model.config.use_cache = False

    # --- 开始训练 ---
    print("Starting full SFT training...")
    trainer.train()

    # --- 保存模型 ---
    print("Training finished. Saving model...")
    trainer.save_model(training_args.output_dir)
    tokenizer.save_pretrained(training_args.output_dir)
    print(f"Model saved to {training_args.output_dir}")

if __name__ == "__main__":
    train()