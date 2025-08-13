#!/usr/bin/env python3
"""
评估脚本：对训练好的模型或检查点进行评估
支持计算困惑度（perplexity）和生成质量评估
"""

import os
import sys
import json
import torch
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from tqdm import tqdm
from datetime import datetime

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
)
from datasets import load_dataset
from torch.utils.data import DataLoader

# 添加父目录到路径，以便导入data_collator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_collator import DataCollatorForChatML


class ModelEvaluator:
    """
    模型评估器类
    负责加载模型、处理数据并计算评估指标
    """
    
    def __init__(
        self,
        model_path: str,
        model_type: str = "llama",
        device: str = "cuda",
        batch_size: int = 4,
        max_seq_length: int = 2048,
        use_flash_attention: bool = True
    ):
        """
        初始化评估器
        
        参数:
            model_path: 模型检查点路径
            model_type: 模型类型 ("llama" 或 "qwen")
            device: 计算设备
            batch_size: 批处理大小
            max_seq_length: 最大序列长度
            use_flash_attention: 是否使用Flash Attention
        """
        self.model_path = model_path
        self.model_type = model_type
        self.device = device if torch.cuda.is_available() else "cpu"
        self.batch_size = batch_size
        self.max_seq_length = max_seq_length
        
        print(f"📊 初始化评估器...")
        print(f"   模型路径: {model_path}")
        print(f"   模型类型: {model_type}")
        print(f"   设备: {self.device}")
        
        # 加载模型和tokenizer
        self._load_model_and_tokenizer(use_flash_attention)
    
    def _load_model_and_tokenizer(self, use_flash_attention: bool):
        """加载模型和分词器"""
        print("🔄 加载模型和tokenizer...")
        
        # 加载tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True
        )
        
        # 设置pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # 模型加载参数
        model_kwargs = {
            "torch_dtype": torch.bfloat16 if self.device == "cuda" else torch.float32,
            "trust_remote_code": True,
            "device_map": "auto" if self.device == "cuda" else None,
        }
        
        # Flash Attention配置
        if use_flash_attention and self.device == "cuda":
            model_kwargs["attn_implementation"] = "flash_attention_2"
        
        # 加载模型
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            **model_kwargs
        )
        
        # 设置为评估模式
        self.model.eval()
        
        print(f"✅ 模型加载完成")
    
    def calculate_perplexity(
        self,
        dataset_path: str,
        num_samples: Optional[int] = None,
        use_loss_mask: bool = False
    ) -> Dict[str, float]:
        """
        计算模型在数据集上的困惑度
        
        参数:
            dataset_path: 评估数据集路径（JSONL格式）
            num_samples: 评估样本数量（None表示全部）
            use_loss_mask: 是否只在assistant回复上计算损失
        
        返回:
            包含困惑度和其他指标的字典
        """
        print(f"\n📈 计算困惑度...")
        print(f"   数据集: {dataset_path}")
        print(f"   样本数: {num_samples if num_samples else '全部'}")
        print(f"   损失掩码: {'启用' if use_loss_mask else '禁用'}")
        
        # 加载数据集
        dataset = load_dataset('json', data_files=dataset_path, split='train')
        if num_samples:
            dataset = dataset.select(range(min(num_samples, len(dataset))))
        
        # 准备数据
        def format_messages(examples):
            """格式化消息为文本"""
            texts = []
            for messages in examples['messages']:
                text = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=False
                )
                texts.append(text)
            return {"text": texts}
        
        # 应用聊天模板
        dataset = dataset.map(
            format_messages,
            batched=True,
            desc="格式化数据"
        )
        
        # 分词
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding=False,
                max_length=self.max_seq_length,
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text", "messages"],
            desc="分词处理"
        )
        
        # 准备数据加载器
        if use_loss_mask:
            # 使用自定义data collator进行损失掩码
            data_collator = DataCollatorForChatML(
                tokenizer=self.tokenizer,
                model_type=self.model_type,
                pad_to_multiple_of=8
            )
        else:
            # 标准语言模型data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,
                pad_to_multiple_of=8
            )
        
        dataloader = DataLoader(
            tokenized_dataset,
            batch_size=self.batch_size,
            collate_fn=data_collator,
            shuffle=False
        )
        
        # 计算损失和困惑度
        total_loss = 0.0
        total_tokens = 0
        batch_losses = []
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="评估中"):
                # 将数据移到设备
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # 前向传播
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                # 计算有效token数（不包括padding和masked）
                valid_tokens = (labels != -100).sum().item()
                
                if valid_tokens > 0:
                    batch_loss = outputs.loss.item() * valid_tokens
                    total_loss += batch_loss
                    total_tokens += valid_tokens
                    batch_losses.append(outputs.loss.item())
        
        # 计算平均损失和困惑度
        avg_loss = total_loss / total_tokens if total_tokens > 0 else float('inf')
        perplexity = torch.exp(torch.tensor(avg_loss)).item()
        
        # 计算其他统计信息
        results = {
            "perplexity": perplexity,
            "avg_loss": avg_loss,
            "total_tokens": total_tokens,
            "num_samples": len(dataset),
            "batch_loss_std": np.std(batch_losses) if batch_losses else 0.0,
            "batch_loss_min": min(batch_losses) if batch_losses else 0.0,
            "batch_loss_max": max(batch_losses) if batch_losses else 0.0,
        }
        
        print(f"\n✅ 评估完成:")
        print(f"   困惑度: {perplexity:.2f}")
        print(f"   平均损失: {avg_loss:.4f}")
        print(f"   总token数: {total_tokens:,}")
        
        return results
    
    def generate_samples(
        self,
        prompts: List[str],
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        top_p: float = 0.9,
        do_sample: bool = True
    ) -> List[str]:
        """
        生成文本样本用于质量评估
        
        参数:
            prompts: 输入提示列表
            max_new_tokens: 最大生成token数
            temperature: 温度参数
            top_p: nucleus采样参数
            do_sample: 是否使用采样
        
        返回:
            生成的文本列表
        """
        print(f"\n🤖 生成样本...")
        print(f"   提示数量: {len(prompts)}")
        print(f"   最大新token: {max_new_tokens}")
        print(f"   温度: {temperature}")
        
        generated_texts = []
        
        for prompt in tqdm(prompts, desc="生成中"):
            # 格式化为消息
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # 应用聊天模板
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # 分词
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_seq_length
            ).to(self.device)
            
            # 生成
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            # 解码
            generated = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            generated_texts.append(generated)
        
        return generated_texts
    
    def save_results(self, results: Dict, output_path: str):
        """
        保存评估结果到JSON文件
        
        参数:
            results: 评估结果字典
            output_path: 输出文件路径
        """
        # 添加元信息
        results['metadata'] = {
            'model_path': self.model_path,
            'model_type': self.model_type,
            'timestamp': datetime.now().isoformat(),
            'device': self.device,
            'batch_size': self.batch_size,
            'max_seq_length': self.max_seq_length,
        }
        
        # 保存到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 结果已保存到: {output_path}")


