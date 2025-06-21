# from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
# from grpo.reward_model import RewardModel4Game24
import json
import requests
from typing import Optional, List, Dict, Any
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import os
import time  # 添加在文件开头的导入部分

def test_prompt_on_case(model, tokenizer, numbers, device="cuda"):
    # 1. 构造 prompt
    prompt_template = '<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n'
    system_prompt = ("Play 24 game. "
                     "Given four numbers, determine if it's possible to reach 24 through basic arithmetic operations."
                     " Output the reasoning steps, one step per line. On the last line, output the expression, for example, "
                     "input: '10 1 12 3', "
                     "the last line should output: 'reach 24! expression: ((12 + 3) + (10 - 1))'.")
    user_prompt = " ".join(str(x) for x in numbers)
    prompt = prompt_template.format(system_prompt=system_prompt, user_prompt=user_prompt)

    # 2. 模型生成
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        output_ids = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=256,
            num_return_sequences=1,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id
        )
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # 3. 评测
    reward_model = RewardModel4Game24()
    reward, correct = reward_model.evaluate_result(generated_text, numbers)
    return {
        "prompt": prompt,
        "output": generated_text,
        "reward": reward,
        "correct": correct
    }

def test_prompt_performance(prompt, num_cases=5, device="cuda"):
    """
    测试给定prompt在24点游戏上的性能
    Args:
        prompt (str): 要测试的prompt
        num_cases (int): 要测试的案例数量
        device (str): 使用的设备，默认为"cuda"
    Returns:
        float: 正确率
        list: 详细的测试结果
    """
    # 1. 加载模型和tokenizer
    model = AutoModelForCausalLM.from_pretrained("./checkpoint/best").to(device)
    tokenizer = AutoTokenizer.from_pretrained("./checkpoint/best")
    
    # 2. 加载测试数据
    with open("./dataset/test_cases.json", "r") as f:
        test_cases = json.load(f)
    test_cases = test_cases[:num_cases]  # 只取前num_cases个案例
    
    # 3. 测试每个案例
    results = []
    correct_count = 0
    for numbers in test_cases:
        result = test_prompt_on_case(model, tokenizer, numbers, device=device)
        results.append(result)
        if result["correct"]:
            correct_count += 1
            
    accuracy = correct_count / len(test_cases)
    return accuracy, results

class SimpleRewardModel4Game24:
    def __init__(self):
        pass

    def extract_numbers(self, expr) -> list:
        """从表达式中提取数字"""
        curr_num = ''
        numbers = []
        for c in expr:
            if c.isdigit():
                curr_num += c
            elif curr_num:
                numbers.append(int(curr_num))
                curr_num = ''
        if curr_num:
            numbers.append(int(curr_num))
        return numbers

    def evaluate_result(self, result, case):
        """评估结果是否正确
        Args:
            result: 模型生成的完整文本
            case: 输入的4个数字列表
        Returns:
            reward: 1.0 如果结果正确，0.0 如果结果错误
            correct: 1 如果结果正确，0 如果结果错误
        """
        try:
            # 提取最后一行（包含最终表达式的行）
            output = result.split('assistant\n')[-1]
            lines = output.strip().split('\n')
            
            # 找到包含expression的最后一行
            expr_line = None
            for line in reversed(lines):
                if 'expression:' in line:
                    expr_line = line
                    break
            
            if not expr_line:
                return 0.0, 0

            # 提取表达式
            expression = expr_line.split('expression:')[-1].strip()
            
            # 检查数字是否匹配
            expr_numbers = sorted(self.extract_numbers(expression))
            input_numbers = sorted(case)
            if expr_numbers != input_numbers:
                return 0.0, 0

            # 计算表达式的值
            value = eval(expression)
            if abs(value - 24) < 1e-6:
                return 1.0, 1
            
            return 0.0, 0

        except Exception as e:
            return 0.0, 0

def test_prompt_performance_simple(prompt, num_cases=5, device="cuda"):
    """使用简化版reward model测试prompt性能"""
    # 1. 加载模型和tokenizer
    model = AutoModelForCausalLM.from_pretrained("./checkpoint/best").to(device)
    tokenizer = AutoTokenizer.from_pretrained("./checkpoint/best")
    
    # 2. 加载测试数据
    with open("./dataset/test_cases.json", "r") as f:
        test_cases = json.load(f)
    test_cases = test_cases[:num_cases]
    
    # 3. 测试每个案例
    results = []
    correct_count = 0
    reward_model = SimpleRewardModel4Game24()
    
    for numbers in test_cases:
        result = test_prompt_on_case_simple(model, tokenizer, numbers, reward_model, device=device)
        results.append(result)
        if result["correct"]:
            correct_count += 1
            
    accuracy = correct_count / len(test_cases)
    return accuracy, results

