# Workflow ID: gsm8k_29_0
# Benchmark: gsm8k
# Data Indices: [423, 599, 65]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best solution using ScEnsemble.
        3. Reflect on it to uncover hidden assumptions or errors.
        4. Use that reflection to guide a new Custom call for an improved final answer.
        This structure ensures robustness (via ensemble) and meta-cognition (via reflection).
        """

        # Step 1: Parallel Ensemble - Generate multiple initial approaches
        solutions = []
        for i in range(3):
            instruction = f"Approach the problem from a different angle: {['step-by-step', 'visualize', 'break into subproblems'][i]}"
            sol = await self.custom(instruction=instruction)
            solutions.append(sol)

        # Step 2: Choose the best solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the chosen solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate using reflection as guidance
        final_instruction = (
            "Given the following reflection on the previous solution:\n"
            f"{reflection}\n\n"
            "Now, synthesize a new, more accurate and logically sound solution based on this insight."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer