#!/usr/bin/env python3
"""
智能读取evaluation_config.yaml并分析训练信息
供run_finetune_with_inplace_eval.sh使用
"""
import yaml
import sys
import os
import json
import argparse
from pathlib import Path

def get_project_root():
    """从root.yaml获取项目根路径"""
    try:
        script_dir = Path(__file__).parent
        root_config_path = script_dir / "configs" / "root.yaml"
        
        with open(root_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config.get('root', '/nas/ganluo/Flow_RL')
    except Exception:
        return '/nas/ganluo/Flow_RL'  # 默认使用服务器路径

def count_jsonl_lines(filepath):
    """计算JSONL文件的行数"""
    try:
        if not os.path.exists(filepath):
            return None
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            for _ in f:
                count += 1
        return count
    except Exception:
        return None

def read_eval_config_smart(args):
    """智能读取评估配置文件并分析训练信息"""
    project_root = get_project_root()
    default_test_path = os.path.join(project_root, 'New_evaluation_and_RL/parquet_and_jsonl_data/single/test.jsonl')
    
    try:
        # 读取评估配置文件
        with open(args.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 提取schedule配置
        schedule = config.get('schedule', {})
        interval = schedule.get('interval', 50)
        batch_size = schedule.get('batch_size', 4)
        max_samples = schedule.get('max_samples', 20)
        
        # 提取测试数据路径（如果是相对路径，转换为绝对路径）
        test_data = config.get('test_data', {})
        test_path = test_data.get('path', default_test_path)
        
        # 如果路径不是绝对路径，则相对于项目根目录
        if test_path and not os.path.isabs(test_path):
            test_path = os.path.join(project_root, test_path)
        
        # 输出基本配置（shell变量格式）
        print(f'EVAL_INTERVAL={interval}')
        print(f'EVAL_BATCH_SIZE={batch_size}')
        print(f'MAX_EVAL_SAMPLES={max_samples if max_samples is not None else ""}')
        print(f'EVAL_TEST_DATA="{test_path}"')
        
        # 如果提供了训练参数，进行智能分析
        if args.dataset and args.batch_size and args.grad_accum and args.num_gpus and args.epochs:
            # 计算训练样本数
            train_samples = count_jsonl_lines(args.dataset)
            if train_samples:
                # 计算全局批次大小
                global_batch_size = int(args.batch_size) * int(args.grad_accum) * int(args.num_gpus)
                
                # 计算每轮步数
                steps_per_epoch = train_samples // global_batch_size
                
                # 计算总步数
                total_steps = steps_per_epoch * int(args.epochs)
                
                # 计算预期评估次数
                expected_eval_count = total_steps // interval
                
                # 输出智能分析结果
                print(f'TOTAL_TRAIN_SAMPLES={train_samples}')
                print(f'GLOBAL_BATCH_SIZE={global_batch_size}')
                print(f'STEPS_PER_EPOCH={steps_per_epoch}')
                print(f'TOTAL_STEPS={total_steps}')
                print(f'EXPECTED_EVAL_COUNT={expected_eval_count}')
                
                # 如果有测试数据路径，也计算测试样本数
                if test_path and os.path.exists(test_path):
                    test_samples = count_jsonl_lines(test_path)
                    if test_samples:
                        print(f'TOTAL_TEST_SAMPLES={test_samples}')
                        
                        # 如果设置了max_samples，计算实际评估样本数
                        if max_samples:
                            actual_eval_samples = min(max_samples, test_samples)
                            print(f'ACTUAL_EVAL_SAMPLES={actual_eval_samples}')
                            
                            # 计算每次评估的时间估计（批次数）
                            eval_batches = (actual_eval_samples + batch_size - 1) // batch_size
                            print(f'EVAL_BATCHES_PER_RUN={eval_batches}')
        
        return 0
        
    except FileNotFoundError:
        sys.stderr.write(f"# 配置文件未找到: {args.config_path}\n")
        # 输出默认值
        print('EVAL_INTERVAL=50')
        print('EVAL_BATCH_SIZE=4')
        print('MAX_EVAL_SAMPLES=20')
        print(f'EVAL_TEST_DATA="{default_test_path}"')
        return 1
        
    except Exception as e:
        sys.stderr.write(f"# 读取配置出错: {e}\n")
        # 输出默认值
        print('EVAL_INTERVAL=50')
        print('EVAL_BATCH_SIZE=4')
        print('MAX_EVAL_SAMPLES=20')
        print(f'EVAL_TEST_DATA="{default_test_path}"')
        return 1

def main():
    parser = argparse.ArgumentParser(description='智能读取评估配置')
    parser.add_argument('config_path', help='evaluation_config.yaml路径')
    parser.add_argument('--dataset', help='训练数据集路径')
    parser.add_argument('--batch-size', type=int, help='每设备批次大小')
    parser.add_argument('--grad-accum', type=int, help='梯度累积步数')
    parser.add_argument('--num-gpus', type=int, help='GPU数量')
    parser.add_argument('--epochs', type=int, help='训练轮数')
    
    args = parser.parse_args()
    exit_code = read_eval_config_smart(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()