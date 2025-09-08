import abc
import json
import importlib
from typing import List, Dict, Any

class BenchmarkHandler(abc.ABC):
    """
    为不同 Benchmark 提供统一接口的抽象基类 (Abstract Base Class)。

    这个类的作用是定义一个标准，所有特定数据集的处理器都需要遵守这个标准。
    它封装了与特定数据集格式相关的所有操作，例如：
    1. 如何加载数据。
    2. 如何提取问题文本以用于生成提示（Prompt）。
    3. 如何将生成的工作流代码包装成一个可执行的完整脚本。
    4. 如何评判工作流的执行结果是否正确。
    """

    def __init__(self, dataset_path: str, config=None):
        """
        初始化处理器。
        :param dataset_path: 指向数据集文件（例如 .jsonl）的完整路径。
        """
        if not dataset_path:
            raise ValueError("数据集路径不能为空。")
        self.dataset_path = dataset_path
        self.benchmark_name = self.__class__.__name__.replace("Handler", "").lower()
        self.data = self._load_data()
        self.config = config

    def _load_data(self) -> List[Dict[str, Any]]:
        """
        从 .jsonl 文件加载所有数据。这是一个通用功能，直接在基类中实现。
        """
        records = []
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                for line in f:
                    records.append(json.loads(line))
        except FileNotFoundError:
            raise FileNotFoundError(f"数据集文件未找到: {self.dataset_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"解析数据集文件失败: {self.dataset_path}, 错误: {e}")
        return records

    def _get_problem_by_index(self, index: int) -> Dict[str, Any]:
        """
        一个辅助函数，通过索引从加载的数据中查找问题。
        它首先尝试匹配数据中 'index' 字段，如果找不到，则退回到使用行号作为索引。
        """
        # 优先使用数据中明确的 'index' 字段
        for problem in self.data:
            if problem.get('index') == index:
                return problem
        
        # 如果没有 'index' 字段或找不到匹配项，则退回到使用列表的索引（行号）
        if 0 <= index < len(self.data):
            return self.data[index]
            
        raise IndexError(f"在数据集中无法找到索引为 {index} 的问题。")

    @abc.abstractmethod
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        【必须被子类实现】
        根据问题索引列表，生成用于构建 Prompt 的问题描述文本。
        每个数据集的 "问题" 格式不同，因此需要具体实现。
        
        :param indices: 用于生成prompt的问题索引列表。
        :return: 一个拼接好的字符串，包含所有问题。
        """
        pass

    @abc.abstractmethod
    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        【必须被子类实现】
        根据单个问题索引，获取用于执行和验证的完整数据。
        这通常是数据集中的一整个 JSON 对象。

        :param index: 用于验证的单个问题的索引。
        :return: 包含问题、答案等信息的完整字典。
        """
        pass

    # def build_executable_script(self, workflow_code: str, timeout: int) -> str:
    #     """
    #     将LLM生成的纯工作流代码，与特定于基准测试的模板拼接起来，
    #     形成一个完整的、可以被 `exec()` 执行的 Python 脚本字符串。
        
    #     这是一个通用实现，因为它通常只需要从 `conditions.py` 加载模板。
    #     如果某个 benchmark 需要非常特殊的拼接逻辑，可以重写此方法。
    #     """
    #     try:
    #         conditions_module = importlib.import_module(f"ScoreFlow.scripts.{self.benchmark_name}.conditions")
    #         python_start = getattr(conditions_module, "PYTHON_START", "")
    #         python_end = getattr(conditions_module, "PYTHON_END", "")
    #     except (ModuleNotFoundError, AttributeError) as e:
    #         raise ImportError(f"无法为 benchmark '{self.benchmark_name}' 加载代码模板: {e}")

    #     # 将工作流代码、启动和结束模板以及超时时间拼接在一起
    #     full_script = f"{python_start}\n{workflow_code}\n{python_end.format(time=timeout)}"
    #     return full_script

    def build_executable_script(self, workflow_code: str, timeout: int) -> str:
        """
        将LLM生成的纯工作流代码，与特定于基准测试的模板拼接起来，
        形成一个完整的、可以被 `exec()` 执行的 Python 脚本字符串。

        这个新版本是向后兼容的：
        1. 它会检查 PYTHON_END 模板是否包含 '{time}' 占位符。
        2. 如果包含 (旧版模板)，它会使用 .format(time=timeout) 来进行替换。
        3. 如果不包含 (新版模板)，它会假设 __call__ 方法接收 timeout 参数，
           并修改执行器代码来传递这个参数。
        """
        try:
            conditions_module = importlib.import_module(f"ScoreFlow.scripts.{self.benchmark_name}.conditions")
            common_module = importlib.import_module(f"ScoreFlow.scripts.common.conditions")
            python_start = getattr(common_module, "PYTHON_START", "")
            python_end = getattr(common_module, "PYTHON_END", "")
        except (ModuleNotFoundError, AttributeError) as e:
            raise ImportError(f"无法为 benchmark '{self.benchmark_name}' 加载代码模板: {e}")

        # ==================================================================
        # =================== 核心的兼容性逻辑 =======================
        # ==================================================================
        
        # 检查 PYTHON_END 模板是否是“旧版”格式
        if '{time}' in python_end:
            # 这是旧版模板，使用 .format() 来注入超时时间
            final_python_end = python_end.format(time=timeout)
            # 告诉执行器，__call__ 方法不需要参数
            call_signature = "await workflow_instance()"
        else:
            # 这是新版模板，它自己处理超时，不需要 .format()
            final_python_end = python_end
            # 告诉执行器，__call__ 方法需要传入 timeout 参数
            call_signature = f"await workflow_instance(timeout={timeout})"

        # 我们不再直接返回拼接好的脚本，而是返回一个包含所有部分的字典
        # 这让执行器可以更灵活地处理
        return {
            "python_start": python_start,
            "workflow_code": workflow_code,
            "python_end": final_python_end,
            "call_signature": call_signature
        }

    async def llm_judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        使用LLM进行智能判断，比较模型输出和标准答案。
        这是一个通用方法，子类可以直接使用或覆盖。
        
        :param model_output: 工作流执行后返回的原始结果
        :param ground_truth_data: 包含标准答案的完整数据
        :return: True 如果判定为正确，否则为 False
        """
        from metagpt.provider.llm_provider_registry import create_llm_instance as create
        
        # 提取问题和答案
        # 1. 直接从 'question' 字段提取问题，不再使用 passage 作为备选
        question = ground_truth_data.get('question', 'N/A')
        # question = ground_truth_data.get('question', '')
        # if not question and 'passage' in ground_truth_data:
        #     # 对于某些数据集，问题可能在不同字段
        #     question = ground_truth_data.get('passage', '')[:200] + "..."
        
        # # 获取标准答案
        # if 'answer' in ground_truth_data:
        #     ground_truth = ground_truth_data['answer']
        # elif 'all_answers' in ground_truth_data:
        #     ground_truth = ground_truth_data['all_answers']
        # else:
        #     ground_truth = str(ground_truth_data)

        # 2. 将完整的 ground_truth_data 格式化后提供给 LLM，让其拥有全部上下文
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

    async def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        评判模型的输出是否正确。
        默认实现使用LLM进行智能判断。
        子类可以覆盖此方法以提供特定的判断逻辑。
        
        :param model_output: 工作流执行后返回的原始结果。
        :param ground_truth_data: 包含标准答案或测试用例的完整数据。
        :return: True 如果判定为正确，否则为 False。
        """
        return await self.llm_judge(model_output, ground_truth_data)