# Workflow ID: humaneval_51_1
# Benchmark: humaneval
# Data Indices: [81, 78]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        solution1 = await self.code_generate("Analyze the problem step by step and generate the code.")
        solution2 = await self.code_generate("Break down the problem into smaller parts and solve them one by one.")
        solution3 = await self.code_generate("Focus on understanding the core requirements and generate the code.")

        results = []
        for solution in [solution1, solution2, solution3]:
            result = await self.code_runner(solution)
            results.append((solution, result))

        passed_solutions = [solution for solution, result in results if result == "PASSED"]
        if passed_solutions:
            ensemble_solution = await self.sc_ensemble(passed_solutions)
            final_solution = await self.review(ensemble_solution)
            return final_solution
        else:
            # Use flexible custom to refine based on previous attempts
            refined_solution = await self.flexible_custom("Improve based on previous attempts", [solution1, solution2, solution3])
            final_solution = await self.review(refined_solution)
            return final_solution