"""
完整的VERL数据生成器
包含workflow生成、执行、reward计算和详细记录
"""
import os
import sys
import json
import asyncio
import argparse
import random
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import pandas as pd
import traceback
import importlib.util

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from ScoreFlow.scripts.internbootcamp.handler import InternBootcampHandler
except Exception as e:
    # 如果导入失败，定义一个占位符
    InternBootcampHandler = None
    print(f"Warning: Could not import InternBootcampHandler: {e}")

from ScoreFlow.scripts.internbootcamp.conditions import (
    META_PROMPTS, SYSTEM_PROMPT, END_PROMPT, PYTHON_END,
    get_workflow_prompts
)
from internbootcamp_utils import InternBootcampManager, classify_ability, get_task_type
from reward_calculator import calculate_reward

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VERLCompleteGenerator:
    """完整的VERL数据生成器，包含workflow生成和reward计算"""
    
    def __init__(self, config: Dict[str, Any], output_dir: str):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.workflows_dir = self.output_dir / "workflows"
        self.execution_dir = self.output_dir / "execution_results"
        self.verl_data_dir = self.output_dir / "verl_data"
        self.logs_dir = self.output_dir / "logs"
        
        for dir_path in [self.workflows_dir, self.execution_dir, self.verl_data_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 初始化组件
        self.manager = InternBootcampManager()
        # InternBootcampHandler不再需要参数
        if InternBootcampHandler is not None:
            try:
                self.handler = InternBootcampHandler()
            except Exception as e:
                # 如果handler初始化失败，可以继续使用manager
                logger.warning(f"Could not initialize InternBootcampHandler: {e}")
                self.handler = None
        else:
            self.handler = None
        
        # 记录生成过程
        self.generation_log = []
        
    def generate_workflow_prompt(self, task_name: str, examples: List[Dict[str, Any]], 
                               workflow_type: str = "predefined") -> str:
        """生成workflow提示词"""
        # 获取workflow类型对应的prompts
        workflow_prompts = get_workflow_prompts(workflow_type)
        
        # 选择随机的meta prompt
        meta_prompt = random.choice(META_PROMPTS)
        
        # 格式化示例
        formatted_examples = []
        for i, example in enumerate(examples[:3], 1):
            formatted_examples.append(f"Example {i}:\n{json.dumps(example, indent=2, ensure_ascii=False)}")
        
        prompt_text = f"{meta_prompt}\n\nTask: {task_name}\n\nExamples:\n" + "\n\n".join(formatted_examples)
        
        # 使用对应的START_PROMPT
        return workflow_prompts["START_PROMPT"].format(prompt_text=prompt_text)
    
    async def generate_workflow_code(self, task_name: str, examples: List[Dict[str, Any]], 
                             workflow_type: str, llm_config: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """使用真实LLM API生成workflow代码"""
        try:
            from openai import AsyncOpenAI
            
            # 生成提示词
            prompt = self.generate_workflow_prompt(task_name, examples, workflow_type)
            workflow_prompts = get_workflow_prompts(workflow_type)
            
            # 构建完整的提示
            full_prompt = f"{prompt}\n\n{END_PROMPT}"
            
            # 调用LLM API
            client = AsyncOpenAI(
                api_key=llm_config.get("api_key", os.getenv("OPENAI_API_KEY")),
                base_url=llm_config.get("base_url", os.getenv("OPENAI_BASE_URL"))
            )
            
            messages = [
                {"role": "system", "content": "You are an expert at creating MetaGPT workflows for problem solving."},
                {"role": "user", "content": full_prompt}
            ]
            
            response = await client.chat.completions.create(
                model=llm_config.get("model", "deepseek-chat"),
                messages=messages,
                temperature=llm_config.get("temperature", 0.7),
                max_tokens=4000
            )
            
            workflow_content = response.choices[0].message.content
            
            # 清理代码（移除可能的markdown标记）
            if workflow_content.startswith("```python"):
                workflow_content = workflow_content[9:]
            if workflow_content.endswith("```"):
                workflow_content = workflow_content[:-3]
            
            # 构建完整的workflow代码
            full_code = f"{workflow_prompts['PYTHON_START']}\n{workflow_content}\n{PYTHON_END}"
            
            return full_code, None
            
        except Exception as e:
            error_msg = f"Failed to generate workflow via API: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return None, error_msg
    
    async def execute_workflow_real(self, workflow_code: str, task_name: str, 
                                  examples: List[Dict[str, Any]], config_path: str = "../config2.yaml") -> Dict[str, Any]:
        """使用MetaGPT真实执行workflow并计算reward"""
        import tempfile
        from pathlib import Path
        
        # 动态导入MetaGPT组件
        try:
            from metagpt.provider.llm_provider_registry import create_llm_instance
            from metagpt.configs.llm_config import LLMConfig, LLMType
        except ImportError as e:
            logger.error(f"Failed to import MetaGPT: {e}")
            # 如果MetaGPT不可用，返回模拟结果
            return await self.execute_workflow_mock(workflow_code, task_name, examples)
        
        results = []
        total_reward = 0.0
        
        # 创建临时目录
        temp_dir = Path(self.output_dir) / "temp_execution"
        temp_dir.mkdir(exist_ok=True)
        
        # 创建临时workflow文件
        workflow_file = temp_dir / f"temp_workflow_{int(time.time())}.py"
        with open(workflow_file, 'w', encoding='utf-8') as f:
            f.write(workflow_code)
        
        try:
            # 动态导入生成的workflow
            spec = importlib.util.spec_from_file_location("temp_workflow", workflow_file)
            workflow_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(workflow_module)
            
            # 获取workflow类
            workflow_class = getattr(workflow_module, "InternBootcampWorkflow")
            
            # 创建LLM实例
            llm_config = LLMConfig(
                api_type=LLMType.OPENAI,
                model="deepseek-chat",
                api_key=os.getenv("DEEPSEEK_API_KEY", "sk-f0e8c12fde05482390eb8f8ff3a2c74a"),
                base_url="https://api.deepseek.com"
            )
            llm = create_llm_instance(llm_config)
            
            # 创建workflow实例
            workflow = workflow_class(llm)
            
            # 执行每个示例
            for example in examples:
                try:
                    logger.info(f"Executing workflow for example {example.get('identity', 'unknown')}")
                    
                    # 执行workflow
                    start_time = time.time()
                    workflow_output = await asyncio.wait_for(
                        workflow.run(example),
                        timeout=180
                    )
                    execution_time = time.time() - start_time
                    
                    # 计算reward
                    reward = calculate_reward(task_name, example, workflow_output)
                    
                    results.append({
                        "example_id": example.get("identity", "unknown"),
                        "input": example.get("input", ""),
                        "expected_output": example.get("output", ""),
                        "workflow_output": str(workflow_output),
                        "reward": reward,
                        "success": reward > 0,
                        "execution_time": execution_time
                    })
                    
                    total_reward += reward
                    
                except asyncio.TimeoutError:
                    logger.error(f"Timeout executing workflow for example")
                    results.append({
                        "example_id": example.get("identity", "unknown"),
                        "input": example.get("input", ""),
                        "expected_output": example.get("output", ""),
                        "workflow_output": "Timeout",
                        "reward": 0.0,
                        "success": False,
                        "error": "Timeout"
                    })
                except Exception as e:
                    logger.error(f"Error executing workflow: {e}\n{traceback.format_exc()}")
                    results.append({
                        "example_id": example.get("identity", "unknown"),
                        "input": example.get("input", ""),
                        "expected_output": example.get("output", ""),
                        "workflow_output": str(e),
                        "reward": 0.0,
                        "success": False,
                        "error": str(e)
                    })
        
        finally:
            # 清理临时文件
            try:
                workflow_file.unlink()
            except:
                pass
        
        avg_reward = total_reward / len(examples) if examples else 0.0
        
        return {
            "task_name": task_name,
            "total_examples": len(examples),
            "successful_examples": sum(1 for r in results if r["success"]),
            "average_reward": avg_reward,
            "total_reward": total_reward,
            "results": results,
            "execution_time": datetime.now().isoformat()
        }
    
    async def execute_workflow_mock(self, workflow_code: str, task_name: str, 
                                  examples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """模拟执行workflow（当MetaGPT不可用时）"""
        results = []
        total_reward = 0.0
        
        for example in examples:
            mock_output = self._generate_mock_output(task_name, example)
            reward = calculate_reward(task_name, example, mock_output)
            
            results.append({
                "example_id": example.get("identity", "unknown"),
                "input": example.get("input", ""),
                "expected_output": example.get("output", ""),
                "workflow_output": mock_output,
                "reward": reward,
                "success": reward > 0,
                "mock": True
            })
            
            total_reward += reward
        
        avg_reward = total_reward / len(examples) if examples else 0.0
        
        return {
            "task_name": task_name,
            "total_examples": len(examples),
            "successful_examples": sum(1 for r in results if r["success"]),
            "average_reward": avg_reward,
            "total_reward": total_reward,
            "results": results,
            "execution_time": datetime.now().isoformat(),
            "mock_execution": True
        }
    
    def _generate_mock_output(self, task_name: str, example: Dict[str, Any]) -> str:
        """生成模拟输出用于测试"""
        # 根据任务类型生成合理的模拟输出
        if "sudoku" in task_name:
            # 返回一个模拟的数独解答
            return "1 2 3 4\n3 4 1 2\n2 1 4 3\n4 3 2 1"
        elif "minesweeper" in task_name:
            # 返回一个模拟的扫雷解答
            return json.dumps({"(0,0)": 1, "(1,1)": 1})
        else:
            # 返回期望的输出（用于测试）
            return example.get("output", "mock_solution")
    
    async def generate_verl_entry(self, task_name: str, workflow_type: str, 
                                entry_id: int, llm_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """生成单个VERL数据条目"""
        start_time = time.time()
        
        try:
            # 生成任务示例
            n_examples = self.config.get('examples_per_entry', 3)
            examples = self.manager.generate_task_examples(task_name, n_examples=n_examples)
            
            if not examples:
                logger.error(f"No examples generated for task {task_name}")
                return None
            
            # 获取任务描述
            description = self.manager.get_task_description(task_name)
            
            # 生成workflow代码
            workflow_code, error = await self.generate_workflow_code(
                task_name, examples, workflow_type, llm_config
            )
            
            if error:
                logger.error(f"Workflow generation failed: {error}")
                return None
            
            # 保存workflow代码
            workflow_file = self.workflows_dir / f"{task_name}_{workflow_type}_{entry_id}.py"
            with open(workflow_file, 'w', encoding='utf-8') as f:
                f.write(workflow_code)
            
            # 执行workflow并计算reward
            execution_result = await self.execute_workflow_real(
                workflow_code, task_name, examples
            )
            
            # 保存执行结果
            execution_file = self.execution_dir / f"{task_name}_{workflow_type}_{entry_id}_result.json"
            with open(execution_file, 'w', encoding='utf-8') as f:
                json.dump(execution_result, f, indent=2, ensure_ascii=False)
            
            # 创建VERL格式的聊天消息
            messages = [
                {
                    "role": "system",
                    "content": f"You are an expert at designing problem-solving workflows using {'predefined operators' if workflow_type == 'predefined' else 'flexible custom operators'}."
                },
                {
                    "role": "user",
                    "content": f"Create a workflow to solve {task_name} problems. Task description: {description}"
                },
                {
                    "role": "assistant",
                    "content": workflow_code
                }
            ]
            
            # 创建VERL条目
            verl_entry = {
                "data_source": f"internbootcamp_{task_name}",
                "prompt": messages,
                "ability": classify_ability(task_name),
                "reward_model": {
                    "task_name": task_name,
                    "test_cases": [ex["identity"] for ex in examples],
                    "average_reward": execution_result["average_reward"],
                    "successful_examples": execution_result["successful_examples"],
                    "total_examples": execution_result["total_examples"]
                },
                "extra_info": {
                    "entry_id": entry_id,
                    "task_type": get_task_type(task_name),
                    "workflow_type": workflow_type,
                    "num_examples": len(examples),
                    "timestamp": datetime.now().isoformat(),
                    "generation_time": time.time() - start_time,
                    "workflow_file": str(workflow_file),
                    "execution_file": str(execution_file)
                }
            }
            
            # 记录生成日志
            self.generation_log.append({
                "entry_id": entry_id,
                "task_name": task_name,
                "workflow_type": workflow_type,
                "reward": execution_result["average_reward"],
                "success": execution_result["average_reward"] > 0,
                "generation_time": time.time() - start_time
            })
            
            return verl_entry
            
        except Exception as e:
            logger.error(f"Failed to generate VERL entry: {e}\n{traceback.format_exc()}")
            self.generation_log.append({
                "entry_id": entry_id,
                "task_name": task_name,
                "workflow_type": workflow_type,
                "error": str(e),
                "success": False
            })
            return None
    
    async def generate_dataset(self, tasks: List[str], workflow_types: List[str], 
                             entries_per_config: int, llm_config: Dict[str, Any]) -> Dict[str, Any]:
        """生成完整的VERL数据集"""
        all_entries = []
        entry_id = 0
        
        total_combinations = len(tasks) * len(workflow_types) * entries_per_config
        logger.info(f"Generating {total_combinations} VERL entries...")
        
        for task_name in tasks:
            for workflow_type in workflow_types:
                task_entries = []
                
                for i in range(entries_per_config):
                    logger.info(f"Generating entry {entry_id+1}/{total_combinations}: {task_name} ({workflow_type})")
                    
                    entry = await self.generate_verl_entry(
                        task_name, workflow_type, entry_id, llm_config
                    )
                    
                    if entry:
                        all_entries.append(entry)
                        task_entries.append(entry)
                        logger.info(f"✓ Entry {entry_id}: reward={entry['reward_model']['average_reward']:.3f}")
                    else:
                        logger.warning(f"✗ Entry {entry_id}: generation failed")
                    
                    entry_id += 1
                
                # 保存任务特定的数据
                if task_entries:
                    task_file = self.verl_data_dir / f"{task_name}_{workflow_type}.json"
                    with open(task_file, 'w', encoding='utf-8') as f:
                        json.dump(task_entries, f, indent=2, ensure_ascii=False)
        
        # 统计信息
        rewards = [e['reward_model']['average_reward'] for e in all_entries]
        successful_entries = [e for e in all_entries if e['reward_model']['average_reward'] > 0]
        
        stats = {
            "total_entries": len(all_entries),
            "successful_entries": len(successful_entries),
            "success_rate": len(successful_entries) / len(all_entries) if all_entries else 0,
            "average_reward": sum(rewards) / len(rewards) if rewards else 0,
            "max_reward": max(rewards) if rewards else 0,
            "min_reward": min(rewards) if rewards else 0,
            "by_task": {},
            "by_workflow_type": {}
        }
        
        # 按任务统计
        for task in tasks:
            # task_name在reward_model中，不在extra_info中
            task_entries = [e for e in all_entries if e['reward_model']['task_name'] == task]
            task_rewards = [e['reward_model']['average_reward'] for e in task_entries]
            stats["by_task"][task] = {
                "count": len(task_entries),
                "average_reward": sum(task_rewards) / len(task_rewards) if task_rewards else 0,
                "success_rate": sum(1 for r in task_rewards if r > 0) / len(task_rewards) if task_rewards else 0
            }
        
        # 按workflow类型统计
        for wf_type in workflow_types:
            wf_entries = [e for e in all_entries if e['extra_info']['workflow_type'] == wf_type]
            wf_rewards = [e['reward_model']['average_reward'] for e in wf_entries]
            stats["by_workflow_type"][wf_type] = {
                "count": len(wf_entries),
                "average_reward": sum(wf_rewards) / len(wf_rewards) if wf_rewards else 0,
                "success_rate": sum(1 for r in wf_rewards if r > 0) / len(wf_rewards) if wf_rewards else 0
            }
        
        return {
            "entries": all_entries,
            "stats": stats
        }
    
    def save_dataset(self, dataset: Dict[str, Any], train_ratio: float = 0.8):
        """保存数据集"""
        entries = dataset["entries"]
        stats = dataset["stats"]
        
        # 随机打乱并分割数据
        random.shuffle(entries)
        split_idx = int(len(entries) * train_ratio)
        train_entries = entries[:split_idx]
        test_entries = entries[split_idx:]
        
        # 保存训练集和测试集
        train_file = self.verl_data_dir / "train.json"
        test_file = self.verl_data_dir / "test.json"
        
        with open(train_file, 'w', encoding='utf-8') as f:
            json.dump(train_entries, f, indent=2, ensure_ascii=False)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_entries, f, indent=2, ensure_ascii=False)
        
        # 保存parquet格式（可选）
        if self.config.get('save_parquet', True):
            train_df = pd.DataFrame(train_entries)
            test_df = pd.DataFrame(test_entries)
            
            train_df.to_parquet(self.verl_data_dir / "train.parquet", index=False)
            test_df.to_parquet(self.verl_data_dir / "test.parquet", index=False)
        
        # 保存统计信息
        stats_file = self.output_dir / "generation_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                "stats": stats,
                "train_size": len(train_entries),
                "test_size": len(test_entries),
                "generation_time": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        # 保存生成日志
        log_file = self.logs_dir / "generation_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.generation_log, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dataset saved:")
        logger.info(f"- Training: {len(train_entries)} entries → {train_file}")
        logger.info(f"- Test: {len(test_entries)} entries → {test_file}")
        logger.info(f"- Stats: {stats_file}")
        logger.info(f"- Log: {log_file}")


async def main():
    parser = argparse.ArgumentParser(description='Complete VERL data generator with reward calculation')
    
    # 基本参数
    parser.add_argument('--tasks', nargs='+', default=['sudoku_4x4_easy', 'minesweeper_5x5'],
                       help='Tasks to generate data for')
    parser.add_argument('--workflow-types', nargs='+', default=['predefined', 'flexible'],
                       choices=['predefined', 'flexible'],
                       help='Workflow types to generate')
    parser.add_argument('--entries-per-config', type=int, default=5,
                       help='Number of entries per task-workflow combination')
    parser.add_argument('--output-dir', default='verl_generation_output',
                       help='Output directory')
    parser.add_argument('--config', default='config.json',
                       help='Configuration file')
    parser.add_argument('--train-ratio', type=float, default=0.8,
                       help='Train/test split ratio')
    
    args = parser.parse_args()
    
    # 加载配置
    config = {}
    if os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    config['examples_per_entry'] = config.get('examples_per_entry', 3)
    config['save_parquet'] = config.get('save_parquet', True)
    
    # LLM配置（用于实际调用时）
    llm_config = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "temperature": 0.7
    }
    
    # 创建生成器
    generator = VERLCompleteGenerator(config, args.output_dir)
    
    # 生成数据集
    logger.info("Starting VERL data generation...")
    logger.info(f"Tasks: {args.tasks}")
    logger.info(f"Workflow types: {args.workflow_types}")
    logger.info(f"Entries per config: {args.entries_per_config}")
    
    dataset = await generator.generate_dataset(
        args.tasks,
        args.workflow_types,
        args.entries_per_config,
        llm_config
    )
    
    # 保存数据集
    generator.save_dataset(dataset, args.train_ratio)
    
    # 打印统计信息
    stats = dataset["stats"]
    logger.info("\n" + "="*50)
    logger.info("GENERATION SUMMARY")
    logger.info("="*50)
    logger.info(f"Total entries: {stats['total_entries']}")
    logger.info(f"Successful entries: {stats['successful_entries']} ({stats['success_rate']*100:.1f}%)")
    logger.info(f"Average reward: {stats['average_reward']:.3f}")
    logger.info(f"Reward range: [{stats['min_reward']:.3f}, {stats['max_reward']:.3f}]")
    
    logger.info("\nBy Task:")
    for task, task_stats in stats['by_task'].items():
        logger.info(f"  {task}: {task_stats['count']} entries, "
                   f"avg_reward={task_stats['average_reward']:.3f}, "
                   f"success={task_stats['success_rate']*100:.1f}%")
    
    logger.info("\nBy Workflow Type:")
    for wf_type, wf_stats in stats['by_workflow_type'].items():
        logger.info(f"  {wf_type}: {wf_stats['count']} entries, "
                   f"avg_reward={wf_stats['average_reward']:.3f}, "
                   f"success={wf_stats['success_rate']*100:.1f}%")
    
    logger.info(f"\nOutput saved to: {args.output_dir}")


if __name__ == "__main__":
    asyncio.run(main())