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

# --- 定义参数类 ---
@dataclass
class ModelArguments:
    model_name_or_path: str = field(metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"})
    use_flash_attention_2: bool = field(default=True, metadata={"help": "Enable Flash Attention 2."})

@dataclass
class DataArguments:
    dataset_path: str = field(metadata={"help": "Path to the training data."})
    max_seq_length: Optional[int] = field(default=2048)

# --- 主函数 ---
def train():
    # --- 解析参数 ---
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    # --- 设置 W&B ---
    if training_args.report_to == "wandb":
        os.environ["WANDB_PROJECT"] = "llama3-8b-full-finetune"
        os.environ["WANDB_LOG_MODEL"] = "checkpoint"

    # --- 加载 Tokenizer ---
    tokenizer = AutoTokenizer.from_pretrained(model_args.model_name_or_path, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    # Llama 3 没有 pad_token_id, 我们需要设置一个，但也要确保 attention_mask 正确
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # --- 加载模型 ---
    print(f"Loading model from {model_args.model_name_or_path}...")
    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        torch_dtype=torch.bfloat16, # 使用 bfloat16
        use_flash_attention_2=model_args.use_flash_attention_2,
        # device_map 不再需要，DeepSpeed会处理
    )
    
    # --- 加载和处理数据集 ---
    raw_dataset = load_dataset('json', data_files=data_args.dataset_path, split="train")

    def formatting_prompts_func(examples):
        # SFTTrainer的 apply_chat_template 效果更好，这里手动模拟
        # 这个函数将 'messages' 列表转换为单个文本字符串
        output_texts = []
        for i in range(len(examples['messages'])):
            text = tokenizer.apply_chat_template(examples['messages'][i], tokenize=False, add_generation_prompt=False)
            output_texts.append(text)
        return output_texts

    # 使用 Trainer 的内置功能来处理聊天模板
    # 这确保了数据在被模型看到之前被正确格式化
    
    # --- 初始化 Trainer ---
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=raw_dataset,
        # 我们让 Trainer 在内部处理聊天模板格式化
        # Trainer 会自动寻找 'messages' 列并应用模板
        data_collator=transformers.DataCollatorForSFT(tokenizer=tokenizer, max_seq_length=data_args.max_seq_length),
    )
    
    # 禁用缓存以提高训练效率
    if hasattr(model.config, "use_cache"):
        model.config.use_cache = False

    # --- 开始训练 ---
    print("Starting full SFT training...")
    trainer.train()

    # --- 保存模型 ---
    # DeepSpeed ZeRO-3 需要特殊方式保存，Trainer会自动处理
    # 它会收集所有分片的权重，然后在 rank 0 上保存完整模型
    print("Training finished. Saving model...")
    trainer.save_model(training_args.output_dir)
    tokenizer.save_pretrained(training_args.output_dir)
    print(f"Model saved to {training_args.output_dir}")

if __name__ == "__main__":
    train()