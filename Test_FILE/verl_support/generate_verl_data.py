"""
VERL格式数据生成器 - 严格复用现有系统逻辑
"""
import os
import sys
import json
import logging
import argparse
import pandas as pd
from typing import Dict, List, Any
from utils import (
    get_benchmark_handler,
    create_train_test_split,
    construct_generation_prompt,
    format_chat_template,
    load_config,
    ensure_dir_exists
)

class VerlDataGenerator:
    """
    VERL数据生成器
    核心原则：完全复用现有系统的方法
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.benchmarks = config['benchmarks']
        self.generation_config = config['generation_config']
        self.verl_config = config['verl_config']
        self.output_paths = config['output_paths']
        
        # 确保输出目录存在
        ensure_dir_exists(self.output_paths['data_dir'])
        ensure_dir_exists(self.output_paths['temp_workspace'])
        
        logging.info("VerlDataGenerator 初始化完成")

    def generate_training_prompts(self, benchmark_name: str) -> List[Dict[str, Any]]:
        """
        生成训练数据的prompts
        严格按照 workflow_generator.py 的逻辑
        """
        benchmark_config = self.benchmarks[benchmark_name]
        dataset_path = benchmark_config['dataset_path']
        total_problems = benchmark_config['total_problems']
        train_ratio = benchmark_config['train_ratio']
        ability = benchmark_config['ability']
        
        logging.info(f"开始为 {benchmark_name} 生成训练prompts...")
        
        # 1. 严格按照 workflow_generator.py 初始化Handler
        handler = get_benchmark_handler(benchmark_name, dataset_path)
        
        # 2. 按照 master_runner.py 的逻辑分割训练/测试集
        train_tasks, test_indices = create_train_test_split(
            total_problems=total_problems,
            train_ratio=train_ratio,
            min_sample=self.generation_config['min_sample_size'],
            max_sample=self.generation_config['max_sample_size']
        )
        
        # 限制生成数量（避免过多数据）
        max_train_samples = self.verl_config['train_samples_per_benchmark']
        if len(train_tasks) > max_train_samples:
            train_tasks = train_tasks[:max_train_samples]
            
        # 3. 为每个训练任务生成VERL格式数据
        verl_training_data = []
        for i, data_indices in enumerate(train_tasks):
            try:
                # 复用 workflow_generator.py 的 _construct_generation_prompt
                messages, problem_text = construct_generation_prompt(
                    handler, data_indices, benchmark_name
                )
                
                # 格式化为HuggingFace chat_template格式
                # formatted_prompt = format_chat_template(messages)
                
                # 构建VERL格式记录
                verl_record = {
                    'data_source': benchmark_name,
                    'prompt': messages,
                    'ability': ability,
                    'reward_model': {
                        'ground_truth': data_indices  # 存储用于生成的问题索引
                    },
                    'extra_info': {
                        'sample_id': i,
                        'num_problems': len(data_indices),
                        'problem_indices': data_indices,
                        'raw_problem_text': problem_text[:500]  # 截断保存原始问题文本片段
                    }
                }
                
                verl_training_data.append(verl_record)
                
            except Exception as e:
                logging.error(f"生成训练样本 {i} 时出错: {e}")
                continue
        
        logging.info(f"{benchmark_name} 训练数据生成完成: {len(verl_training_data)} 条记录")
        
        # 保存测试集索引用于后续reward计算
        self._save_test_indices(benchmark_name, test_indices)
        
        return verl_training_data
    
    def _save_test_indices(self, benchmark_name: str, test_indices: List[int]):
        """生成测试数据，格式与训练数据完全一致，使用config控制数量，确保与训练集不重合"""
        benchmark_config = self.benchmarks[benchmark_name]
        ability = benchmark_config['ability']
        
        # 使用config控制测试样本数量
        max_test_samples = self.verl_config['test_samples_per_benchmark']
        if len(test_indices) > max_test_samples:
            test_indices = test_indices[:max_test_samples]
        
        # 获取benchmark handler
        handler = get_benchmark_handler(benchmark_name, benchmark_config['dataset_path'])
        
        test_data = []
        for i, test_idx in enumerate(test_indices):
            try:
                # 使用单个问题索引生成prompt（和train数据格式保持一致）
                data_indices = [test_idx]  # 包装成列表格式
                
                # 复用 workflow_generator.py 的 _construct_generation_prompt
                messages, problem_text = construct_generation_prompt(
                    handler, data_indices, benchmark_name
                )
                
                # 格式化为HuggingFace chat_template格式
                formatted_prompt = format_chat_template(messages)
                
                # 构建VERL格式记录（与训练数据完全一致的格式）
                test_record = {
                    'data_source': benchmark_name,
                    'prompt': messages,
                    'ability': ability,
                    'reward_model': {
                        'ground_truth': data_indices  # 存储用于生成的问题索引
                    },
                    'extra_info': {
                        'sample_id': i,
                        'num_problems': len(data_indices),
                        'problem_indices': data_indices,
                        'raw_problem_text': problem_text[:500]  # 截断保存原始问题文本片段
                    }
                }
                
                test_data.append(test_record)
                
            except Exception as e:
                logging.error(f"生成测试样本 {i} 时出错: {e}")
                continue
        
        # 保存为parquet文件
        test_df = pd.DataFrame(test_data)
        test_output_path = os.path.join(
            self.output_paths['data_dir'], 
            f"{benchmark_name}_verl_test.parquet"
        )
        test_df.to_parquet(test_output_path, index=False)
        logging.info(f"{benchmark_name} 测试数据已保存: {test_output_path} ({len(test_data)} 条记录)")
        
        # 打印测试数据统计
        if test_data:
            logging.info(f"测试数据统计 - 样本数: {len(test_df)}, 平均prompt长度: {test_df['prompt'].str.len().mean():.0f} 字符")

    def generate_all_benchmarks(self):
        """为所有配置的benchmark生成VERL数据"""
        for benchmark_name in self.benchmarks.keys():
            try:
                logging.info(f"\n开始处理 benchmark: {benchmark_name}")
                
                # 生成训练数据
                training_data = self.generate_training_prompts(benchmark_name)
                
                if training_data:
                    # 转换为DataFrame并保存
                    train_df = pd.DataFrame(training_data)
                    train_output_path = os.path.join(
                        self.output_paths['data_dir'],
                        f"{benchmark_name}_verl_train.parquet"
                    )
                    train_df.to_parquet(train_output_path, index=False)
                    logging.info(f"{benchmark_name} 训练数据已保存: {train_output_path}")
                    
                    # 打印样本统计
                    self._print_data_statistics(benchmark_name, train_df)
                    
            except Exception as e:
                logging.error(f"处理 benchmark {benchmark_name} 时发生错误: {e}")
                continue
                
        logging.info("\n所有 benchmark 的 VERL 数据生成完成！")

    def _print_data_statistics(self, benchmark_name: str, df: pd.DataFrame):
        """打印数据统计信息"""
        logging.info(f"\n=== {benchmark_name} 数据统计 ===")
        logging.info(f"训练样本数: {len(df)}")
        logging.info(f"能力类别: {df['ability'].iloc[0]}")
        logging.info(f"平均prompt长度: {df['prompt'].str.len().mean():.0f} 字符")
        
        # 统计问题数量分布
        problem_counts = [len(record['ground_truth']) for record in df['reward_model']]
        logging.info(f"每个prompt包含问题数: 最小{min(problem_counts)}, 最大{max(problem_counts)}, 平均{sum(problem_counts)/len(problem_counts):.1f}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='VERL格式数据生成器')
    parser.add_argument('--config', type=str, default='config.json', help='配置文件路径')
    parser.add_argument('--benchmark', type=str, help='指定单个benchmark进行生成')
    parser.add_argument('--log-level', type=str, default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='日志级别')
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    # 设置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 加载配置
        config = load_config(args.config)
        
        # 创建生成器
        generator = VerlDataGenerator(config)
        
        if args.benchmark:
            # 生成指定benchmark
            if args.benchmark in config['benchmarks']:
                logging.info(f"指定生成benchmark: {args.benchmark}")
                training_data = generator.generate_training_prompts(args.benchmark)
                
                if training_data:
                    train_df = pd.DataFrame(training_data)
                    train_output_path = os.path.join(
                        config['output_paths']['data_dir'],
                        f"{args.benchmark}_verl_train.parquet"
                    )
                    train_df.to_parquet(train_output_path, index=False)
                    generator._print_data_statistics(args.benchmark, train_df)
            else:
                logging.error(f"未找到benchmark配置: {args.benchmark}")
        else:
            # 生成所有benchmark
            generator.generate_all_benchmarks()
            
    except Exception as e:
        logging.error(f"程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 