def evaluate_checkpoint(
    checkpoint_path: str,
    eval_data_path: str,
    model_type: str = "llama",
    batch_size: int = 4,
    num_samples: Optional[int] = None,
    use_loss_mask: bool = False,
    output_dir: Optional[str] = None
) -> Dict:
    """
    评估单个检查点的便捷函数
    
    参数:
        checkpoint_path: 检查点路径
        eval_data_path: 评估数据路径
        model_type: 模型类型
        batch_size: 批大小
        num_samples: 评估样本数
        use_loss_mask: 是否使用损失掩码
        output_dir: 结果输出目录
    
    返回:
        评估结果字典
    """
    # 创建评估器
    evaluator = ModelEvaluator(
        model_path=checkpoint_path,
        model_type=model_type,
        batch_size=batch_size
    )
    
    # 计算困惑度
    results = evaluator.calculate_perplexity(
        dataset_path=eval_data_path,
        num_samples=num_samples,
        use_loss_mask=use_loss_mask
    )
    
    # 保存结果
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        checkpoint_name = os.path.basename(checkpoint_path)
        output_path = os.path.join(output_dir, f"eval_{checkpoint_name}.json")
        evaluator.save_results(results, output_path)
    
    return results


def main():
    """主函数：命令行接口"""
    parser = argparse.ArgumentParser(description="评估训练好的模型")
    
    # 基本参数
    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="模型或检查点路径"
    )
    parser.add_argument(
        "--eval_data",
        type=str,
        required=True,
        help="评估数据集路径（JSONL格式）"
    )
    parser.add_argument(
        "--model_type",
        type=str,
        default="llama",
        choices=["llama", "qwen"],
        help="模型类型"
    )
    
    # 评估参数
    parser.add_argument(
        "--batch_size",
        type=int,
        default=4,
        help="批处理大小"
    )
    parser.add_argument(
        "--num_samples",
        type=int,
        default=None,
        help="评估样本数量（默认全部）"
    )
    parser.add_argument(
        "--max_seq_length",
        type=int,
        default=2048,
        help="最大序列长度"
    )
    parser.add_argument(
        "--use_loss_mask",
        action="store_true",
        help="只在assistant回复上计算损失"
    )
    
    # 输出参数
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./eval_results",
        help="结果输出目录"
    )
    
    # 生成参数（可选）
    parser.add_argument(
        "--generate_samples",
        action="store_true",
        help="是否生成样本进行质量评估"
    )
    parser.add_argument(
        "--test_prompts",
        type=str,
        nargs="+",
        default=[
            "请解释什么是机器学习？",
            "写一个Python函数计算斐波那契数列",
            "如何提高代码质量？"
        ],
        help="测试提示列表"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 模型评估工具")
    print("="*60)
    
    # 执行评估
    results = evaluate_checkpoint(
        checkpoint_path=args.model_path,
        eval_data_path=args.eval_data,
        model_type=args.model_type,
        batch_size=args.batch_size,
        num_samples=args.num_samples,
        use_loss_mask=args.use_loss_mask,
        output_dir=args.output_dir
    )
    
    # 生成样本（如果需要）
    if args.generate_samples:
        print("\n" + "="*60)
        print("📝 生成测试样本")
        print("="*60)
        
        evaluator = ModelEvaluator(
            model_path=args.model_path,
            model_type=args.model_type,
            batch_size=1  # 生成时使用batch_size=1
        )
        
        generated = evaluator.generate_samples(
            prompts=args.test_prompts,
            max_new_tokens=128
        )
        
        # 打印生成结果
        for prompt, response in zip(args.test_prompts, generated):
            print(f"\n提示: {prompt}")
            print(f"回复: {response}")
            print("-"*40)
        
        # 保存生成样本
        if args.output_dir:
            samples_path = os.path.join(args.output_dir, "generated_samples.json")
            with open(samples_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "prompts": args.test_prompts,
                    "responses": generated,
                    "model_path": args.model_path,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            print(f"\n💾 生成样本已保存到: {samples_path}")
    
    print("\n" + "="*60)
    print("✅ 评估完成！")
    print("="*60)


if __name__ == "__main__":
    main()