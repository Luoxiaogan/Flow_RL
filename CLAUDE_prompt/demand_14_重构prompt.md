# 1. 确定新的system prompt
我们设计的System Prompt必须是**极其纯粹、抽象且稳固的**，因为它是在为Llama模型**灌输一种“元能力”（meta-skill）**——即“学习如何学习”新任务的能力。
```
SYSTEM_PROMPT = """
Your fundamental purpose is to act as an expert and highly abstract **System Architect**. You translate formal problem specifications into universal, reusable Python solution blueprints.

Your core task is to **generalize**, not to solve. You will receive a detailed specification for a class of problems, which includes:
1.  A high-level description of the problem domain.
2.  A strictly defined set of callable software "Operators" that serve as your only building blocks.
3.  An illustrative example instance, provided solely to help you understand the abstract reasoning pattern.

Your generated output **must** be a single, parameterized Python function that represents a generic workflow. This function must be robust enough to work for any problem instance within the described domain.

Crucially, the skill you are developing must be transferable. You should be prepared to receive specifications for **entirely new problem domains and new sets of operators** in the future and apply the same rigorous process of abstraction and generalization.
"""
```
1.  **定义了一个根本性的、不变的身份 (Defines a Fundamental Identity)**
    *   它用`Your fundamental purpose is to act as...`开头，直接定义了模型的“存在意义”。这个身份是任务无关的，无论是处理HotpotQA还是一个全新的叫`FutureBench`的任务，它的身份始终是“System Architect”。

2.  **明确将“泛化”作为核心任务 (Makes "Generalization" the Core Task)**
    *   `Your core task is to generalize, not to solve.` 这句话是整个Prompt的灵魂。它直接命令模型不要陷入具体例子的细节，而是去提炼更高层次的模式。

3.  **清晰地设定了输入契约 (Sets a Clear Input Contract)**
    *   它明确告诉模型，它将接收到一个包含三部分的“规格说明书”。这为您的User Prompt（`instruction`）提供了一个极其稳定的结构。您可以为五个benchmark（以及未来任何新的benchmark）都按照这个三段式结构来撰写User Prompt，从而保证SFT数据的高度一致性。

4.  **直接注入“可迁移性”的概念 (Explicitly Injects the Concept of Transferability)**
    *   最后一段是画龙点睛之笔：`Crucially, the skill you are developing must be transferable... prepared to receive specifications for entirely new problem domains and new sets of operators...`
    *   这部分几乎是在对模型进行“元认知训练”。它在告诉模型：“你现在学习的这个‘看说明书写代码’的技能，不是一次性的。你必须学会这个**方法论**，因为我以后会用全新的说明书来考验你。” 这会激励模型在SFT过程中学习到更深层次、更不容易被遗忘的抽象推理能力。
  
