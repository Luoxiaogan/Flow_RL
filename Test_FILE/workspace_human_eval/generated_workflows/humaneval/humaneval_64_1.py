# Workflow ID: humaneval_64_1
# Benchmark: humaneval
# Data Indices: [106, 69]

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
        solution1 = await self.code_generate("Can you analyze this problem step by step and generate the code?")
        solution2 = await self.code_generate("Can you analyze this problem step by step and generate the code?")
        solution3 = await self.code_generate("Can you analyze this problem step by step and generate the code?")

        results = [
            await self.code_runner(solution1),
            await self.code_runner(solution2),
            await self.code_runner(solution3)
        ]

        working_solutions = [solution1, solution2, solution3][0:results.count("PASSED")]

        if len(working_solutions) == 0:
            fixed_solution1 = await self.code_fix(solution1, results[0])
            fixed_solution2 = await self.code_fix(solution2, results[1])
            fixed_solution3 = await self.code_fix(solution3, results[2])

            reviewed_solution1 = await self.review(fixed_solution1)
            reviewed_solution2 = await self.review(fixed_solution2)
            reviewed_solution3 = await self.review(fixed_solution3)

            best_solution = await self.sc_ensemble([reviewed_solution1, reviewed_solution2, reviewed_solution3])
            return best_solution
        else:
            best_solution = await self.sc_ensemble(working_solutions)
            return best_solution