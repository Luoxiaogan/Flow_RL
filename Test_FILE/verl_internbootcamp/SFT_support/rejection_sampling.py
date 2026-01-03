"""
拒绝采样（Rejection Sampling）数据生成器
用于InternBootcamp数据集的SFT训练数据准备
"""
import os
import sys
import json
import asyncio
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import aiohttp
import time

# 添加必要的路径
CURRENT_DIR = Path(__file__).parent
PARENT_DIR = CURRENT_DIR.parent
PROJECT_ROOT = PARENT_DIR.parent.parent
sys.path.append(str(PARENT_DIR))
sys.path.append(str(PROJECT_ROOT))

# 导入必要的模块
from internbootcamp_reward import InternBootcampRewardCalculator

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RejectionSampler:
    """拒绝采样器：生成多个响应并选择最佳的"""
    
    def __init__(self, config_path: Optional[str] = None, debug_mode: bool = False):
        """初始化采样器"""
        # 加载配置
        if config_path is None:
            config_path = PARENT_DIR / "config.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # LLM配置
        self.llm_config = self.config['llm_config']['upstream']
        
        # 采样配置
        self.sampling_config = {
            'num_samples': 8,  # 每个prompt采样8次
            'reward_threshold': 0.5,  # reward阈值
            'max_concurrent_api_calls': 5,  # 最大并发API调用数
            'timeout': 60,  # API调用超时时间
        }
        
        # Debug模式
        self.debug_mode = debug_mode
        
        # 初始化reward计算器
        self.reward_calculator = InternBootcampRewardCalculator(config_path)
        
        # 统计信息
        self.stats = {
            'total_prompts': 0,
            'successful_prompts': 0,
            'failed_prompts': 0,
            'total_api_calls': 0,
            'avg_reward': 0.0,
            'above_threshold': 0
        }
        
        logger.info(f"RejectionSampler initialized (debug_mode={debug_mode})")
    
    def load_verl_data(self, data_path: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """加载VERL格式的数据"""
        logger.info(f"Loading VERL data from {data_path}")
        
        # 根据文件扩展名选择加载方式
        if data_path.endswith('.parquet'):
            df = pd.read_parquet(data_path)
        elif data_path.endswith('.json'):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported file format: {data_path}")
        
        # 限制数据量（用于测试）
        if limit:
            df = df.head(limit)
            logger.info(f"Limited to {limit} entries for testing")
        
        # 转换为字典列表
        entries = []
        for idx, row in df.iterrows():
            entry = row.to_dict()
            
            # 解析JSON字符串字段
            if isinstance(entry.get('prompt'), str):
                try:
                    entry['prompt'] = json.loads(entry['prompt'])
                except:
                    pass
            
            if isinstance(entry.get('extra_info'), str):
                try:
                    entry['extra_info'] = json.loads(entry['extra_info'])
                except:
                    pass
            
            entries.append(entry)
        
        logger.info(f"Loaded {len(entries)} entries")
        return entries
    
    async def call_llm_api(self, messages: List[Dict[str, str]], session: aiohttp.ClientSession) -> Optional[str]:
        """调用LLM API生成响应"""
        url = self.llm_config['base_url'].rstrip('/') + '/chat/completions'
        headers = {
            'Authorization': f"Bearer {self.llm_config['api_key']}",
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.llm_config['model'],
            'messages': messages,
            'temperature': self.llm_config.get('temperature', 0.7),
            'max_tokens': 4096
        }
        
        try:
            async with session.post(url, json=data, headers=headers, 
                                  timeout=aiohttp.ClientTimeout(total=self.sampling_config['timeout'])) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    logger.error(f"API call failed with status {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error("API call timed out")
            return None
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return None
    
    async def generate_responses(self, messages: List[Dict[str, str]], num_samples: int) -> List[str]:
        """为一个prompt生成多个响应"""
        responses = []
        
        async with aiohttp.ClientSession() as session:
            # 创建并发任务
            tasks = []
            for i in range(num_samples):
                task = self.call_llm_api(messages, session)
                tasks.append(task)
                
                # 限制并发数
                if len(tasks) >= self.sampling_config['max_concurrent_api_calls']:
                    batch_responses = await asyncio.gather(*tasks)
                    responses.extend([r for r in batch_responses if r is not None])
                    tasks = []
                    # 短暂延迟避免过快调用
                    await asyncio.sleep(0.1)
            
            # 处理剩余的任务
            if tasks:
                batch_responses = await asyncio.gather(*tasks)
                responses.extend([r for r in batch_responses if r is not None])
        
        self.stats['total_api_calls'] += num_samples
        logger.info(f"Generated {len(responses)} responses out of {num_samples} attempts")
        return responses
    
    async def compute_rewards(self, responses: List[str], extra_info: Dict[str, Any]) -> List[Tuple[str, float]]:
        """计算每个响应的reward分数"""
        results = []
        
        for i, response in enumerate(responses):
            try:
                # 提取workflow代码
                workflow_code = self.reward_calculator.extract_workflow_from_response(response)
                if not workflow_code:
                    logger.warning(f"Sample {i+1}: No workflow code found in response")
                    results.append((response, 0.0))
                    continue
                
                # 获取任务信息
                task_name = extra_info.get('task_name', '')
                test_cases = extra_info.get('test_cases', [])
                
                if not task_name:
                    logger.error("No task_name in extra_info")
                    results.append((response, 0.0))
                    continue
                
                # 计算reward
                reward = await self.reward_calculator.compute_reward_async(
                    workflow_code, task_name, test_cases
                )
                results.append((response, reward))
                logger.debug(f"Sample {i+1}: Computed reward: {reward:.3f}")
                
            except Exception as e:
                logger.error(f"Sample {i+1}: Error computing reward: {e}")
                results.append((response, 0.0))
        
        return results
    
    def save_single_result(self, result: Dict[str, Any], output_path: str):
        """立即保存单个结果到JSONL文件"""
        with open(output_path, 'a', encoding='utf-8') as f:
            json_line = json.dumps(result, ensure_ascii=False)
            f.write(json_line + '\n')
            f.flush()  # 立即刷新缓冲区，确保写入磁盘
    
    async def process_single_prompt(self, entry: Dict[str, Any], output_path: str) -> Optional[Dict[str, Any]]:
        """处理单个prompt的拒绝采样"""
        self.stats['total_prompts'] += 1
        
        # 执行轨迹记录
        execution_trace = {
            'start_time': datetime.now().isoformat(),
            'steps': [],
            'errors': []
        }
        
        try:
            # 获取prompt和相关信息
            messages = entry.get('prompt', [])
            extra_info = entry.get('extra_info', {})
            
            if not messages:
                logger.error("No prompt messages found")
                self.stats['failed_prompts'] += 1
                execution_trace['errors'].append("No prompt messages found")
                return None
            
            # 记录开始生成响应
            execution_trace['steps'].append({
                'step': 'start_generation',
                'timestamp': datetime.now().isoformat(),
                'num_samples': self.sampling_config['num_samples']
            })
            
            # 生成多个响应
            start_time = time.time()
            responses = await self.generate_responses(messages, self.sampling_config['num_samples'])
            
            execution_trace['steps'].append({
                'step': 'generation_complete',
                'timestamp': datetime.now().isoformat(),
                'num_responses': len(responses),
                'generation_time': time.time() - start_time
            })
            
            if not responses:
                logger.error("Failed to generate any responses")
                self.stats['failed_prompts'] += 1
                execution_trace['errors'].append("Failed to generate any responses")
                return None
            
            # 记录开始计算reward
            execution_trace['steps'].append({
                'step': 'start_reward_computation',
                'timestamp': datetime.now().isoformat()
            })
            
            # 计算每个响应的reward
            response_rewards = await self.compute_rewards(responses, extra_info)
            
            execution_trace['steps'].append({
                'step': 'reward_computation_complete',
                'timestamp': datetime.now().isoformat(),
                'rewards': [reward for _, reward in response_rewards]
            })
            
            # 过滤超过阈值的响应
            valid_responses = [
                (resp, reward) for resp, reward in response_rewards 
                if reward >= self.sampling_config['reward_threshold']
            ]
            
            if not valid_responses:
                logger.warning(f"No responses above threshold {self.sampling_config['reward_threshold']}")
                # 如果没有超过阈值的，选择reward最高的
                best_response, best_reward = max(response_rewards, key=lambda x: x[1])
                execution_trace['steps'].append({
                    'step': 'selection_fallback',
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'no_responses_above_threshold'
                })
            else:
                # 选择reward最高的
                best_response, best_reward = max(valid_responses, key=lambda x: x[1])
                self.stats['above_threshold'] += 1
                execution_trace['steps'].append({
                    'step': 'selection_success',
                    'timestamp': datetime.now().isoformat(),
                    'num_valid_responses': len(valid_responses)
                })
            
            # 更新统计
            self.stats['successful_prompts'] += 1
            self.stats['avg_reward'] = (
                (self.stats['avg_reward'] * (self.stats['successful_prompts'] - 1) + best_reward) 
                / self.stats['successful_prompts']
            )
            
            # 构建结果
            result = {
                'prompt': messages,  # 保持原始格式
                'response': best_response,
                'reward': best_reward,
                'task_name': extra_info.get('task_name', 'unknown'),
                'attempts': len(responses),
                'generation_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat(),
                'data_source': entry.get('data_source', 'internbootcamp'),
                'above_threshold': best_reward >= self.sampling_config['reward_threshold']
            }
            
            # 在debug模式下添加执行轨迹
            if self.debug_mode:
                result['execution_trace'] = execution_trace
                result['all_responses'] = responses
                result['all_rewards'] = [reward for _, reward in response_rewards]
            
            # 立即保存结果
            self.save_single_result(result, output_path)
            
            logger.info(f"Processed prompt: task={result['task_name']}, "
                       f"best_reward={best_reward:.3f}, attempts={len(responses)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing prompt: {e}")
            self.stats['failed_prompts'] += 1
            execution_trace['errors'].append(str(e))
            
            # 在debug模式下保存错误信息
            if self.debug_mode:
                error_result = {
                    'prompt': entry.get('prompt', []),
                    'response': None,
                    'reward': 0.0,
                    'task_name': entry.get('extra_info', {}).get('task_name', 'unknown'),
                    'attempts': 0,
                    'generation_time': 0.0,
                    'timestamp': datetime.now().isoformat(),
                    'data_source': entry.get('data_source', 'internbootcamp'),
                    'above_threshold': False,
                    'execution_trace': execution_trace,
                    'error': str(e)
                }
                self.save_single_result(error_result, output_path)
            
            return None
    
    async def process_dataset(self, entries: List[Dict[str, Any]], 
                            output_path: str, batch_size: int = 5) -> None:
        """处理整个数据集"""
        logger.info(f"Processing {len(entries)} entries in batches of {batch_size}")
        
        # 确保输出文件存在（如果不存在则创建）
        if not os.path.exists(output_path):
            with open(output_path, 'w', encoding='utf-8') as f:
                pass  # 创建空文件
        
        # 分批处理
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(entries) + batch_size - 1)//batch_size}")
            
            # 并发处理batch中的prompts
            tasks = [self.process_single_prompt(entry, output_path) for entry in batch]
            batch_results = await asyncio.gather(*tasks)
            
            # 短暂延迟
            await asyncio.sleep(0.5)
        
        # 打印统计信息
        self.print_stats()
    
    def save_results(self, results: List[Dict[str, Any]], output_path: str, append: bool = False):
        """保存结果为JSONL格式（保留原有方法以兼容性）"""
        mode = 'a' if append else 'w'
        
        with open(output_path, mode, encoding='utf-8') as f:
            for result in results:
                # 转换为JSON行
                json_line = json.dumps(result, ensure_ascii=False)
                f.write(json_line + '\n')
        
        logger.info(f"Saved {len(results)} results to {output_path}")
    
    def print_stats(self):
        """打印统计信息"""
        logger.info("\n" + "="*50)
        logger.info("REJECTION SAMPLING STATISTICS")
        logger.info("="*50)
        logger.info(f"Total prompts processed: {self.stats['total_prompts']}")
        logger.info(f"Successful: {self.stats['successful_prompts']}")
        logger.info(f"Failed: {self.stats['failed_prompts']}")
        logger.info(f"Total API calls: {self.stats['total_api_calls']}")
        logger.info(f"Average reward: {self.stats['avg_reward']:.3f}")
        logger.info(f"Above threshold: {self.stats['above_threshold']}")
        logger.info(f"Success rate: {self.stats['successful_prompts'] / max(1, self.stats['total_prompts']) * 100:.1f}%")
        logger.info(f"Debug mode: {self.debug_mode}")
        logger.info("="*50)


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rejection Sampling for InternBootcamp SFT')
    parser.add_argument('--input', default='../flexible_all/train.parquet',
                       help='Input VERL data file (parquet or json)')
    parser.add_argument('--output', default='./output/rejection_sampled.jsonl',
                       help='Output JSONL file')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of entries to process (for testing)')
    parser.add_argument('--batch-size', type=int, default=5,
                       help='Batch size for processing')
    parser.add_argument('--config', default=None,
                       help='Config file path')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode to include execution traces')
    
    args = parser.parse_args()
    
    # 创建输出目录
    output_dir = Path(args.output).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建采样器
    sampler = RejectionSampler(args.config, debug_mode=args.debug)
    
    # 加载数据
    entries = sampler.load_verl_data(args.input, limit=args.limit)
    
    if not entries:
        logger.error("No data loaded")
        return
    
    # 处理数据集
    await sampler.process_dataset(entries, args.output, batch_size=args.batch_size)
    
    logger.info(f"Processing completed. Results saved to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())