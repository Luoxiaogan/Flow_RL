PYTHON_START = '''import asyncio
from typing import Literal
import ScoreFlow.scripts.humaneval.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

PYTHON_END = '''

    async def __call__(self):
        TIMEOUT = {time}
        return await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)'''


START_PROMPT = '''Your objective is to output a workflow graph, based on the following template:

<graph>
class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.code_generate = operator.CustomCodeGenerate(self.config, self.problem)
        self.code_runner = operator.CodeRunner(self.config, self.problem)
        self.code_fix = operator.CodeFix(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        solution = await self.code_generate(instruction="Can you analyze this problem step by step and generate the code?")
        
        return solution
</graph>


Here's an introduction to operators you can use: (these are all you can use, do not create new operators)
1. CustomCodeGenerate:
Usage: Generates Python code based on customized input instruction.
Format MUST follow: code_generate(instruction: str) -> str
The instruction should encourage operator to think step by step and understand the problem, do not add the specific information of the task into the input instruction.
The output can serve as the input of next operators or the final output.

2. CodeRunner:
Usage: Executes the provided code solution against test cases and returns the results.
Format MUST follow: code_runner(solution) -> str
Returns either "PASSED" if all tests pass, or detailed error information if tests fail.
Example: test_result = await self.code_runner(generated_code)

3. CodeFix:
Usage: Analyzes failed code and error messages to generate a corrected version.
Format MUST follow: code_fix(solution, error_message) -> str
Takes the failed code and error details, returns an improved solution.
Example: fixed_code = await self.code_fix(failed_code, error_info)

4. ScEnsemble:
Usage: Evaluates multiple solutions and selects the best one based on quality and correctness.
Format MUST follow: sc_ensemble(solutions: List[str]) -> str
You can ensemble multiple solutions, for example:
ensembled_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])
The output can serve as the input of next operators or the final output.

5. Review:
Usage: Reviews and improves existing code solution for better quality, readability, and efficiency.
Format MUST follow: review(solution) -> str
Example: reviewed_solution = await self.review(working_code)

We have the task input as follow. But your output graph can not contain any specific information of the give task.
TASK: '''


END_PROMPT = '''

You need to notice:

**Ensure your graph is based on the given template and is correct to avoid runtime failures.** Do NOT import the modules operator and create, which have already been automatically imported. Ensure that all the prompts required by the current graph are included. Exclude any other prompts. The generated prompt must not contain any placeholders. Do not load the operators not provided.

**Introducing multiple operators at appropriate points can enhance performance.** Consider Python's loops (for, the iteration number MUST <= 3) to generate multiple solutions to ensemble. Consider logical and control flow (IF-ELSE, loops) for a more enhanced graphical representation.

**The graph complexity may corelate with the task complexity.** The graph complexity must < 7. Considering information loss, complex graphs may yield better results, but insufficient information transmission can omit the solution.

**As for the instruction prompt for operators. Your instruction prompt should focus on encouraging agent to think step by step. Do not ask agent to generate multiple (a few, some, etc) answers in one operator's instruction. Also note that different agents are independent, so do not use prompts like "generate another/alternative/different answer", "generate the first/second answer", etc.**

**Your output graph can not contain any specific information of the given task due to project requirement. All the information of this task will be given as input "problem" (self.problem) and other agents will execute this workflow.**

Only output the optimized graph (remember to add <graph> and </graph>, and the output can not contain any information of the given task).

Here is the graph without any task information: '''


TEMP_AVOID = '''class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.code_generate = operator.CustomCodeGenerate(self.config, self.problem)
        self.code_runner = operator.CodeRunner(self.config, self.problem)
        self.code_fix = operator.CodeFix(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        solution = await self.code_generate(instruction="Can you analyze this problem step by step and generate the code?")
        
        return solution'''

META_PROMPTS = [
    "Your objective is to design a workflow that generates correct Python code through iterative testing and refinement cycles. The workflow should emphasize code correctness by running tests and fixing errors systematically.",
    "Your objective is to create a robust workflow that implements test-driven development patterns. The workflow should generate code, test it thoroughly, fix any failures, and possibly ensemble multiple solutions for the best result.",
    "Your objective is to develop a workflow that uses parallel generation and ensemble methods. Generate multiple code solutions independently, test them all, and select the best working solution through ensemble evaluation.",
    "Your objective is to build a workflow that combines thoughtful code generation with comprehensive testing. Use review operators to improve code quality and ensure the final solution is both correct and well-written.",
    "Your objective is to construct an efficient workflow that balances thoroughness with simplicity. Focus on generating high-quality code on the first attempt, with targeted fix cycles only when necessary.",
    "Your objective is to design a creative workflow that explores different problem-solving approaches. Use branching logic to try alternative strategies when initial attempts fail, ensuring robustness.",
    "Your objective is to create a workflow emphasizing code quality through peer review patterns. Generate initial solutions, review them for improvements, test thoroughly, and refine based on both test results and code review feedback."
]

SYSTEM_PROMPT = "You are a helpful AI assistant expert in solving programming challenges. Please think step by step."

TEST_PROMPT = {"task_id": "HumanEval/2025", "prompt": "\n\ndef my_sum(a: int, b: int) -> int:\n    \"\"\" Write a function to add two int numbers.", "entry_point": "my_sum", "canonical_solution": "    return a+b\n", "test": "\n\ndef check(candidate):\n    assert candidate(1, 2) == 3\n"}

NO_EXCEPTION_LIST = ['''.split(' ')''', '''int(''']

TIME_LIMIT_TEST = 120
TIME_LIMIT = 180
sim_threshold = 1.1