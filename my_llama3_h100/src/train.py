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
from transformers.trainer_callback import TrainerCallback, TrainerControl, TrainerState
from transformers.training_args import TrainingArguments as HfTrainingArguments

# --- 定义参数类 ---
@dataclass
class ModelArguments:
    model_name_or_path: str = field(metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"})
    use_flash_attention_2: bool = field(default=True, metadata={"help": "Enable Flash Attention 2."})

@dataclass
class DataArguments:
    dataset_path: str = field(metadata={"help": "Path to the training data."})
    max_seq_length: Optional[int] = field(default=2048)

class SaveInferenceWeightsCallback(TrainerCallback):
    """自定义回调，仅保存推理所需的模型权重"""
    
    def __init__(self, output_dir: str, save_steps: int, save_total_limit: int = None):
        self.output_dir = output_dir
        self.save_steps = save_steps
        self.save_total_limit = save_total_limit
        self.saved_checkpoints = []
    
    def on_step_end(self, args: HfTrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        # 每 save_steps 步保存一次
        if state.global_step % self.save_steps == 0 and state.global_step > 0:
            checkpoint_dir = os.path.join(self.output_dir, f"checkpoint-{state.global_step}")
            self._save_inference_weights(kwargs["model"], kwargs["tokenizer"], checkpoint_dir)
            
            # 管理保存的检查点数量
            self.saved_checkpoints.append(checkpoint_dir)
            if self.save_total_limit and len(self.saved_checkpoints) > self.save_total_limit:
                # 删除最旧的检查点
                old_checkpoint = self.saved_checkpoints.pop(0)
                if os.path.exists(old_checkpoint):
                    import shutil
                    shutil.rmtree(old_checkpoint)
                    print(f"Removed old checkpoint: {old_checkpoint}")
    
    def on_train_end(self, args: HfTrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        # 训练结束时保存最终模型
        self._save_inference_weights(kwargs["model"], kwargs["tokenizer"], self.output_dir)
    
    def _save_inference_weights(self, model, tokenizer, save_path):
        """仅保存推理所需的权重"""
        print(f"Saving inference weights to {save_path}...")
        os.makedirs(save_path, exist_ok=True)
        
        # 从 DeepSpeed 收集模型权重
        if hasattr(model, 'module'):
            # DeepSpeed wrapped model
            unwrapped_model = model.module
        else:
            unwrapped_model = model
        
        # 使用 save_pretrained 保存模型（这会自动处理 DeepSpeed 的权重收集）
        unwrapped_model.save_pretrained(
            save_path,
            state_dict=unwrapped_model.state_dict(),
            safe_serialization=True  # 使用 safetensors 格式
        )
        
        # 保存 tokenizer
        tokenizer.save_pretrained(save_path)
        
        print(f"Inference weights saved to {save_path}")

def formatting_prompts_func(examples):
    """格式化数据集中的聊天数据"""
    output_texts = []
    for i in range(len(examples['messages'])):
        # 应用聊天模板
        text = tokenizer.apply_chat_template(
            examples['messages'][i], 
            tokenize=False, 
            add_generation_prompt=False
        )
        output_texts.append(text)
    return {"text": output_texts}

# --- 主函数 ---
def train():
    global tokenizer  # 需要在formatting_prompts_func中使用
    
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
    model_kwargs = {
        "torch_dtype": torch.bfloat16,
    }
    # 只有在支持时才添加 Flash Attention 2
    if model_args.use_flash_attention_2:
        model_kwargs["attn_implementation"] = "flash_attention_2"
    
    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        **model_kwargs
    )
    
    # --- 加载和处理数据集 ---
    raw_dataset = load_dataset('json', data_files=data_args.dataset_path, split="train")
    
    # 应用聊天模板格式化
    formatted_dataset = raw_dataset.map(
        formatting_prompts_func,
        batched=True,
        remove_columns=raw_dataset.column_names
    )
    
    # 对文本进行tokenization
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
    
    # --- 初始化自定义回调 ---
    # 从 training_args 中提取保存相关参数
    save_inference_callback = SaveInferenceWeightsCallback(
        output_dir=training_args.output_dir,
        save_steps=training_args.save_steps,
        save_total_limit=training_args.save_total_limit
    )
    
    # --- 初始化 Trainer ---
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(
            tokenizer=tokenizer, 
            mlm=False,  # 因果语言建模，不是掩码语言建模
        ),
        callbacks=[save_inference_callback]
    )
    
    # 禁用缓存以提高训练效率
    if hasattr(model.config, "use_cache"):
        model.config.use_cache = False

    # --- 开始训练 ---
    print("Starting full SFT training...")
    trainer.train()

    # --- 最终模型保存已由回调处理 ---
    print("Training finished. Model has been saved by callback.")

if __name__ == "__main__":
    train()