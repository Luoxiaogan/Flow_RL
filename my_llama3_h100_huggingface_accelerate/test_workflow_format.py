#!/usr/bin/env python3
"""
验证workflow生成格式与reward server的匹配性
"""
import re
import json
from pathlib import Path

def test_workflow_format_compatibility():
    """测试workflow格式的兼容性"""
    
    print("=" * 70)
    print("Workflow格式兼容性测试")
    print("=" * 70)
    
    # 1. 模拟生成的不同格式文本
    test_cases = [
        {
            "name": "正确格式 - ```python标记",
            "text": '''根据问题，我需要生成一个workflow来解决这个数学问题。

```python
class Workflow:
    def __init__(self):
        self.steps = []
    
    def solve(self, problem):
        # 解决问题的逻辑
        result = problem * 2
        return result
```

这个workflow可以处理给定的问题。''',
            "expected": True
        },
        {
            "name": "旧格式 - <code>标记",
            "text": '''这是解决方案：

<code>
class Workflow:
    def __init__(self):
        pass
    
    def execute(self):
        return "solution"
</code>

完成。''',
            "expected": False  # reward server已不支持
        },
        {
            "name": "无格式标记",
            "text": '''class Workflow:
    def __init__(self):
        self.data = []
    
    def process(self):
        return sum(self.data)''',
            "expected": False  # 可能会失败
        },
        {
            "name": "多个```python块",
            "text": '''首先定义辅助函数：

```python
def helper(x):
    return x * 2
```

然后定义主要的workflow：

```python
class Workflow:
    def __init__(self):
        self.helper = helper
    
    def run(self):
        return self.helper(10)
```

这样就完成了。''',
            "expected": True  # 应该提取第一个或包含class Workflow的块
        }
    ]
    
    print("\n📝 测试不同格式的兼容性:")
    print("-" * 50)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {case['name']}")
        print(f"文本长度: {len(case['text'])} 字符")
        
        # 模拟reward server的提取逻辑
        workflow_code = extract_workflow_like_reward_server(case['text'])
        
        if workflow_code:
            print(f"✅ 成功提取workflow代码 ({len(workflow_code)} 字符)")
            print(f"   提取的代码开头: {workflow_code[:100]}...")
            
            # 验证是否包含class Workflow
            if "class Workflow" in workflow_code:
                print(f"   ✓ 包含class Workflow定义")
                success = True
            else:
                print(f"   ⚠️ 未找到class Workflow定义")
                success = False
        else:
            print(f"❌ 无法提取workflow代码")
            success = False
        
        # 检查是否符合预期
        if success == case['expected']:
            print(f"   测试结果: ✅ 符合预期")
        else:
            print(f"   测试结果: ❌ 不符合预期 (预期: {'成功' if case['expected'] else '失败'})")
    
    # 2. 测试实际的训练数据格式
    print("\n\n📊 检查训练数据格式:")
    print("-" * 50)
    
    # 尝试读取一个训练数据样本（如果存在）
    training_data_path = Path("/nas/ganluo/Flow_RL/training_data/training_data_raw_0825/filtered.jsonl")
    if training_data_path.exists():
        print(f"读取训练数据: {training_data_path}")
        with open(training_data_path, 'r') as f:
            # 只读取前5行作为样本
            for i, line in enumerate(f):
                if i >= 5:
                    break
                
                sample = json.loads(line)
                if 'messages' in sample:
                    # 查找assistant的响应
                    for msg in sample['messages']:
                        if msg.get('role') == 'assistant':
                            content = msg.get('content', '')
                            
                            print(f"\n样本 {i+1}:")
                            if "```python" in content:
                                print("   ✅ 包含```python格式")
                            elif "<code>" in content:
                                print("   ⚠️ 使用旧的<code>格式")
                            else:
                                print("   ❌ 无格式标记")
                            
                            break
    else:
        print("⚠️ 训练数据文件不存在（本地测试环境）")
    
    # 3. 提供建议
    print("\n\n💡 格式建议:")
    print("=" * 70)
    print("1. 训练数据应使用```python格式包裹workflow代码")
    print("2. 生成时模型会自然遵循训练数据的格式")
    print("3. Reward server会自动提取```python块中的代码")
    print("4. 客户端不需要做任何提取，直接发送原始生成文本")
    print("5. 如果提取失败，检查日志中的'生成文本预览'")

def extract_workflow_like_reward_server(response: str) -> str:
    """
    模拟reward server的提取逻辑
    基于scoreflow_reward_utils.py第1282-1303行
    """
    if not response:
        return None
    
    # 尝试提取```python标记内的代码
    code_pattern = re.compile(r'```python\s*\n(.*?)\n```', re.DOTALL)
    matches = code_pattern.findall(response)
    
    if matches:
        # 如果有多个匹配，优先返回包含class Workflow的
        for match in matches:
            if "class Workflow" in match:
                return match.strip()
        # 否则返回第一个
        return matches[0].strip()
    
    # 后备：尝试提取<code>标记（虽然reward server已注释掉这部分）
    # code_pattern = r'<code>(.*?)</code>'
    # matches = re.findall(code_pattern, response, re.DOTALL)
    # if matches:
    #     return matches[0].strip()
    
    return None

if __name__ == "__main__":
    test_workflow_format_compatibility()