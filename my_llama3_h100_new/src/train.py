# src/train.py
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
from .data_collator import DataCollatorForChatML, DataCollatorForCausalLMWithMasking

# --- 定义参数类 ---
@dataclass
class ModelArguments:
    model_name_or_path: str = field(
        metadata={"help": "Path to pretrained model"}
    )
    model_type: str = field(
        default="llama",
        metadata={"help": "Model type: 'qwen' or 'llama'"}
    )
    use_flash_attention_2: bool = field(
        default=True, 
        metadata={"help": "Enable Flash Attention 2"}
    )
    use_loss_mask: bool = field(
        default=False,
        metadata={"help": "Only compute loss on assistant responses (loss masking)"}
    )

@dataclass
class DataArguments:
    dataset_path: str = field(
        metadata={"help": "Path to the training data"}
    )
    max_seq_length: Optional[int] = field(default=2048)

def setup_tokenizer(model_name: str, model_type: str):
    """根据模型类型设置tokenizer"""
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, 
        trust_remote_code=True
    )
    
    if model_type == "llama":
        # Llama特定设置
        tokenizer.pad_token = tokenizer.eos_token
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id
    elif model_type == "qwen":
        # Qwen特定设置
        # Qwen通常已经有pad_token，但检查一下
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
    
    return tokenizer

def load_model(model_args):
    """根据模型类型加载模型"""
    print(f"Loading {model_args.model_type} model from {model_args.model_name_or_path}...")
    
    model_kwargs = {
        "torch_dtype": torch.bfloat16,
        "trust_remote_code": True,  # Qwen需要这个
    }
    
    # Flash Attention 2 配置
    if model_args.use_flash_attention_2:
        # 检查模型是否支持Flash Attention 2
        if model_args.model_type == "qwen":
            # Qwen 2.5 支持 Flash Attention 2
            model_kwargs["attn_implementation"] = "flash_attention_2"
        elif model_args.model_type == "llama":
            # Llama 3.1 也支持
            model_kwargs["attn_implementation"] = "flash_attention_2"
    
    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        **model_kwargs
    )
    
    # 禁用缓存以提高训练效率
    if hasattr(model.config, "use_cache"):
        model.config.use_cache = False
    
    return model

def formatting_prompts_func(examples, tokenizer, model_type):
    """根据模型类型格式化数据"""
    output_texts = []
    
    for i in range(len(examples['messages'])):
        messages = examples['messages'][i]
        
        # 应用相应的聊天模板
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        output_texts.append(text)
    
    return {"text": output_texts}

# --- 主函数 ---
def train():
    # --- 解析参数 ---
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    # --- 设置 W&B ---
    if training_args.report_to == "wandb":
        os.environ["WANDB_LOG_MODEL"] = "checkpoint"
        # 设置运行名称
        os.environ["WANDB_RUN_NAME"] = f"{model_args.model_type}_sft_{training_args.run_name or ''}"

    # --- 加载 Tokenizer ---
    tokenizer = setup_tokenizer(model_args.model_name_or_path, model_args.model_type)
    
    # --- 加载模型 ---
    model = load_model(model_args)
    
    # --- 加载和处理数据集 ---
    print(f"Loading dataset from {data_args.dataset_path}...")
    raw_dataset = load_dataset('json', data_files=data_args.dataset_path, split="train")
    
    # 检查数据格式
    sample = raw_dataset[0]
    print(f"Dataset sample keys: {sample.keys()}")
    if 'messages' in sample:
        print(f"First message: {sample['messages'][0] if sample['messages'] else 'No messages'}")
    
    # 应用聊天模板格式化
    formatted_dataset = raw_dataset.map(
        lambda x: formatting_prompts_func(x, tokenizer, model_args.model_type),
        batched=True,
        remove_columns=raw_dataset.column_names,
        desc="Formatting prompts"
    )
    
    # --- 选择 Data Collator 和准备数据集 ---
    if model_args.use_loss_mask:
        print(f"Using loss masking for {model_args.model_type} (only computing loss on assistant responses)")
        
        # For loss masking, tokenize text but keep it simple (DataCollator will handle labels)
        def tokenize_for_masking(examples):
            tokenized = tokenizer(
                examples["text"],
                truncation=True,
                padding=False,
                max_length=data_args.max_seq_length,
                return_overflowing_tokens=False,
            )
            return tokenized
        
        train_dataset = formatted_dataset.map(
            tokenize_for_masking,
            batched=True,
            remove_columns=["text"],
            desc="Tokenizing for loss masking"
        )
        
        data_collator = DataCollatorForChatML(
            tokenizer=tokenizer,
            model_type=model_args.model_type,
            pad_to_multiple_of=8
        )
    else:
        print("Using standard causal language modeling (loss on all tokens)")
        
        # Standard tokenization
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                padding=False,
                max_length=data_args.max_seq_length,
                return_overflowing_tokens=False,
            )
        
        train_dataset = formatted_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"],
            desc="Tokenizing"
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,  # 因果语言建模
            pad_to_multiple_of=8  # 优化性能
        )
    
    print(f"Dataset size: {len(train_dataset)} samples")
    
    # --- 初始化 Trainer ---
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=data_collator,
    )

    # --- 开始训练 ---
    print(f"Starting {model_args.model_type} SFT training...")
    print(f"Total training samples: {len(train_dataset)}")
    print(f"Number of epochs: {training_args.num_train_epochs}")
    if model_args.use_loss_mask:
        print("Loss masking: ENABLED (only assistant tokens contribute to loss)")
    
    trainer.train()

    # --- 保存最终模型 ---
    print("Training finished. Saving model...")
    
    # 使用 Trainer 的 save_model 方法处理 DeepSpeed ZeRO-3
    trainer.save_model(training_args.output_dir)
    
    # 保存 tokenizer
    if trainer.is_world_process_zero():
        tokenizer.save_pretrained(training_args.output_dir)
        
        # 保存训练配置信息
        import json
        config_info = {
            "model_type": model_args.model_type,
            "base_model": model_args.model_name_or_path,
            "max_seq_length": data_args.max_seq_length,
            "training_samples": len(train_dataset),
            "epochs": training_args.num_train_epochs,
            "global_batch_size": training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps * training_args.world_size,
            "use_loss_mask": model_args.use_loss_mask,
        }
        with open(os.path.join(training_args.output_dir, "training_config.json"), "w") as f:
            json.dump(config_info, f, indent=2)
        
        print(f"Model and tokenizer saved to {training_args.output_dir}")

if __name__ == "__main__":
    train()