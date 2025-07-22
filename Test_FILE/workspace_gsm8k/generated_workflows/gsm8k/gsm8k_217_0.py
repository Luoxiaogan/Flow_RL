# Workflow ID: gsm8k_217_0
# Benchmark: gsm8k
# Data Indices: [267, 442, 366]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates three independent solutions with varied reasoning approaches,
        then selects the best one via ensemble, followed by a final review for quality assurance.
        """
        # Step 1: Generate multiple solutions using different strategies (Parallel Ensemble)
        solution_list = []
        instructions = [
            "Solve step-by-step: first identify what is given, then set up equations, and finally compute the answer.",
            "Break down the problem into parts: define variables, write expressions, solve each part independently, then combine results.",
            "Use a visual or diagrammatic approach: represent quantities as blocks or bars to reason about relationships before calculating."
        ]

        for instr in instructions:
            solution = await self.custom(instruction=instr)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the chosen solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer