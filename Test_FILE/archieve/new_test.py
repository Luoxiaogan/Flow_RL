# solve_math.py

import asyncio
# metagpt.llm.LLM 是获取默认语言模型实例的标准方式
from metagpt.llm import LLM 
from ScoreFlow.scripts.GSM8K import operator  # 导入我们定义好的Actions

class MathSolverWorkflow:
    """
    这个类是一个自定义的“角色”（Role），负责解决一个数学问题。
    它通过编排一系列“动作”(Operators/Actions)来完成这个复杂任务。
    """
    def __init__(self, problem: str):
        """
        初始化工作流。

        Args:
            problem (str): 需要解决的具体问题描述。
        """
        self.problem = problem
        # 直接实例化一个默认的LLM。
        # MetaGPT会自动从您的环境（例如环境变量 OPENAI_API_KEY）加载配置。
        self.llm = LLM()
        
        # 为这个角色配备所有需要的“工具”(Actions/Operators)
        self.custom = operator.Custom(self.llm, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.llm, self.problem)
        self.review = operator.Review(self.llm, self.problem)
        print(f"--- 角色 [MathSolver] 已创建 ---\n负责解决问题: {self.problem}\n")

    async def run(self):
        """
        这是角色的核心执行逻辑，它定义了解决问题的步骤。
        """
        # --- 阶段1: 从不同角度思考，生成多个初步解法 ---
        print("--- 阶段1: 启动 'Custom' 动作，生成3个初步解法 ---")
        prompts = [
            "Solve the problem step-by-step. Show your reasoning clearly.",
            "Think about this problem from a different perspective and provide a detailed solution.",
            "Break the problem down into logical parts and solve each part."
        ]
        tasks = [self.custom(instruction=p) for p in prompts]
        initial_solutions = await asyncio.gather(*tasks)
        for i, sol in enumerate(initial_solutions):
            print(f"\n[初步解法 #{i+1}]\n{sol}\n")

        # --- 阶段2: 集成选优，找出最可靠的方案 ---
        print("--- 阶段2: 启动 'ScEnsemble' 动作，从多个解法中选出最可靠的 ---")
        ensembled_solution = await self.sc_ensemble(solutions=initial_solutions)
        print(f"\n[集成后的最佳解法]\n{ensembled_solution}\n")

        # --- 阶段3: 评审优化，给出最终答案 ---
        print("--- 阶段3: 启动 'Review' 动作，对最佳解法进行最终评审和优化 ---")
        final_solution = await self.review(pre_solution=ensembled_solution)
        print("\n--- ✨ 最终答案 ✨ ---\n")
        print(final_solution)

        return final_solution

async def main(requirement: str):
    """
    主函数，负责初始化并运行整个工作流。
    """
    # 实例化我们自定义的角色/工作流
    workflow = MathSolverWorkflow(problem=requirement)
    
    # 运行工作流
    await workflow.run()

if __name__ == "__main__":
    math_problem = "The greatest common divisor of positive integers m and n is 6. The least common multiple of m and n is 126. What is the least possible value of m + n?"
    
    # 使用asyncio运行主程序
    asyncio.run(main(math_problem))