def test_prompt_on_case_simple(model, tokenizer, numbers, reward_model, device="cuda"):
    """使用简化版reward model测试单个案例"""
    # 1. 构造 prompt
    prompt_template = '<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n'
    system_prompt = ("Play 24 game. "
                     "Given four numbers, determine if it's possible to reach 24 through basic arithmetic operations."
                     " Output the reasoning steps, one step per line. On the last line, output the expression, for example, "
                     "input: '10 1 12 3', "
                     "the last line should output: 'reach 24! expression: ((12 + 3) + (10 - 1))'.")
    user_prompt = " ".join(str(x) for x in numbers)
    prompt = prompt_template.format(system_prompt=system_prompt, user_prompt=user_prompt)

    # 2. 模型生成
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        output_ids = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=256,
            num_return_sequences=1,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id
        )
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # 3. 评测
    reward, correct = reward_model.evaluate_result(generated_text, numbers)
    return {
        "prompt": prompt,
        "output": generated_text,
        "reward": reward,
        "correct": correct
    }

class OnlineAPIModel:
    """在线API调用的基类"""
    def __init__(self, api_key: str, api_base: str):
        self.api_key = api_key
        self.api_base = api_base
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def generate(self, prompt: str) -> str:
        raise NotImplementedError

    async def generate_batch(self, prompts: List[str], batch_size: int = 5) -> List[str]:
        """并行生成多个回答"""
        async with aiohttp.ClientSession() as session:
            # 将prompts分成大小为batch_size的批次
            batches = [prompts[i:i + batch_size] for i in range(0, len(prompts), batch_size)]
            all_results = []
            
            for batch in batches:
                # 并行处理每个批次
                tasks = [self.generate(prompt, session) for prompt in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                all_results.extend(batch_results)
            
            return all_results

class DeepSeekAPI(OnlineAPIModel):
    """DeepSeek API调用类"""
    def __init__(self, api_key: str, api_base: str = "https://api.deepseek.com/v1"):
        super().__init__(api_key, api_base)
        
    async def generate(self, prompt: str, session: Optional[aiohttp.ClientSession] = None) -> str:
        """异步生成回答"""
        if session is None:
            async with aiohttp.ClientSession() as session:
                return await self._generate(prompt, session)
        else:
            return await self._generate(prompt, session)
    
    async def _generate(self, prompt: str, session: aiohttp.ClientSession) -> str:
        """实际的API调用逻辑"""
        try:
            async with session.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 1,
                    "max_tokens": 2560
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API调用失败 (状态码: {response.status}): {error_text}")
                json_response = await response.json()
                return json_response["choices"][0]["message"]["content"]
        except Exception as e:
            # 保留完整的错误堆栈
            import traceback
            raise Exception(f"API调用出错: {str(e)}\n堆栈跟踪:\n{traceback.format_exc()}")

class QwenAPI(OnlineAPIModel):
    """Qwen API调用类 - 使用OpenAI风格的API"""
    def __init__(self, api_key: str, api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"):
        super().__init__(api_key, api_base)
        from openai import AsyncOpenAI  # 使用异步客户端
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base,
        )
        
    async def generate(self, prompt: str, session: Optional[aiohttp.ClientSession] = None) -> str:
        """异步生成回答"""
        try:
            completion = await self.client.chat.completions.create(  # 使用await调用异步API
                model="qwen-turbo-latest",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that solves 24 game problems."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1,
                max_tokens=2048,
            )
            return completion.choices[0].message.content
        except Exception as e:
            import traceback
            raise Exception(f"API调用出错: {str(e)}\n堆栈跟踪:\n{traceback.format_exc()}")
    
    async def generate_batch(self, prompts: List[str], batch_size: int = 5) -> List[str]:
        """重写父类的generate_batch方法，实现真正的并行处理"""
        tasks = []
        for prompt in prompts:
            task = self.generate(prompt)
            tasks.append(task)
        
        # 使用asyncio.gather并行执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

async def test_prompt_with_api_async(prompt: str,
                                   api_model: OnlineAPIModel,
                                   num_cases: int = 64,
                                   batch_size: int = 64,
                                   reward_model: Optional[Any] = None) -> tuple:
    """异步并行测试prompt性能"""
    total_start_time = time.time()  # 总计时开始
    
    print("\n开始加载测试数据...")
    start_time = time.time()
    # 1. 加载测试数据
    with open("./dataset/test_cases.json", "r") as f:
        test_cases = json.load(f)
    test_cases = test_cases[:num_cases]
    print(f"加载数据耗时: {time.time() - start_time:.2f}秒")
    
    print(f"\n准备测试 {len(test_cases)} 个案例...")
    start_time = time.time()
    # 2. 使用默认的简化版reward model
    if reward_model is None:
        reward_model = SimpleRewardModel4Game24()
    
    # 3. 准备所有prompts
    prompts = []
    for numbers in test_cases:
        user_input = " ".join(str(x) for x in numbers)
        full_prompt = f"{prompt}\n\nInput: {user_input}"
        prompts.append(full_prompt)
    print(f"准备prompts耗时: {time.time() - start_time:.2f}秒")
    
    print("\n开始并行生成答案...")
    start_time = time.time()
    # 4. 并行生成答案
    generated_texts = await api_model.generate_batch(prompts, batch_size)
    api_time = time.time() - start_time
    print(f"API调用总耗时: {api_time:.2f}秒")
    print(f"平均每个请求耗时: {api_time/len(prompts):.2f}秒")
    
    print("\n开始评估结果...")
    start_time = time.time()
    # 5. 评估结果
    results = []
    correct_count = 0
    
    # 使用线程池并行评估结果
    with ThreadPoolExecutor() as executor:
        eval_futures = []
        for i, (numbers, generated_text) in enumerate(zip(test_cases, generated_texts)):
            if isinstance(generated_text, Exception):
                print(f"处理案例 {numbers} 时发生错误: {str(generated_text)}")
                results.append({
                    "prompt": prompts[i],
                    "output": str(generated_text),
                    "reward": 0.0,
                    "correct": 0
                })
                continue
                
            future = executor.submit(reward_model.evaluate_result, generated_text, numbers)
            eval_futures.append((i, future))
        
        # 收集评估结果
        for i, future in eval_futures:
            try:
                reward, correct = future.result()
                results.append({
                    "prompt": prompts[i],
                    "output": generated_texts[i],
                    "reward": reward,
                    "correct": correct
                })
                if correct:
                    correct_count += 1
            except Exception as e:
                print(f"评估结果时发生错误: {str(e)}")
                results.append({
                    "prompt": prompts[i],
                    "output": generated_texts[i],
                    "reward": 0.0,
                    "correct": 0
                })
    
    print(f"评估结果耗时: {time.time() - start_time:.2f}秒")
    
    accuracy = correct_count / len(test_cases)
    total_time = time.time() - total_start_time
    print(f"\n总耗时: {total_time:.2f}秒")
    print(f"正确率: {accuracy * 100:.2f}%")
    
    return accuracy, results

if __name__ == "__main__":
    # 示例使用
    custom_prompt = ("Given four numbers, determine if it's possible to reach 24 through basic arithmetic operations (+, -, *, /)."
                    " Show your reasoning steps, one step per line."
                    " On the last line, write 'reach 24! expression: ' followed by the final expression."
                     "for example, input: '10 1 12 3', "
                     "the last line should output: 'reach 24! expression: ((12 + 3) + (10 - 1))'.")
    
    try:
        # 测试 Qwen API
        qwen_api_key = os.getenv("DASHSCOPE_API_KEY", "sk-ffc9c6e1042d48c290d5a81cbf7daf74")  # 优先使用环境变量
        qwen_api = QwenAPI(qwen_api_key)
        print("\nTesting with Qwen API (Parallel):")
        
        # 运行异步测试
        try:
            # 测试 Qwen
            accuracy_qwen, results_qwen = asyncio.run(test_prompt_with_api_async(
                custom_prompt, 
                qwen_api,
                num_cases=64,
                batch_size=64
            ))
            print(f"Qwen API Accuracy: {accuracy_qwen * 100:.2f}%")
            
            # 打印详细结果
            # for i, result in enumerate(results_qwen):
            #     print(f"\nTest case {i+1}:")
            #     print(f"Input: {result['prompt']}")
            #     print(f"Output: {result['output']}")
            #     print(f"Correct: {result['correct']}")
            # print(f"Qwen API Accuracy: {accuracy_qwen * 100:.2f}%")
        except Exception as inner_e:
            import traceback
            print(f"测试执行过程中发生错误:")
            print(f"错误类型: {type(inner_e).__name__}")
            print(f"错误信息: {str(inner_e)}")
            print(f"详细堆栈:\n{traceback.format_exc()}")
            
    except Exception as outer_e:
        import traceback
        print(f"\n完整错误信息:")
        print(f"错误类型: {type(outer_e).__name__}")
        print(f"错误消息: {str(outer_e)}")
        print(f"错误堆栈:\n{traceback.format_exc()}")