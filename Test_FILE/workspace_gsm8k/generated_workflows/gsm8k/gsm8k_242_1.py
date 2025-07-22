# Workflow ID: gsm8k_242_1
# Benchmark: gsm8k
# Data Indices: [823, 389]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates three independent solutions using different reasoning strategies,
        then uses ScEnsemble to select the most consistent and accurate one.
        Finally, it performs a single review to polish the chosen solution.
        This approach improves robustness by leveraging multiple perspectives and reducing reliance on any single reasoning path.
        """

        # Step 1: Generate 3 diverse solutions using varied instructions
        solution_list = []
        instructions = [
            "Solve the problem step-by-step, starting from first principles. Break down each part clearly.",
            "Approach this as if you're teaching someone who has never seen this type of problem before. Use analogies and simple explanations.",
            "Use a structured method: identify knowns, unknowns, formulas, and calculate step-by-step."
        ]

        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement — review the best solution to catch subtle errors or improve clarity
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution