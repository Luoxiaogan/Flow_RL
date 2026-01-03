#!/usr/bin/env python3
"""
SFT Data Optimizer - 批量优化SFT训练数据格式
用于将<code>标签转换为markdown代码块，并优化prompt格式
"""

import json
import re
import sys
import argparse
from typing import Dict, List, Tuple
from pathlib import Path


class SFTDataOptimizer:
    def __init__(self):
        # System role 的新内容 - 使用原始字符串形式
        self.new_system_content = "\nYour fundamental purpose is to act as an expert and highly abstract **System Architect**. You translate formal problem specifications into universal, reusable Python solution blueprints.\n\nYour core task is to **generalize**, not to solve. You will receive a detailed specification for a class of problems, which includes:\n1. A high-level description of the problem domain\n2. A strictly defined set of callable software \"Operators\" that serve as your only building blocks\n3. An illustrative example instance, provided solely to help you understand the abstract reasoning pattern\n\n**Your response MUST strictly adhere to the following two-part format:**\n\n**1. A `<think>...</think>` block:**\nInside this block, you must articulate your complete reasoning process for creating a **general solution for the entire problem class**, not just the provided example. Your reasoning should include:\n- A step-by-step analysis of the problem category.\n- Consideration of different potential strategies and approaches.\n- A clear explanation of your final design decisions and why you chose specific operators for the workflow.\n\n**2. A Python Code Block:**\nImmediately following the closing `</think>` tag, provide the complete and reusable Python solution. This code must be enclosed in markdown fences, specifically ` ```python ... ``` `.\n\n---\n\n### Example Response Structure:\n\n<think>\nFirst, I need to deeply understand the core characteristics of this problem class. The goal is to design a workflow that is robust and generic.\n\nMy strategy will be to [Your step-by-step reasoning for the general problem class goes here...].\n\nI've chosen the `Generate` operator for the initial step because [Your design decision explanation...]. This approach is superior to [alternative approach] because [justification...].\n</think>\n```python\n# --- DO NOT IMPORT HERE ---\nclass Workflow:\n    def __init__(self, config, problem) -> None:\n        # --- DO NOT MODIFY THIS SECTION ---\n        self.config = config\n        self.problem_text = problem\n        self.llm = create(config)\n        \n        self.generate = operator.Generate(self.llm, self.problem_text)\n        self.revise = operator.Revise(self.llm, self.problem_text)\n        self.summarize = operator.Summarize(self.llm, self.problem_text)\n        self.ensemble = operator.Ensemble(self.llm, self.problem_text)\n\n    async def run_workflow(self):\n        \"\"\"\n        Implement the core problem-solving logic here.\n        Remember: \n        - Use detailed, comprehensive instructions\n        - Dynamic instruction construction is powerful\n        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]\n        \"\"\"\n        import asyncio\n        # --- YOUR WORKFLOW LOGIC HERE ---\n```\n---\n\nYour generated Python workflow must be robust enough to work for any problem instance within the described domain."

        # User role 中需要替换的部分（从 ### 2 到 ### 5）- 使用原始字符串形式
        self.user_replacement_section = "### 2. Available Operators & Building Blocks\n\nAll operators follow a consistent interface pattern and are initialized with the problem text. They are available as `self.operator_name`.\n\n**Important Note:** The operators are pre-initialized with `self.problem_text`. Each operator automatically includes it in their prompts (you'll see it as \"**Original Problem:**\" in their internal prompts). You don't need to worry about losing the problem context - it's always available to every operator call behind the scenes, regardless of what you pass as the context parameter.\n\n\n#### **CRITICAL: Understanding Parameters**\n\n**The `instruction` Parameter (Required for all operators):**\n- **Purpose:** Contains the COMPLETE strategic directive that fully specifies what the operator should do\n- **Content:** Should be **comprehensive and detailed** - think of it as a full prompt that leaves nothing ambiguous\n- **Length:** Can and SHOULD be long when needed (100-500+ words is perfectly acceptable and often necessary)\n- **Dynamic Construction:** Can include information extracted from previous steps, specific constraints, detailed reasoning strategies, and formatted requirements\n- **Key Principle:** Since we're building reusable workflows, problem-specific information cannot be hardcoded in the workflow structure. While instructions can dynamically incorporate relevant extracted information to guide the operation, the main data to be processed should remain in the context parameter.\n\n**The `context` Parameter (Required for all operators except Generate):**\n- **Purpose:** Provides the INPUT DATA that the instruction will operate on\n- **Content:** The actual text, data, or results from previous operations - this is the primary information source\n- **Type:** String for Generate/Revise/Summarize operators\n- **Usage:** Think of it as the \"working material\" that the instruction processes\n- **Note:** Ensemble uses `contexts` (plural) which takes List[str] instead of a single string\n\n### Core Operators\n\n**1. Generate: CREATE new information**\n- **Signature:** `await self.generate(instruction: str, context: str = \"\") -> str`\n- **Purpose:** Produces new text, analysis, or reasoning based on strategic instructions\n\n**2. Revise: IMPROVE existing information**\n- **Signature:** `await self.revise(instruction: str, context: str) -> str`\n- **Purpose:** Critiques and refines existing text based on specific improvement criteria\n\n**3. Summarize: COMPRESS information**\n- **Signature:** `await self.summarize(instruction: str, context: str) -> str`\n- **Purpose:** Condenses text while preserving key information relevant to the problem\n\n**4. Ensemble: DECIDE between or synthesize options**\n- **Signature:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`\n- **Purpose:** Evaluates, compares, or merges multiple candidate solutions\n\n### 3. Key Design Principles\n\n**Dynamic Instruction Construction:**\nExtract information early, then incorporate it into subsequent instructions using f-strings:\n```python\nextraction = await self.generate(instruction=\"Extract all numerical values...\", context=self.problem_text)\nanalysis = await self.generate(\n    instruction=f\"Given these extracted values: {extraction}\\nNow solve step by step...\",\n    context=self.problem_text\n)\n```\n\n**Parallel Execution:**\nUse `asyncio.gather()` for independent operations:\n```python\nresults = await asyncio.gather(\n    self.generate(instruction=\"Approach 1...\", context=...),\n    self.generate(instruction=\"Approach 2...\", context=...)\n)\nfinal = await self.ensemble(instruction=\"Select best...\", contexts=results)\n```\n\n**Common Pitfalls:**\n- Don't hardcode problem-specific data in workflow code\n- Don't use `await` inside list comprehensions (blocks parallelism)\n- Do use detailed instructions (100-500+ words when needed)\n- Do extract info dynamically and incorporate into instructions\n\n#### **Innovation Guidelines:**\n\n**Maximize the power of instructions by:**\n- Building multi-paragraph instructions that leave nothing to interpretation\n- Dynamically incorporating ALL relevant extracted information\n- Creating instruction templates that adapt based on detected patterns\n- Using instructions to implement complex reasoning strategies\n- Including specific formatting requirements and output structures\n\n**Remember:**\n- Instructions are mini-prompts - make them as detailed as needed\n- Extract early, enrich instructions throughout\n- The workflow provides structure; instructions provide intelligence\n- Never hardcode problem-specific data in the workflow code itself\n- Always pass context appropriately - empty string for initial Generate, List for Ensemble\n\n#### **Common Pitfalls to Avoid:**\n\n```python\n# WRONG: Hardcoding problem-specific information\nresult = await self.generate(\n    instruction=\"Count how many field goals the Patriots scored\",  # Too specific!\n    context=self.problem_text\n)\n\n# CORRECT: Generic instruction that works for any problem\nresult = await self.generate(\n    instruction=\"Identify what the question is asking for, then count or calculate the requested value\",\n    context=self.problem_text\n)\n\n# WRONG: Sequential execution when parallel is possible\nresult1 = await self.generate(...)  # Waits\nresult2 = await self.generate(...)  # Then waits again\n\n# CORRECT: Parallel execution for independent operations\nresults = await asyncio.gather(\n    self.generate(...),\n    self.generate(...)\n)\n```\n\n### 4. Your Task: Complete the `run_workflow` Method\n\nYour task is to write the Python code for the `run_workflow` method within the provided template. Focus on creating a robust, reusable workflow that leverages detailed instructions.\n\n**Base Template:**\n\n<think>\nFirst, I need to deeply understand the core characteristics of this problem class. The goal is to design a workflow that is robust and generic.\n\nMy strategy will be to [Your step-by-step reasoning for the general problem class goes here...].\n\nI've chosen the `Generate` operator for the initial step because [Your design decision explanation...]. This approach is superior to [alternative approach] because [justification...].\n</think>\n```python\n# --- DO NOT IMPORT HERE ---\nclass Workflow:\n    def __init__(self, config, problem) -> None:\n        # --- DO NOT MODIFY THIS SECTION ---\n        self.config = config\n        self.problem_text = problem\n        self.llm = create(config)\n        \n        self.generate = operator.Generate(self.llm, self.problem_text)\n        self.revise = operator.Revise(self.llm, self.problem_text)\n        self.summarize = operator.Summarize(self.llm, self.problem_text)\n        self.ensemble = operator.Ensemble(self.llm, self.problem_text)\n\n    async def run_workflow(self):\n        \"\"\"\n        Implement the core problem-solving logic here.\n        Remember: \n        - Use detailed, comprehensive instructions\n        - Dynamic instruction construction is powerful\n        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]\n        \"\"\"\n        import asyncio\n        # --- YOUR WORKFLOW LOGIC HERE ---\n```\n\n### 5. Critical Rules\n\n**A. Generality:** Create templates for problem CLASSES, not specific instances\n**B. Instructions:** Use comprehensive, detailed instructions (100-500+ words OK)\n**C. Parameters:** `instruction` (str) + `context` (str) for most; `contexts` (List[str]) for Ensemble\n**D. Control Flow:** Branch on operator results, not direct problem_text parsing\n**E. Complexity:** Typically 3-8 operator calls, parallelize when possible\n**F. Response Format:** ONLY `<think>...</think>` followed by ` ```python ... ``` `\n\n"

    def process_system_message(self, content: str) -> str:
        """处理 system 消息，直接替换为新内容"""
        return self.new_system_content

    def process_user_message(self, content: str) -> str:
        """处理 user 消息，替换中间部分但保留问题描述和示例"""
        # 找到 ### 1 的结束位置（即 ### 2 的开始位置）
        section2_start = content.find("### 2. Available Operators")
        if section2_start == -1:
            print("Warning: Could not find '### 2. Available Operators' in user message")
            return content
        
        # 找到 ### 6 的开始位置
        section6_start = content.find("### 6. Illustrative Example")
        if section6_start == -1:
            print("Warning: Could not find '### 6. Illustrative Example' in user message")
            return content
        
        # 保留 ### 1 的部分（问题描述）
        part1 = content[:section2_start].rstrip()
        
        # 保留 ### 6 及之后的部分（示例和引导语）
        part3 = content[section6_start:]
        
        # 组合新的内容
        new_content = f"{part1}\n\n{self.user_replacement_section}{part3}"
        
        return new_content

    def process_assistant_message(self, content: str) -> str:
        """处理 assistant 消息，替换代码标签为 markdown 格式"""
        # 替换 <code> 为 ```python
        new_content = re.sub(r'<code>\s*', '\n```python\n', content)
        
        # 替换 </code> 为 ```
        new_content = re.sub(r'\s*</code>', '\n```', new_content)
        
        return new_content

    def process_single_sample(self, sample: Dict) -> Dict:
        """处理单个数据样本"""
        new_sample = sample.copy()
        new_messages = []
        
        for message in sample['messages']:
            new_message = message.copy()
            role = message['role']
            
            if role == 'system':
                new_message['content'] = self.process_system_message(message['content'])
            elif role == 'user':
                new_message['content'] = self.process_user_message(message['content'])
            elif role == 'assistant':
                new_message['content'] = self.process_assistant_message(message['content'])
            else:
                # 保持其他角色的消息不变
                pass
            
            new_messages.append(new_message)
        
        new_sample['messages'] = new_messages
        return new_sample

    def validate_sample(self, sample: Dict) -> List[str]:
        """验证处理后的样本格式"""
        issues = []
        
        for message in sample.get('messages', []):
            content = message.get('content', '')
            role = message.get('role', '')
            
            if role == 'assistant':
                # 检查 assistant 消息的格式
                if '<code>' in content or '</code>' in content:
                    issues.append(f"Assistant message still contains <code> tags")
                if '<think>' not in content or '</think>' not in content:
                    issues.append(f"Assistant message missing <think> tags")
                if '```python' not in content:
                    issues.append(f"Assistant message missing Python code block")
            elif role == 'user':
                # 检查是否包含必要的章节
                required_sections = ["### 1.", "### 2.", "### 3.", "### 4.", "### 5.", "### 6."]
                for section in required_sections:
                    if section not in content:
                        issues.append(f"User message missing section {section}")
        
        return issues

    def process_file(self, input_path: str, output_path: str, validate: bool = True) -> Tuple[int, int, Dict]:
        """批量处理 JSONL 文件"""
        processed_count = 0
        error_count = 0
        validation_issues = {}
        
        # 确保输入文件存在
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\nProcessing: {input_path}")
        print(f"Output to: {output_path}")
        print("-" * 60)
        
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile, 1):
                if not line.strip():
                    continue
                
                try:
                    # 解析原始数据
                    sample = json.loads(line.strip())
                    
                    # 处理数据
                    new_sample = self.process_single_sample(sample)
                    
                    # 验证格式（如果启用）
                    if validate:
                        issues = self.validate_sample(new_sample)
                        if issues:
                            validation_issues[f"Line {line_num}"] = issues
                    
                    # 写入处理后的数据
                    outfile.write(json.dumps(new_sample, ensure_ascii=False) + '\n')
                    processed_count += 1
                    
                    # 显示进度
                    if processed_count % 100 == 0:
                        print(f"  Processed {processed_count} samples...")
                    
                except json.JSONDecodeError as e:
                    print(f"  Error: Invalid JSON at line {line_num}: {e}")
                    error_count += 1
                except Exception as e:
                    print(f"  Error at line {line_num}: {e}")
                    error_count += 1
        
        return processed_count, error_count, validation_issues


def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(
        description="Optimize SFT training data by converting code tags to markdown format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python optimize_sft_data.py /path/to/input.jsonl /path/to/output.jsonl
  python optimize_sft_data.py input.jsonl output.jsonl --no-validate
        """
    )
    
    parser.add_argument(
        'input_path',
        type=str,
        help='Absolute or relative path to the input JSONL file'
    )
    
    parser.add_argument(
        'output_path',
        type=str,
        help='Absolute or relative path for the output JSONL file'
    )
    
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip validation of processed data'
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 创建优化器实例
    optimizer = SFTDataOptimizer()
    
    # 执行处理
    try:
        print("\n" + "=" * 60)
        print("SFT Data Format Optimization Tool")
        print("=" * 60)
        
        processed, errors, issues = optimizer.process_file(
            input_path=args.input_path,
            output_path=args.output_path,
            validate=not args.no_validate
        )
        
        # 输出统计结果
        print("\n" + "=" * 60)
        print("Processing Summary")
        print("=" * 60)
        print(f"  Total processed: {processed} samples")
        print(f"  Total errors: {errors} samples")
        
        if processed + errors > 0:
            success_rate = (processed / (processed + errors)) * 100
            print(f"  Success rate: {success_rate:.2f}%")
        
        if issues and not args.no_validate:
            print(f"\n  Validation issues found: {len(issues)} samples")
            # 显示前5个问题作为示例
            for i, (location, sample_issues) in enumerate(list(issues.items())[:5]):
                print(f"\n  {location}:")
                for issue in sample_issues:
                    print(f"    - {issue}")
                if i == 4 and len(issues) > 5:
                    print(f"\n  ... and {len(issues) - 5} more samples with issues")
        elif not args.no_validate:
            print("\n  ✓ All samples passed validation!")
        
        print("\n" + "=" * 60)
        print("Process completed successfully!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()