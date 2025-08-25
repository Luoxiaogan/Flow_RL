# -*- coding: utf-8 -*-
"""
数据处理工具模块
从原始训练脚本中提取的数据加载和处理功能
"""
import torch
from typing import Optional, List
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from dataclasses import dataclass, field


@dataclass
class ModelArguments:
    """模型相关参数"""
    model_name_or_path: str = field(
        metadata={"help": "预训练模型路径"}
    )
    model_type: str = field(
        default="llama",
        metadata={"help": "模型类型: 'qwen' 或 'llama'"}
    )
    use_flash_attention_2: bool = field(
        default=True, 
        metadata={"help": "启用Flash Attention 2"}
    )
    use_loss_mask: bool = field(
        default=False,
        metadata={"help": "仅对助手回复计算损失（损失掩码）"}
    )


@dataclass
class DataArguments:
    """数据相关参数"""
    dataset_path: str = field(
        metadata={"help": "训练数据路径"}
    )
    max_seq_length: Optional[int] = field(default=2048)


@dataclass
class EvalArguments:
    """原地评估相关参数"""
    enable_inplace_eval: bool = field(
        default=False,
        metadata={"help": "在训练过程中启用原地评估"}
    )
    eval_interval: int = field(
        default=50,
        metadata={"help": "每N个训练步骤评估一次"}
    )
    eval_test_data_path: Optional[str] = field(
        default=None,
        metadata={"help": "评估测试数据JSONL文件路径"}
    )
    eval_batch_size: int = field(
        default=4,
        metadata={"help": "评估批次大小"}
    )
    max_eval_samples: Optional[int] = field(
        default=None,
        metadata={"help": "最大评估样本数（None表示全部）"}
    )
    eval_output_dir: Optional[str] = field(
        default="evaluation_reports",
        metadata={"help": "评估报告保存目录"}
    )


def setup_tokenizer(model_name: str, model_type: str):
    """
    根据模型类型设置tokenizer
    
    Args:
        model_name: 模型名称或路径
        model_type: 模型类型（'llama' 或 'qwen'）
        
    Returns:
        配置好的tokenizer
    """
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


def load_model(model_args: ModelArguments):
    """
    根据模型类型加载模型
    
    Args:
        model_args: 模型参数
        
    Returns:
        加载的模型
    """
    print(f"正在加载 {model_args.model_type} 模型，路径: {model_args.model_name_or_path}...")
    
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
    
    print(f"✓ 模型加载成功")
    return model


def formatting_prompts_func(examples, tokenizer, model_type):
    """
    根据模型类型格式化数据
    
    Args:
        examples: 数据样本
        tokenizer: 分词器
        model_type: 模型类型
        
    Returns:
        格式化后的文本
    """
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


def load_and_process_dataset(data_args: DataArguments, tokenizer, model_type: str, use_loss_mask: bool = False):
    """
    加载并处理数据集
    
    Args:
        data_args: 数据参数
        tokenizer: 分词器
        model_type: 模型类型
        use_loss_mask: 是否使用损失掩码
        
    Returns:
        处理后的数据集
    """
    print(f"正在加载数据集，路径: {data_args.dataset_path}...")
    raw_dataset = load_dataset('json', data_files=data_args.dataset_path, split="train")
    
    # 检查数据格式
    sample = raw_dataset[0]
    print(f"数据集样本键: {sample.keys()}")
    if 'messages' in sample:
        print(f"第一条消息: {sample['messages'][0] if sample['messages'] else '无消息'}")
    
    # 应用聊天模板格式化
    formatted_dataset = raw_dataset.map(
        lambda x: formatting_prompts_func(x, tokenizer, model_type),
        batched=True,
        remove_columns=raw_dataset.column_names,
        desc="格式化提示词"
    )
    
    # 根据是否使用损失掩码进行不同的标记化处理
    if use_loss_mask:
        print(f"为 {model_type} 使用损失掩码（仅对助手回复计算损失）")
        
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
            desc="为损失掩码进行标记化"
        )
    else:
        print("使用标准损失计算（对所有token计算损失）")
        
        def tokenize_function(examples):
            tokenized = tokenizer(
                examples["text"],
                truncation=True,
                padding=False,
                max_length=data_args.max_seq_length,
                return_overflowing_tokens=False,
            )
            # 对于标准训练，labels和input_ids相同
            tokenized["labels"] = tokenized["input_ids"].copy()
            return tokenized
        
        train_dataset = formatted_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"],
            desc="标准标记化"
        )
    
    print(f"✓ 数据集处理完成，样本数: {len(train_dataset)}")
    return train_dataset


def load_test_data(test_data_path: str, max_samples: Optional[int] = None):
    """
    加载测试数据
    
    Args:
        test_data_path: 测试数据路径
        max_samples: 最大样本数
        
    Returns:
        测试样本列表
    """
    import json
    
    if not test_data_path:
        print("⚠ 未提供测试数据路径")
        return []
    
    test_samples = []
    
    try:
        with open(test_data_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    sample = json.loads(line.strip())
                    test_samples.append(sample)
                    
                    # 限制样本数
                    if max_samples and len(test_samples) >= max_samples:
                        break
        
        print(f"✓ 成功加载 {len(test_samples)} 个测试样本")
        if max_samples and len(test_samples) >= max_samples:
            print(f"  （限制为最多 {max_samples} 个样本）")
            
    except Exception as e:
        print(f"❌ 加载测试数据失败: {e}")
        return []
    
    return test_samples