# 2. 整个prompt的结构(清洗API时&SFT数据)
1. 下面我们来polish和调整整个prompt的组成和结构。场景是这样的，我们有两种prompt。一种是我们在调用API合成数据的时候的prompt（system+user），一种是SFT时候的prompt(system+user,不包含答案，答案由调用API清洗数据给出)
首先回顾一下目前在调用API合成数据时的 prompt 的合成方法以及保存SFT数据时的 prompt 的方法：
```python
def _construct_generation_prompt(self, data_indices: List[int], existing_workflow: str = None) -> Tuple[List[Dict], str]:
    """使用 Handler 构建生成请求的 Prompt。"""
    start_prompt, end_prompt, system_prompt, meta_prompts = self._load_prompt_templates()
    
    # 1. 使用 handler 获取问题文本
    problem_text = self.handler.get_prompt_text(data_indices)
    
    # 2. 构建 Prompt
    selected_meta_prompt = random.choice(meta_prompts) if meta_prompts else ""
    final_end_prompt = f"\n**CRITICAL INSTRUCTION FOR THIS SPECIFIC TASK:**\n{selected_meta_prompt}\n\n" + end_prompt
    
    # 3. 如果有已存在的工作流，添加指示生成不同逻辑的工作流
    if existing_workflow:
        diversity_prompt = f"\n\n**CRITICAL REQUIREMENT - DIFFERENT LOGIC**: \n<existing_workflow>\n{existing_workflow}\n</existing_workflow>\n\n**You MUST generate a workflow with FUNDAMENTALLY DIFFERENT LOGIC from the above workflow.**\n\nDO NOT just change variable names (solution vs solution1) or formatting!\n\nInstead, you MUST use at least TWO of the following strategies to ensure different logic:\n1. **Different operator sequence**: Use operators in a different order (e.g., if existing uses generate->fix->review, try generate->review->ensemble)\n2. **Different control flow**: Use different conditional logic or loop structures (e.g., if existing checks result once, try multiple attempts with different strategies)\n3. **Different parallel/serial execution**: If existing runs operators serially, try parallel execution, or vice versa\n4. **Different ensemble strategy**: If existing uses ScEnsemble on all solutions, try selecting the best one first\n5. **Different error handling**: Use different approaches when solutions fail (e.g., retry with different prompts vs fix existing)\n6. **Different operator combinations**: Use operators that the existing workflow doesn't use at all\n\n**REMEMBER: The goal is LOGICAL DIFFERENCE, not cosmetic changes!**\n\n"
        user_prompt_str = start_prompt + f"{problem_text}" + diversity_prompt + final_end_prompt
    else:
        user_prompt_str = start_prompt + f"{problem_text}" + final_end_prompt

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt_str}
    ]
    
    return messages, problem_text

async def _generate_one_workflow(self, workflow_id: str, data_indices: List[int], api_config: Dict, existing_workflow: str = None):
    """生成单个工作流并保存文件。"""
    try:
        # 1. 构建 Prompt
        messages, problem_text = self._construct_generation_prompt(data_indices, existing_workflow)
        
        # 2. 调用 API
        logging.info(f"向 {api_config.get('provider', 'api')} 发送生成请求 (ID: {workflow_id}, Indices: {data_indices})")
        response_content = await call_openai_compatible_api(api_config, messages)
        
        # 3. 提取代码
        # 优先提取 <graph> 标签内的内容，否则剥离 ```python ```
        if "<graph>" in response_content:
            code = response_content.split('<graph>')[1].split('</graph>')[0].strip()
        else:
            code = response_content.strip().strip('```python').strip('```').strip()

        # 4. 保存结果
        if code:
            self._save_workflow_files(workflow_id, code, data_indices)
            logging.info(f"成功生成并保存工作流: {workflow_id}")
            # 立即保存训练数据（而不是暂存）
            if self.training_data_output:
                _, _, system_prompt, _ = self._load_prompt_templates()
                training_record = {
                    "workflow_id": workflow_id,  # 添加工作流ID以便后续匹配
                    "benchmark": self.benchmark_name,
                    "data_indices": data_indices,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": problem_text},
                        {"role": "assistant", "content": code}
                    ]
                }
                self._save_single_training_record(training_record)
            return code  # 返回生成的代码供后续使用
        else:
            raise ValueError("API响应中未能提取有效代码。")

    except Exception as e:
        logging.error(f"生成工作流 {workflow_id} 时失败: {e}")
        return None
```
所以，输入给API的user prompt，主要是: start_prompt + f"{problem_text}"(这部分主要是问题的例子) + final_end_prompt(由随机的一条random prompt+end_prompt)
而对于保存在SFT数据里面的user prompt，我目前是完全保存了全部的prompt的
而这里的`start_prompt, end_prompt, system_prompt, meta_prompts`, 是从每个benchmark对应的condition里面提取的
这里给出DROP的例子：
```
META_PROMPTS = [
    # 1. 强调多步推理
    "Your main goal is step-by-step reasoning. Use the specialized reasoning operators (CountingReasoning, ArithmeticReasoning, ComparisonReasoning) based on the problem type. Combine them with Custom for extraction and final answer formatting.",
    # 2. 强调鲁棒性
    "Your main goal is robustness. Use the 'Parallel Ensemble' pattern. Generate multiple solutions using different reasoning approaches, then use sc_ensemble to select the most consistent answer.",
    # 3. 强调迭代改进
    "Your main goal is iterative improvement. Start with AnswerGenerate for a quick solution, then use Review to refine it based on the problem's complexity.",
    # 4. 强调混合方法
    "Your main goal is comprehensive reasoning. Use FlexibleCustom with different reasoning patterns (sequential for step-by-step, parallel for multiple approaches) combined with specialized operators.",
    # 5. 强调效率
    "Your main goal is efficiency. Create a simple but effective workflow using the most appropriate specialized operator (CountingReasoning, ArithmeticReasoning, or ComparisonReasoning) based on the problem type.",
]

# System prompt for DROP tasks
SYSTEM_PROMPT = """
Your fundamental purpose is to act as an expert and highly abstract **System Architect**. You translate formal problem specifications into universal, reusable Python solution blueprints.

Your core task is to **generalize**, not to solve. You will receive a detailed specification for a class of problems, which includes:
1.  A high-level description of the problem domain.
2.  A strictly defined set of callable software "Operators" that serve as your only building blocks.
3.  An illustrative example instance, provided solely to help you understand the abstract reasoning pattern.

Your generated output **must** be a single, parameterized Python function that represents a generic workflow. This function must be robust enough to work for any problem instance within the described domain.

Crucially, the skill you are developing must be transferable. You should be prepared to receive specifications for **entirely new problem domains and new sets of operators** in the future and apply the same rigorous process of abstraction and generalization.
"""

START_PROMPT = '''Your objective is to generate a Python workflow graph for solving reading comprehension and discrete reasoning problems. You must output valid Python code based on the following template (but you must modify it):

<graph>
class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem  # IMPORTANT: problem is a dictionary, not a string!
        # If you need the problem as text, use self.problem_text:
        self.problem_text = str(problem) if isinstance(problem, dict) else problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.config, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.config, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        solution = await self.answer_generate()
        
        return solution
</graph>


Here's an introduction to operators you can use: (these are all you can use, do not create new operators)
1. Custom:
Usage: Generates anything based on fixed input problem and modifiable instruction.
Format MUST follow: custom(instruction: str) -> str
You can modify the instruction prompt, such like "Can you break down the problem into smaller steps?", "Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?", "Explain how to solve the problem with clear reasoning for each step", etc. For example:
solution = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
The output can serve as the input of next operators or the final output.
2. AnswerGenerate:
Usage: Directly generate answer (including thought) to the given problem.
Format MUST follow: answer_generate() -> str
For example:
solution = await self.answer_generate()
The output can serve as the input of next operators or the final output.
3. ScEnsemble:
Usage: Evaluate every solutions, then select the best solution in the solution list.
Format MUST follow: sc_ensemble(solutions: List[str]) -> str
You can ensemble few solutions, for example:
ensembled_solution = await self.sc_ensemble(solutions=solution_list)
The output can serve as the input of next operators or the final output.
4. Review:
Usage: Given previous solution, Review operator reviews the previous solution to regenerate the solution.
Format MUST follow: review(pre_solution: str) -> str
pre_solution should be solution from previous operator, for example
rev_solution = await self.review(pre_solution=pre_solution)
The output can serve as the input of next operators or the final output.
5. CountingReasoning:
Usage: Specialized for counting tasks (counting events, entities, occurrences).
Format MUST follow: counting_reasoning() -> str
For example:
count_result = await self.counting_reasoning()
Use this when the problem requires counting items, events, or occurrences.
6. ArithmeticReasoning:
Usage: Specialized for arithmetic computations (addition, subtraction, multiplication).
Format MUST follow: arithmetic_reasoning() -> str
For example:
arithmetic_result = await self.arithmetic_reasoning()
Use this when the problem requires numerical calculations.
7. ComparisonReasoning:
Usage: Specialized for comparison tasks (finding max/min, sorting, comparing values).
Format MUST follow: comparison_reasoning() -> str
For example:
comparison_result = await self.comparison_reasoning()
Use this when the problem requires finding maximum, minimum, or comparing entities.
8. FlexibleCustom (Advanced Operator):
Usage: A flexible operator that supports various reasoning patterns (sequential, parallel, iterative, branching) with customizable steps. Perfect for complex discrete reasoning without embedding problem-specific information.
Format: flexible_custom(custom_instruction: str = "", previous_results: List[str] = None) -> str
Configuration Options:
- reasoning_pattern: "sequential", "parallel", "iterative", or "branching"
- steps: List of reasoning steps like ["extract_values", "identify_operation", "perform_calculation", "verify_result"]
- max_iterations: Maximum iterations for iterative patterns (default: 1)
- use_structured_output: Whether to use structured output format (default: True)
Example 1 (Sequential calculation):
self.flexible_custom = operator.FlexibleCustom(self.agent, self.problem, 
                                              reasoning_pattern="sequential",
                                              steps=["identify_numbers", "determine_operation", "calculate_step_by_step", "check_answer"])
solution = await self.flexible_custom(custom_instruction="Focus on careful numerical extraction and computation")
Example 2 (Iterative refinement):
self.flexible_custom_iter = operator.FlexibleCustom(self.agent, self.problem,
                                                   reasoning_pattern="iterative", 
                                                   steps=["initial_count", "verify_completeness", "refine_answer"],
                                                   max_iterations=3)
refined_answer = await self.flexible_custom_iter(custom_instruction="Count carefully and double-check for missed items")
Use Cases:
- Sequential: Step-by-step calculations with verification
- Parallel: Compare multiple approaches to the same problem
- Iterative: Progressive refinement of counts or calculations
- Branching: Different paths based on problem type (counting vs arithmetic)


IMPORTANT NOTES ABOUT PROBLEM HANDLING:
- The 'problem' parameter is a DICTIONARY, not a string! 
- Do NOT call string methods like .lower() directly on self.problem
- If you need to check problem content, use self.problem_text instead
- The operators already handle the problem internally - you don't need to analyze it in the workflow
- Avoid conditional logic based on problem content - let the operators handle that

We have the problem input as follow. But your output graph can not contain any specific information of the this problem.
Question: '''

END_PROMPT = '''

You need to notice:

**Ensure your graph is based on the given template and is correct to avoid runtime failures.** Do NOT import the modules operator and create, which have already been automatically imported. Do not load the operators not provided.

**Introducing multiple operators at appropriate points can enhance performance.** Consider Python's loops (for, list comprehensions) to generate multiple solutions to ensemble.

**Every operator(agent)'s output should contribute to the final return output, otherwise, do not use them.**

**The graph complexity may corelate with the problem complexity.** The graph complexity must between 3 and 8. Considering information loss, complex graphs may yield better results, but insufficient information transmission can omit the solution.

**AVOID conditional logic in your workflow!** Do not use if/elif statements checking problem content like 'if "count" in self.problem.lower()'. The specialized operators (CountingReasoning, ArithmeticReasoning, etc.) already handle problem type detection internally. Just use them directly or combine multiple operators and let ScEnsemble select the best result.

**As for the instruction prompt for custom operator. Your instruction prompt should focus on encouraging agent to think step by step. Do not ask agent to generate multiple (a few, some, etc) answers in one operator's instruction. Also note that different agents are independent, so do not use prompts like "generate another/alternative/different answer", "generate the first/second answer", etc.**

**Your output graph must be optimized and different from the given template graph. Do not output graph without modification!**

**Your output graph can not contain any information of the given problem due to project requirement. All the information of this problem will be given as input "problem" (self.problem) and other agents will execute this workflow.**

Only output the optimized Python code graph (remember to add <graph> and </graph> tags around your Python code, and the output can not contain any information of the given problem).

Your output must be valid Python code that can be executed. Do not output XML or any other format.

Here is the optimized Python workflow graph without any problem information: '''
```

上述的整个prompt的设计主要是有如下的 concerns :
1. 给SFT的数据的user prompt, 可能太长了，例如包含了太多篇幅的详细的任务描述，以及operator描述，以及(尤其是hotpotqa)2～3个问题实例。
2. 整个prompt的设计可能还不太好