# -*- coding: utf-8 -*-
"""
基于Accelerate的简化训练脚本
从复杂的7+1卡系统迁移而来，使用标准8卡Accelerate分布式训练
"""
import os
import sys
import yaml
import torch
# import asyncio  # 不再需要异步支持
import logging
from pathlib import Path
from accelerate import Accelerator
from accelerate.logging import get_logger
from transformers import (
    HfArgumentParser,
    TrainingArguments,
    get_cosine_schedule_with_warmup
)
from torch.optim import AdamW
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
    """
    加载评估配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"✓ 成功加载评估配置: {config_path}")
        return config
    except Exception as e:
        logger.error(f"❌ 加载评估配置失败: {e}")
        return {}

def main():
    """
    主训练函数 - 基于Accelerate的简化版本
    """
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
    
    # 设置随机种子
    if training_args.seed is not None:
        torch.manual_seed(training_args.seed)
    
    # 只在主进程打印信息
    if accelerator.is_main_process:
        logger.info("🚀 开始基于Accelerate的简化训练")
        logger.info(f"模型类型: {model_args.model_type}")
        logger.info(f"模型路径: {model_args.model_name_or_path}")
        logger.info(f"数据集路径: {data_args.dataset_path}")
        logger.info(f"使用损失掩码: {model_args.use_loss_mask}")
        logger.info(f"启用原地评估: {eval_args.enable_inplace_eval}")
    
    # 设置W&B
    if training_args.report_to == "wandb" and accelerator.is_main_process:
        wandb.init(
            project=os.environ.get("WANDB_PROJECT", "llama3-8b-accelerate-training"),
            name=f"{model_args.model_type}_sft_accelerate_{training_args.run_name or ''}",
            config={
                "model_type": model_args.model_type,
                "model_path": model_args.model_name_or_path,
                "dataset_path": data_args.dataset_path,
                "use_loss_mask": model_args.use_loss_mask,
                "enable_eval": eval_args.enable_inplace_eval,
                "eval_interval": eval_args.eval_interval,
                "max_seq_length": data_args.max_seq_length,
                "learning_rate": training_args.learning_rate,
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
        )
    
    # 创建数据加载器
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=training_args.per_device_train_batch_size,
        shuffle=True,
        collate_fn=data_collator,
        num_workers=0  # 避免多进程问题
    )
    
    # 设置优化器和学习率调度器
    optimizer = AdamW(
        model.parameters(),
        lr=training_args.learning_rate,
        weight_decay=training_args.weight_decay,
    )
    
    # 计算总训练步数
    num_update_steps_per_epoch = len(train_dataloader) // training_args.gradient_accumulation_steps
    max_train_steps = training_args.num_train_epochs * num_update_steps_per_epoch
    
    lr_scheduler = get_cosine_schedule_with_warmup(
        optimizer=optimizer,
        num_warmup_steps=int(training_args.warmup_ratio * max_train_steps),
        num_training_steps=max_train_steps
    )
    
    # 使用Accelerator准备模型、优化器等
    # model, optimizer, train_dataloader, lr_scheduler = accelerator.prepare(
    #     model, optimizer, train_dataloader, lr_scheduler
    # )
    model, _, train_dataloader, _ = accelerator.prepare(
        model, None, train_dataloader, None
    )
    
    # 初始化评估组件（如果启用）
    evaluator = None
    score_collector = None
    report_generator = None
    test_samples = []
    
    if eval_args.enable_inplace_eval and accelerator.is_main_process:
        logger.info("🔍 初始化评估组件...")
        
        # 加载评估配置
        eval_config = load_evaluation_config("configs/evaluation_config.yaml")
        
        # 初始化评估器
        evaluator = SimpleEvaluator(eval_config)
        
        # 加载测试数据
        if eval_args.eval_test_data_path:
            test_samples = load_test_data(
                eval_args.eval_test_data_path, 
                eval_args.max_eval_samples
            )
            logger.info(f"✓ 加载了 {len(test_samples)} 个测试样本")
        
        # 初始化分数收集器和报告生成器
        reward_server_config = eval_config.get('reward_server', {})
        fallback_config = reward_server_config.get('fallback', {})
        server_url = f"http://{fallback_config.get('host', 'localhost')}:{fallback_config.get('port', 8897)}"
        
        score_collector = ScoreCollector(server_url)
        report_generator = ReportGenerator(eval_args.eval_output_dir)
        
        logger.info("✓ 评估组件初始化完成")
    
    # 训练循环
    logger.info("🎯 开始训练...")
    
    global_step = 0
    total_loss = 0.0
    
    model.train()
    
    for epoch in range(int(training_args.num_train_epochs)):
        if accelerator.is_main_process:
            logger.info(f"\n📊 开始第 {epoch + 1}/{int(training_args.num_train_epochs)} 轮训练")
        
        epoch_loss = 0.0
        progress_bar = tqdm(
            train_dataloader, 
            desc=f"Epoch {epoch + 1}", 
            disable=not accelerator.is_main_process
        )
        
        for step, batch in enumerate(progress_bar):
            with accelerator.accumulate(model):
                outputs = model(**batch)
                loss = outputs.loss
                
                # 反向传播
                accelerator.backward(loss)
                
                # 梯度裁剪
                if training_args.max_grad_norm > 0:
                    accelerator.clip_grad_norm_(model.parameters(), training_args.max_grad_norm)
                
                #optimizer.step()
                #lr_scheduler.step()
                #optimizer.zero_grad()
            
            # 更新统计信息
            loss_item = loss.detach().float()
            total_loss += loss_item
            epoch_loss += loss_item
            
            # 更新进度条
            if accelerator.is_main_process:
                progress_bar.set_postfix({
                    'loss': f"{loss_item:.4f}",
                    # 'lr': f"{lr_scheduler.get_last_lr()[0]:.2e}",
                    'step': global_step
                })
            
            global_step += 1
            
            # 记录日志
            if global_step % training_args.logging_steps == 0:
                avg_loss = total_loss / training_args.logging_steps
                
                if accelerator.is_main_process:
                    log_dict = {
                        "train_loss": avg_loss,
                        # "learning_rate": lr_scheduler.get_last_lr()[0],
                        "epoch": epoch,
                        "global_step": global_step
                    }
                    
                    if training_args.report_to == "wandb":
                        wandb.log(log_dict, step=global_step)
                    
                    logger.info(f"Step {global_step}: loss={avg_loss:.4f}")
                
                total_loss = 0.0
            
            # 原地评估
            if (eval_args.enable_inplace_eval and 
                global_step % eval_args.eval_interval == 0 and 
                global_step > 0 and 
                accelerator.is_main_process and 
                test_samples):
                
                logger.info(f"\n🔍 开始第 {global_step} 步的原地评估...")
                
                try:
                    # 获取原始模型（去除Accelerator包装）
                    unwrapped_model = accelerator.unwrap_model(model)
                    
                    # 执行评估 - 传递accelerator用于DDP主进程推理
                    solutions = evaluator.evaluate_during_training(
                        unwrapped_model, tokenizer, test_samples, eval_args.eval_batch_size, accelerator
                    )
                    
                    if solutions:
                        # 收集分数
                        logger.info("📊 正在计算评估分数...")
                        scores = score_collector.batch_evaluate(
                            test_samples, solutions, batch_size=eval_args.eval_batch_size
                        )
                        
                        # 生成报告
                        checkpoint_info = {
                            'step': global_step,
                            'epoch': epoch,
                            'output_dir': training_args.output_dir
                        }
                        
                        report = report_generator.generate_report(
                            scores, checkpoint_info, test_samples
                        )
                        
                        # 记录评估指标
                        eval_metrics = {
                            "eval_overall_score": report.get('overall_score', 0.0),
                            "eval_success_rate": report.get('success_rate', 0.0),
                            "eval_mean_score": report['evaluation_results'].get('mean_score', 0.0)
                        }
                        
                        if training_args.report_to == "wandb":
                            wandb.log(eval_metrics, step=global_step)
                        
                        logger.info(f"✅ 评估完成:")
                        logger.info(f"  整体分数: {eval_metrics['eval_overall_score']:.2%}")
                        logger.info(f"  成功率: {eval_metrics['eval_success_rate']:.2%}")
                        logger.info(f"  平均分数: {eval_metrics['eval_mean_score']:.3f}")
                    
                except Exception as e:
                    logger.error(f"❌ 评估过程中发生错误: {e}")
                
                logger.info("🎯 恢复训练...")
            
            # 保存检查点
            if (training_args.save_steps and 
                global_step % training_args.save_steps == 0 and 
                global_step > 0):
                
                if accelerator.is_main_process:
                    logger.info(f"💾 保存检查点: step-{global_step}")
                
                checkpoint_dir = Path(training_args.output_dir) / f"checkpoint-{global_step}"
                accelerator.save_state(str(checkpoint_dir))
                
                # 保存模型和tokenizer
                unwrapped_model = accelerator.unwrap_model(model)
                unwrapped_model.save_pretrained(str(checkpoint_dir))
                tokenizer.save_pretrained(str(checkpoint_dir))
                
                # 清理旧检查点
                if training_args.save_total_limit and training_args.save_total_limit > 0:
                    checkpoints = list(Path(training_args.output_dir).glob("checkpoint-*"))
                    checkpoints.sort(key=lambda x: int(x.name.split('-')[1]))
                    
                    while len(checkpoints) > training_args.save_total_limit:
                        old_checkpoint = checkpoints.pop(0)
                        if accelerator.is_main_process:
                            logger.info(f"🗑️ 删除旧检查点: {old_checkpoint}")
                        import shutil
                        shutil.rmtree(old_checkpoint, ignore_errors=True)
    
    # 训练完成，保存最终模型
    if accelerator.is_main_process:
        logger.info("🎉 训练完成！保存最终模型...")
        
        final_output_dir = Path(training_args.output_dir) / "final"
        final_output_dir.mkdir(parents=True, exist_ok=True)
        
        unwrapped_model = accelerator.unwrap_model(model)
        unwrapped_model.save_pretrained(str(final_output_dir))
        tokenizer.save_pretrained(str(final_output_dir))
        
        logger.info(f"✅ 最终模型已保存到: {final_output_dir}")
        
        # 最终评估
        if eval_args.enable_inplace_eval and test_samples:
            logger.info("🔍 执行最终评估...")
            
            try:
                solutions = evaluator.evaluate_during_training(
                    unwrapped_model, tokenizer, test_samples, eval_args.eval_batch_size, accelerator
                )
                
                if solutions:
                    scores = score_collector.batch_evaluate(
                        test_samples, solutions, batch_size=eval_args.eval_batch_size
                    )
                    
                    checkpoint_info = {
                        'step': global_step,
                        'epoch': int(training_args.num_train_epochs),
                        'output_dir': training_args.output_dir,
                        'final': True
                    }
                    
                    final_report = report_generator.generate_report(
                        scores, checkpoint_info, test_samples
                    )
                    
                    logger.info(f"🏁 最终评估结果:")
                    logger.info(f"  整体分数: {final_report.get('overall_score', 0.0):.2%}")
                    logger.info(f"  成功率: {final_report.get('success_rate', 0.0):.2%}")
                    
                    if training_args.report_to == "wandb":
                        wandb.log({
                            "final_eval_overall_score": final_report.get('overall_score', 0.0),
                            "final_eval_success_rate": final_report.get('success_rate', 0.0)
                        }, step=global_step)
                
            except Exception as e:
                logger.error(f"❌ 最终评估失败: {e}")
        
        if training_args.report_to == "wandb":
            wandb.finish()
        
        logger.info("🎊 训练流程全部完成！")

if __name__ == "__main__":
    main()  # 直接调用，不再需要asyncio