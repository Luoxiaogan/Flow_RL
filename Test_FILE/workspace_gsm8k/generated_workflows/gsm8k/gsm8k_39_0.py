# Workflow ID: gsm8k_39_0
# Benchmark: gsm8k
# Data Indices: [887, 285, 578]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        1. Generate 3 independent solutions (Parallel Ensemble).
        2. Select the best one using ScEnsemble.
        3. Reflect on its weaknesses or assumptions.
        4. Use reflection to guide a new Custom call for an improved solution.
        This structure ensures robustness through diversity and meta-cognition.
        """
        # Step 1: Generate multiple initial solutions in parallel (Fan-out)
        solution_list = []
        for i in range(3):
            instruction = "Solve the problem step-by-step with clear reasoning. Focus on breaking it into logical parts."
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Evaluate and select the best solution (Fan-in)
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Critically reflect on the chosen solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to generate a refined solution
        final_instruction = f"Given the following solution: {best_solution}\n\nAnd this reflection on potential flaws or improvements: {reflection}\n\nNow, provide a revised, more accurate solution based on that reflection."
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution