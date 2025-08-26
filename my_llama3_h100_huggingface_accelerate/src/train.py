# -*- coding: utf-8 -*-
"""
基于DeepSpeed ZeRO-2的优化训练脚本
完全由DeepSpeed管理优化过程，Accelerate仅负责分布式协调
"""
import os
import sys
import yaml
import torch
import logging
from pathlib import Path
from accelerate import Accelerator
from accelerate.logging import get_logger
from transformers import HfArgumentParser, TrainingArguments
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
import wandb

# 添加本地模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_utils import (
    ModelArguments, 
    DataArguments, 
    EvalArguments,
    setup_tokenizer,
    load_model,
    load_and_process_dataset,
    load_test_data
)
from data_collator import DataCollatorForChatML
from evaluation.simple_evaluator import SimpleEvaluator
from evaluation.score_collector import ScoreCollector
from evaluation.report_generator import ReportGenerator

logger = get_logger(__name__)

def load_evaluation_config(config_path: str) -> dict:
    """加载评估配置文件"""
    config_path = Path(config_path)
    if not config_path.exists():
        logger.warning(f"评估配置文件不存在: {config_path}")
        return {}
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    logger.info(f"已加载评估配置: {config_path}")
    return config

def main():
    """主训练函数 - DeepSpeed完全管理优化过程"""
    
    # 解析命令行参数
    parser = HfArgumentParser((ModelArguments, DataArguments, EvalArguments, TrainingArguments))
    model_args, data_args, eval_args, training_args = parser.parse_args_into_dataclasses()

    # 初始化Accelerator（DeepSpeed要求完全无参数初始化）
    accelerator = Accelerator()
    
    # 设置日志
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
    )
    logger.info(accelerator.state, main_process_only=False)
    
    if accelerator.is_local_main_process:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.ERROR)
    
    # 设置随机种子
    if training_args.seed is not None:
        import random
        import numpy as np
        random.seed(training_args.seed)
        np.random.seed(training_args.seed)
        torch.manual_seed(training_args.seed)
        torch.cuda.manual_seed_all(training_args.seed)
    
    # 初始化W&B（仅在主进程）
    if training_args.report_to == "wandb" and accelerator.is_main_process:
        wandb.init(
            project=os.environ.get("WANDB_PROJECT", "llama3-8b-accelerate-training"),
            name=f"{model_args.model_type}_deepspeed_zero2_{training_args.run_name or ''}",
            config={
                "model_type": model_args.model_type,
                "model_path": model_args.model_name_or_path,
                "dataset_path": data_args.dataset_path,
                "use_loss_mask": model_args.use_loss_mask,
                "enable_eval": eval_args.enable_inplace_eval,
                "eval_interval": eval_args.eval_interval,
                "max_seq_length": data_args.max_seq_length,
                "per_device_train_batch_size": training_args.per_device_train_batch_size,
                "gradient_accumulation_steps": training_args.gradient_accumulation_steps,
                "num_train_epochs": training_args.num_train_epochs
            }
        )
    
    # 加载tokenizer和模型
    tokenizer = setup_tokenizer(model_args.model_name_or_path, model_args.model_type)
    model = load_model(model_args)
    
    # 启用梯度检查点（如果在TrainingArguments中指定）
    if training_args.gradient_checkpointing:
        model.gradient_checkpointing_enable()
        logger.info("✓ 梯度检查点已启用（节省内存）")
    
    # 加载和处理数据集
    train_dataset = load_and_process_dataset(
        data_args, tokenizer, model_args.model_type, model_args.use_loss_mask
    )
    
    # 设置数据collator
    if model_args.use_loss_mask:
        data_collator = DataCollatorForChatML(
            tokenizer=tokenizer,
            model_type=model_args.model_type,
            pad_to_multiple_of=8,  # 对齐到8的倍数提高效率
        )
    else:
        from transformers import DataCollatorForLanguageModeling
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,  # 因果语言建模
            pad_to_multiple_of=8
        )
    
    # 创建DataLoader
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=training_args.per_device_train_batch_size,
        shuffle=True,
        collate_fn=data_collator,
        num_workers=training_args.dataloader_num_workers,
        pin_memory=True,
        drop_last=training_args.dataloader_drop_last
    )
    
    # 使用Accelerator准备模型和数据加载器
    # 注意：不传递optimizer和lr_scheduler，让DeepSpeed完全管理
    model, train_dataloader = accelerator.prepare(model, train_dataloader)
    
    # 初始化评估组件（如果启用）
    evaluator = None
    score_collector = None
    report_generator = None
    
    if eval_args.enable_inplace_eval and accelerator.is_main_process:
        # 加载评估配置
        eval_config = load_evaluation_config("/nas/ganluo/Flow_RL/my_llama3_h100_huggingface_accelerate/configs/evaluation_config.yaml")

        print(f"🐺 🐺 🐺 🐺 🐺 :eval_config = \n{eval_config}")
        
        # 初始化评估组件
        evaluator = SimpleEvaluator()

        # 从reward_server配置构建正确的URL
        reward_config = eval_config.get('reward_server', {})
        fallback_config = reward_config.get('fallback', {})
        print(f"🐺 🐺 🐺 🐺 🐺 :fallback_config = \n{fallback_config}")
        # server_host = fallback_config.get('host', 'localhost')
        server_port = fallback_config.get('prot', 8899)
        print(f"🐺 🐺 🐺 🐺 🐺 : port = {server_port}")
        server_url=f"http://localhost:{server_port}"
        print(f"🐺 🐺 🐺 🐺 🐺 :server_url={server_url}")
        score_collector = ScoreCollector(
            server_url=server_url
        )
        report_generator = ReportGenerator()
        
        # 加载测试数据
        test_samples = load_test_data(
            eval_args.eval_test_data_path,
            max_samples=eval_args.max_eval_samples
        )
        logger.info(f"已加载 {len(test_samples)} 个评估样本")
    
    # 计算总训练步数（用于进度条）
    num_update_steps_per_epoch = len(train_dataloader) // training_args.gradient_accumulation_steps
    max_train_steps = int(training_args.num_train_epochs * num_update_steps_per_epoch)
    
    # 创建进度条
    progress_bar = tqdm(
        range(max_train_steps), 
        disable=not accelerator.is_local_main_process,
        desc="训练进度"
    )
    
    # 训练循环
    logger.info("🚀 开始训练...")
    logger.info(f"  训练轮数 = {training_args.num_train_epochs}")
    logger.info(f"  每设备批次大小 = {training_args.per_device_train_batch_size}")
    logger.info(f"  梯度累积步数 = {training_args.gradient_accumulation_steps}")
    logger.info(f"  总优化步数 = {max_train_steps}")
    
    global_step = 0
    total_loss = 0.0
    
    for epoch in range(int(training_args.num_train_epochs)):
        model.train()
        
        for step, batch in enumerate(train_dataloader):
            # 前向传播
            outputs = model(**batch)
            loss = outputs.loss
            
            # 反向传播（DeepSpeed自动处理梯度累积）
            accelerator.backward(loss)
            
            # 更新统计信息
            loss_item = loss.detach().float()
            total_loss += loss_item
            
            # 更新进度条（每个梯度累积步骤）
            if step % training_args.gradient_accumulation_steps == 0:
                if accelerator.is_main_process:
                    progress_bar.set_postfix({
                        'loss': f"{loss_item:.4f}",
                        'epoch': epoch,
                        'step': global_step
                    })
                
                progress_bar.update(1)
                global_step += 1
                
                # 日志记录
                if global_step % training_args.logging_steps == 0:
                    avg_loss = total_loss / training_args.logging_steps / training_args.gradient_accumulation_steps
                    
                    if accelerator.is_main_process:
                        log_dict = {
                            "train_loss": avg_loss,
                            "epoch": epoch,
                            "global_step": global_step
                        }
                        
                        if training_args.report_to == "wandb":
                            wandb.log(log_dict, step=global_step)
                        
                        logger.info(f"Step {global_step}: loss={avg_loss:.4f}")
                    
                    total_loss = 0.0
                
                # 保存检查点
                if global_step % training_args.save_steps == 0:
                    accelerator.wait_for_everyone()
                    if accelerator.is_main_process:
                        output_dir = Path(training_args.output_dir) / f"checkpoint-{global_step}"
                        output_dir.mkdir(parents=True, exist_ok=True)
                        
                        unwrapped_model = accelerator.unwrap_model(model)
                        unwrapped_model.save_pretrained(
                            output_dir,
                            is_main_process=accelerator.is_main_process,
                            save_function=accelerator.save,
                            state_dict=accelerator.get_state_dict(model)
                        )
                        tokenizer.save_pretrained(output_dir)
                        logger.info(f"✅ 保存检查点到 {output_dir}")
                
                # 原地评估（如果启用）
                if (eval_args.enable_inplace_eval and 
                    global_step % eval_args.eval_interval == 0 and 
                    evaluator is not None and 
                    accelerator.is_main_process):
                    
                    logger.info(f"📊 开始评估 (Step {global_step})...")
                    model.eval()
                    
                    # 生成解决方案
                    solutions = evaluator.evaluate_during_training(
                        model=model,
                        tokenizer=tokenizer,
                        test_samples=test_samples,
                        batch_size=eval_args.eval_batch_size,
                        accelerator=accelerator
                    )
                    
                    # 评分
                    scores = score_collector.batch_evaluate(
                        test_samples=test_samples,
                        solutions=solutions,
                        batch_size=8
                    )
                    
                    # 生成报告
                    report = report_generator.generate_report(
                        test_samples=test_samples,
                        solutions=solutions,
                        scores=scores,
                        step=global_step
                    )
                    
                    # 保存评估报告
                    if eval_args.eval_output_dir:
                        report_path = Path(eval_args.eval_output_dir) / f"eval_report_step_{global_step}.json"
                        report_path.parent.mkdir(parents=True, exist_ok=True)
                        report_generator.save_report(report, report_path)
                        logger.info(f"✅ 评估报告已保存到 {report_path}")
                    
                    # 记录到W&B
                    if training_args.report_to == "wandb":
                        wandb.log({
                            "eval_accuracy": report["accuracy"],
                            "eval_total_score": report["total_score"],
                            "eval_max_score": report["max_score"]
                        }, step=global_step)
                    
                    model.train()
    
    # 训练结束
    accelerator.wait_for_everyone()
    
    # 保存最终模型
    if accelerator.is_main_process:
        output_dir = Path(training_args.output_dir) / "final_model"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        unwrapped_model = accelerator.unwrap_model(model)
        unwrapped_model.save_pretrained(
            output_dir,
            is_main_process=accelerator.is_main_process,
            save_function=accelerator.save,
            state_dict=accelerator.get_state_dict(model)
        )
        tokenizer.save_pretrained(output_dir)
        logger.info(f"✅ 最终模型已保存到 {output_dir}")
    
    # 清理W&B
    if training_args.report_to == "wandb" and accelerator.is_main_process:
        wandb.finish()
    
    logger.info("🎉 训练完成！")

if __name__ == "__main__":
    main()