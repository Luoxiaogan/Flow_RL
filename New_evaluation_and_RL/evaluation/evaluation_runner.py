#!/usr/bin/env python3
"""
Evaluation Runner - Simple data pipeline for workflow evaluation

This module implements a straightforward data pipeline:
parquet读取 → 模型API → workflow → reward_server

Concurrency control is handled by the API services themselves through rate limiting.
"""

import os
import sys
import json
import yaml
import argparse
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from tqdm import tqdm
import logging
import re

# Setup logging with Chinese output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'evaluation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def clean_numpy_arrays(obj):
    """
    递归清理对象中的numpy数组，转换为Python原生类型
    
    Args:
        obj: 要清理的对象（可能包含numpy数组）
        
    Returns:
        清理后的对象（所有numpy数组转换为list）
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: clean_numpy_arrays(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_numpy_arrays(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(clean_numpy_arrays(item) for item in obj)
    else:
        return obj


class EvaluationRunner:
    """评估执行引擎 - 简单数据管道"""
    
    def __init__(self, config_path: str = "../config.yaml"):
        """
        Initialize evaluation runner
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.setup_endpoints()
        self.session = requests.Session()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"✅ 成功加载配置文件: {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"❌ 无法加载配置文件 {self.config_path}: {e}")
            raise
    
    def setup_endpoints(self):
        """根据config.yaml设置API端点"""
        mode = self.config.get('model', {}).get('mode', 'evaluation_api')
        logger.info(f"📝 模型模式: {mode}")
        
        if mode == "evaluation_api":
            self.model_url = "http://localhost:5010/chat/completions"
            # evaluation_api模式使用固定的模型名称
            self.model_name = "qwen-turbo"  # 或从服务配置中获取
            logger.info(f"🔗 模型端点: {self.model_url} (评估API代理)")
        elif mode == "local":
            port = self.config.get('model', {}).get('local', {}).get('port', 30009)
            self.model_url = f"http://localhost:{port}/v1/chat/completions"
            # 使用配置中的模型路径作为模型名称
            self.model_name = self.config.get('model', {}).get('local', {}).get('model_path', '/nas/models/Qwen2.5-7B-Instruct')
            logger.info(f"🔗 模型端点: {self.model_url} (SGLang本地服务器 - OpenAI兼容模式)")
        else:
            raise ValueError(f"不支持的模型模式: {mode}")
        
        # Reward server endpoint
        reward_config = self.config.get('services', {}).get('scoreflow_reward', {})
        reward_port = reward_config.get('port', 8899)
        self.reward_url = f"http://localhost:{reward_port}/compute_score"
        logger.info(f"🏆 奖励端点: {self.reward_url}")
    
    def call_model_api(self, messages: List[Dict[str, str]]) -> str:
        """
        Call model API to generate workflow code
        
        Args:
            messages: List of messages in OpenAI format
            
        Returns:
            Generated workflow code
        """
        try:
            # 所有模式统一使用OpenAI-compatible API格式
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 8192
            }
            
            logger.debug(f"📤 发送请求到 {self.model_url}")
            logger.debug(f"   模型: {self.model_name}")
            logger.debug(f"   消息数: {len(messages)}")
            
            print(f"📤 发送模型请求到 {self.model_url}")
            
            # Send request (synchronous - let API handle rate limiting)
            response = self.session.post(
                self.model_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300  # 5 minutes timeout
            )
            print(f"📤📤📤response📤📤📤:\n{response}\n")
            
            if response.status_code == 200:
                result = response.json()
                
                # 统一的 OpenAI 响应格式
                workflow_code = result['choices'][0]['message']['content']
                
                logger.debug(f"✅ 成功获取workflow代码 (长度: {len(workflow_code)})")
                return workflow_code
            else:
                error_msg = f"模型API请求失败: {response.status_code} - {response.text}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "模型API请求超时"
            logger.error(f"⏰ {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"模型API调用错误: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def call_reward_api(self, request_data: Dict[str, Any]) -> float:
        """
        Call reward server to compute score
        
        Args:
            request_data: Reward computation request
            
        Returns:
            Computed score
        """
        try:
            logger.debug(f"📤 发送评分请求到 {self.reward_url}")
            
            response = self.session.post(
                self.reward_url,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=600  # 10 minutes timeout for workflow execution
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"📊 评分结果: {result}")
                score = result.get('score', 0.0)
                logger.debug(f"✅ 成功获取评分: {score}")
                return score
            else:
                error_msg = f"评分API请求失败: {response.status_code} - {response.text}"
                logger.error(f"❌ {error_msg}")
                return 0.0
                
        except requests.exceptions.Timeout:
            logger.error("⏰ 评分API请求超时")
            return 0.0
        except Exception as e:
            logger.error(f"❌ 评分API调用错误: {str(e)}")
            return 0.0
    
    def process_single_row(self, row_idx: int, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process single row from parquet file
        
        Args:
            row_idx: Row index for tracking
            row_data: Row data from parquet
            
        Returns:
            Processing result
        """
        try:
            # Extract data from row
            # print(f"raw_data: {row_data}")
            data_source = row_data.get('data_source', 'unknown')
            # print(f"🔄data_source: {data_source}")
            prompt = row_data.get('prompt', [])
            # print(f"🔄prompt: \n{prompt}\n")
            reward_model = row_data.get('reward_model', {})
            # print(f"🔄reward_model: \n{reward_model}\n")
            extra_info = row_data.get('extra_info', {})
            # print(f"🔄extra_info: \n{extra_info}\n")
            
            sample_id = extra_info.get('sample_id', row_idx)
            logger.info(f"🔄 处理样本 {sample_id} (行 {row_idx}) - 数据源: {data_source}")
            
            # Extract messages from prompt (already in correct OpenAI format)
            # prompt contains: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            if isinstance(prompt, list):
                messages = prompt
            elif hasattr(prompt, 'tolist'):  # Handle numpy array case
                messages = prompt.tolist()
            else:
                # Fallback for unexpected format
                logger.warning(f"意外的prompt格式: {type(prompt)}, 内容: {prompt}")
                messages = [{"role": "user", "content": str(prompt)}]
            
            # Step 1: Get workflow code from model
            logger.info(f"📝 发送messages到模型API (共{len(messages)}条消息)...")
            for i, msg in enumerate(messages):
                logger.debug(f"   消息{i+1}: {msg.get('role', 'unknown')} - {msg.get('content', '')[:100]}...")
            
            workflow_code = self.call_model_api(messages)
            # print(f"📤📤📤workflow_code获取成功了!📤📤📤:\n{workflow_code}\n")

            # Extract code from <code></code> tags if present
            code_match = re.search(r'<code>(.*?)</code>', workflow_code, re.DOTALL)
            if code_match:
                extracted_code = code_match.group(1).strip()
                logger.debug(f"✅ 成功提取<code>标签内的代码 (长度: {len(extracted_code)})")
                workflow_code = extracted_code
            else:
                logger.debug("ℹ️ 未找到<code>标签，使用原始workflow_code")
            # print(f"📤📤📤<code>部分获取成功了!📤📤📤:\n{workflow_code}\n")
            
            # Step 2: Clean extra_info to remove numpy arrays before JSON serialization
            print("🧹 清理extra_info中的numpy数组...")
            clean_extra_info = clean_numpy_arrays(extra_info)
            print(f"✅ 已清理extra_info: {clean_extra_info}")
            
            # Step 3: Prepare reward request
            reward_request = {
                "data_source": data_source,
                "solution_str": f"<code>\n{workflow_code}\n</code>",
                "ground_truth": reward_model.get('ground_truth', 'default'),
                "extra_info": clean_extra_info
            }
            
            # Step 4: Get score from reward server
            print(f"🏆 计算评分...")
            score = self.call_reward_api(reward_request)
            
            result = {
                'sample_id': sample_id,
                'row_index': row_idx,
                'data_source': data_source,
                'score': score,
                'workflow_length': len(workflow_code),
                'success': True,
                'error': None,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ 样本 {sample_id}: 得分 {score:.3f}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ 样本 {row_idx} 处理失败: {error_msg}")
            
            result = {
                'sample_id': row_idx,
                'row_index': row_idx,
                'data_source': row_data.get('data_source', 'unknown'),
                'score': 0.0,
                'workflow_length': 0,
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }
            return result
    
    def run_evaluation(self, test_data_path: str, limit: Optional[int] = None, 
                      output_dir: str = "./results") -> Dict[str, Any]:
        """
        Run evaluation on test data
        
        Args:
            test_data_path: Path to test parquet file
            limit: Maximum number of samples to process
            output_dir: Output directory for results
            
        Returns:
            Evaluation summary
        """
        logger.info("=" * 60)
        logger.info("🚀 开始评估")
        logger.info("=" * 60)
        
        # Load test data
        logger.info(f"📊 加载测试数据: {test_data_path}")
        df = pd.read_parquet(test_data_path)
        logger.info(f"📈 总样本数: {len(df)}")
        
        if limit:
            df = df.head(limit)
            logger.info(f"🔢 限制处理样本数: {limit}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Process samples sequentially (let API handle rate limiting)
        results = []
        start_time = datetime.now()
        
        for idx, (_, row) in enumerate(tqdm(df.iterrows(), total=len(df), desc="评估进度")):
            result = self.process_single_row(idx, row.to_dict())
            results.append(result)
            
            # Save intermediate results every 10 samples
            if (idx + 1) % 10 == 0:
                self._save_intermediate_results(results, output_dir, idx + 1)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate statistics
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        if successful_results:
            scores = [r['score'] for r in successful_results]
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
        else:
            avg_score = max_score = min_score = 0.0
        
        summary = {
            'total_samples': len(results),
            'successful_samples': len(successful_results),
            'failed_samples': len(failed_results),
            'success_rate': len(successful_results) / len(results) if results else 0.0,
            'average_score': avg_score,
            'max_score': max_score,
            'min_score': min_score,
            'duration_seconds': duration,
            'samples_per_second': len(results) / duration if duration > 0 else 0.0,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'config': {
                'test_data_path': test_data_path,
                'limit': limit,
                'model_mode': self.config.get('model', {}).get('mode'),
                'model_url': self.model_url
            }
        }
        
        # Save final results
        self._save_final_results(results, summary, output_dir, test_data_path)
        
        # Print summary
        self._print_summary(summary)
        
        return summary
    
    def _save_intermediate_results(self, results: List[Dict], output_dir: str, count: int):
        """Save intermediate results"""
        try:
            intermediate_file = os.path.join(output_dir, f"intermediate_results_{count}.json")
            with open(intermediate_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.debug(f"💾 已保存中间结果: {intermediate_file}")
        except Exception as e:
            logger.warning(f"⚠️ 保存中间结果失败: {e}")
    
    def _save_final_results(self, results: List[Dict], summary: Dict, output_dir: str, test_data_path: str = None):
        """Save final results and summary to organized subfolder structure"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create timestamped subfolder
        session_dir = os.path.join(output_dir, f"evaluation_session_{timestamp}")
        os.makedirs(session_dir, exist_ok=True)
        
        # Save session configuration first
        session_config = {
            "session_info": {
                "timestamp": timestamp,
                "start_time": summary.get('start_time'),
                "end_time": summary.get('end_time'),
                "duration_seconds": summary.get('duration_seconds'),
                "evaluation_version": "1.0"
            },
            "data_source": {
                "test_data_path": test_data_path,
                "total_samples": summary.get('total_samples'),
                "processed_samples": len(results)
            },
            "model_config": {
                "model_mode": summary.get('config', {}).get('model_mode'),
                "model_url": summary.get('config', {}).get('model_url'),
                "reward_url": summary.get('config', {}).get('reward_url')
            },
            "evaluation_stats": {
                "success_rate": summary.get('success_rate'),
                "average_score": summary.get('average_score'),
                "samples_per_second": summary.get('samples_per_second')
            }
        }
        
        config_file = os.path.join(session_dir, "session_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(session_config, f, ensure_ascii=False, indent=2)
        
        # Save detailed results
        results_file = os.path.join(session_dir, "evaluation_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Save summary
        summary_file = os.path.join(session_dir, "evaluation_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # Save CSV for easy analysis
        csv_file = os.path.join(session_dir, "evaluation_results.csv")
        df_results = pd.DataFrame(results)
        df_results.to_csv(csv_file, index=False, encoding='utf-8')
        
        logger.info(f"💾 结果已保存到评估会话目录:")
        logger.info(f"   📁 会话目录: {session_dir}")
        logger.info(f"   ⚙️  会话配置: {config_file}")
        logger.info(f"   📊 详细结果: {results_file}")
        logger.info(f"   📋 评估摘要: {summary_file}")
        logger.info(f"   📈 CSV格式: {csv_file}")
    
    def _print_summary(self, summary: Dict):
        """Print evaluation summary"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 评估结果摘要")
        logger.info("=" * 60)
        logger.info(f"总样本数: {summary['total_samples']}")
        logger.info(f"成功样本: {summary['successful_samples']}")
        logger.info(f"失败样本: {summary['failed_samples']}")
        logger.info(f"成功率: {summary['success_rate']:.1%}")
        logger.info(f"平均得分: {summary['average_score']:.3f}")
        logger.info(f"最高得分: {summary['max_score']:.3f}")
        logger.info(f"最低得分: {summary['min_score']:.3f}")
        logger.info(f"总耗时: {summary['duration_seconds']:.1f}秒")
        logger.info(f"处理速度: {summary['samples_per_second']:.2f}样本/秒")
        logger.info("=" * 60)


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="评估系统 - 简单数据管道")
    parser.add_argument("--test-data", default="../Test_FILE/verl_support/data/gsm8k/test.parquet",
                       help="测试数据parquet文件路径")
    parser.add_argument("--config", default="../config.yaml",
                       help="配置文件路径")
    parser.add_argument("--limit", type=int, default=None,
                       help="限制处理的样本数量")
    parser.add_argument("--output-dir", default="./results",
                       help="结果输出目录")
    parser.add_argument("--verbose", action="store_true",
                       help="显示详细日志")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🎯 评估系统启动")
    print(f"配置文件: {args.config}")
    print(f"测试数据: {args.test_data}")
    if args.limit:
        print(f"样本限制: {args.limit}")
    print()
    
    try:
        # Initialize runner
        runner = EvaluationRunner(args.config)
        
        # Check if test data exists
        if not os.path.exists(args.test_data):
            logger.error(f"❌ 测试数据文件不存在: {args.test_data}")
            sys.exit(1)
        
        # Determine output directory: use config if args.output_dir is default
        if args.output_dir == "./results":
            # Use config output_dir if command line argument wasn't explicitly set
            config_output_dir = runner.config.get('evaluation', {}).get('output_dir', './results')
            output_dir = config_output_dir
        else:
            output_dir = args.output_dir
        
        logger.info(f"📂 输出目录: {output_dir}")
        
        # Run evaluation
        summary = runner.run_evaluation(
            test_data_path=args.test_data,
            limit=args.limit,
            output_dir=output_dir
        )
        
        print(f"\n🎉 评估完成！成功率: {summary['success_rate']:.1%}")
        
    except KeyboardInterrupt:
        logger.info("\n⏸️ 用户中断评估")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ 评估失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()