#!/usr/bin/env python3
"""
获取项目根路径的辅助脚本
供Shell脚本调用，输出root.yaml中配置的根路径
"""
import os
import yaml
import sys

def get_project_root():
    """从root.yaml读取项目根路径"""
    try:
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_config_path = os.path.join(script_dir, 'configs', 'root.yaml')
        
        with open(root_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        root_path = config.get('root', '/nas/ganluo/Flow_RL')
        
        # 只输出路径，不输出其他信息
        print(root_path)
        return 0
        
    except Exception as e:
        # 出错时输出默认路径到stdout，错误信息到stderr
        sys.stderr.write(f"# 读取root.yaml失败: {e}\n")
        print("/nas/ganluo/Flow_RL")  # 默认使用服务器路径
        return 1

if __name__ == "__main__":
    sys.exit(get_project_root())