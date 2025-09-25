from multiprocessing.connection import answer_challenge
from typing import List, Dict, Any
import json

# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class DropHandler(BenchmarkHandler):
    """
    DROP (Discrete Reasoning Over Passages) 数据集的具体处理器。
    
    简化版本: 移除了所有rule-based的判断逻辑, 完全依赖LLM进行智能判断。
    """
    
    def get_prompt_text_workflow_generation(self, indices: List[int]) -> str:
        """
        从 DROP 数据中提取问题和相关段落，并格式化为清晰的文本用于生成工作流。
        
        格式:
        ---
        **PASSAGE:**
        [passage text]

        **QUESTION:**
        [question text]

        **ANSWER:**
        [answer text]

        **ALL ANSWERS:(sometimes there are multiple answers, but the verification is that if you find one correct answer, you are right)**
        [all_answers text]
        ---
        
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取问题和段落
                question = problem['question']
                passage = problem['passage']
                answer = problem['answer']
                all_answers = problem['all_answers']

                # 组合问题和段落
                formatted_problem = f"""---
**PASSAGE:**
{passage}

**QUESTION:**
{question}

**ANSWER:(in the testing of the workflow, this will not be provided to the workflow)**
{answer}

**ALL ANSWERS:(in the testing of the workflow, this will not be provided to the workflow; sometimes there are multiple answers, but the verification is that if you find one correct answer, you are right)**
{all_answers}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从DROP数据中提取问题时出错: {e}")
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 DROP 数据中提取问题和相关段落，并格式化为清晰的文本用于生成工作流。
        
        格式:
        ---
        **PASSAGE:**
        [passage text]

        **QUESTION:**
        [question text]
        ---
        
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取问题和段落
                question = problem['question']
                passage = problem['passage']
                answer = problem['answer']
                all_answers = problem['all_answers']

                # 组合问题和段落
                formatted_problem = f"""---
**PASSAGE:**
{passage}

**QUESTION:**
{question}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从DROP数据中提取问题时出错: {e}")
        
    async def llm_judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        使用LLM进行智能判断，比较模型输出和标准答案。
        这是一个通用方法，子类可以直接使用或覆盖。
        
        :param model_output: 工作流执行后返回的原始结果
        :param ground_truth_data: 包含标准答案的完整数据
        :return: True 如果判定为正确，否则为 False
        """
        from metagpt.provider.llm_provider_registry import create_llm_instance as create
        
        question = ground_truth_data.get('question', 'N/A')
        ground_truth_context = json.dumps(ground_truth_data, indent=2, ensure_ascii=False)
        
        # 构建判断prompt - 更严格的版本
        # 修改 Prompt 逻辑，指导 LLM 如何使用完整的上下文进行判断
        prompt = f"""You are a meticulous and fair evaluator for a question-answering system. Your task is to determine if the "Model's Response" correctly answers the question based on the provided "Ground Truth Data".

**Question(this can also found in the Ground Truth Data):**
{question}

**Ground Truth Data (The reference for correctness):**
{ground_truth_context}

**The Model's Response to Evaluate:**
{model_output}


**Your Task & Evaluation Rules:**
1.  Analyze the `Ground Truth Data`. It contains the original `question`, the `answer`, and sometimes a list of all possible correct answers in `all_answers`.
2.  **Crucial Rule for `all_answers`:** If the `Ground Truth Data` contains a list called `all_answers`, the "Model's Response" is considered **CORRECT** if it is semantically equivalent to **ANY ONE** of the answers in that list.
3.  If only a single `answer` field exists, the "Model's Response" must be semantically equivalent to that value.
4.  The model's response MUST directly and accurately answer the `question` specified in the ground truth. Do not accept related but tangential information.
5.  Pay attention to specifics:
    -   For "Which happened first?" questions: The answer must specify the event that happened first.
    -   For counting questions: The answer must provide the correct number.
    -   For identification questions: The answer must identify the correct entity/person/place.

**Important:** 
- An answer that describes something related but doesn't answer the actual question is INCORRECT
- An answer missing key parts of the expected answer is INCORRECT
- Focus on whether the question was actually answered, not just whether related information was provided

**Examples of INCORRECT answers:**
- Question: "Which happened first, A or B?" → Answer: "A was an important event" (doesn't say which was first)
- Question: "Who won the game?" → Answer: "The game was exciting" (doesn't identify the winner)
- Question: "What is the death of Charles?" → Answer: "Charles II of Spain" (missing "death")

**Your Decision:**
Reply with EXACTLY one word: CORRECT or INCORRECT"""
        
        try:
            # 创建LLM实例并调用
            llm = create(self.config)
            response = await llm.aask(prompt)
            
            # 解析响应
            response = response.strip().upper()
            
            # 判断结果 - 修复：先检查INCORRECT，避免误判
            if "INCORRECT" in response:
                return False
            elif "CORRECT" in response:
                return True
            else:
                # 如果既不是CORRECT也不是INCORRECT，默认为错误
                print(f"Warning: Unexpected LLM judge response: {response}")
                return False
                
        except Exception as e:
            print(f"LLM judge failed: {e}")
            # 如果LLM判断失败，回退到字符串比较
            return str(model_output).lower() == str(ground_truth_context).lower()

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个 DROP 问题的完整数据，用于后续的执行和验证。
        这包括问题、段落、答案等信息。
        """
        return self._get_problem_by_index(index)

    # judge方法继承自基类，使用LLM进行智能判断
    # 如果需要特殊处理，可以覆盖该方法