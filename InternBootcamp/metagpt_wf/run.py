#!/usr/bin/env python3
"""
运行脚本 - MetaGPT Workflow Executor
提供简单的命令行接口来运行完整流程或测试
"""

import argparse
import asyncio
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='MetaGPT Workflow Executor')
    parser.add_argument('--mode', choices=['full', 'test'], default='test',
                        help='运行模式: full=完整数据集, test=单任务测试')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='显示详细输出')
    
    args = parser.parse_args()
    
    if args.mode == 'test':
        print("运行单任务测试...")
        from test_single_task import test_single_task
        asyncio.run(test_single_task())
    
    elif args.mode == 'full':
        print("运行完整数据集...")
        from metagpt_workflow_executor import main as run_full
        asyncio.run(run_full())
    
    print("运行完成!")

if __name__ == "__main__":
    main() 