# Workflow ID: gsm8k_240_0
# Benchmark: gsm8k
# Data Indices: [625, 10, 847]

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
        This approach first explores multiple solution paths, selects the best one,
        then uses reflection to guide a targeted refinement — mimicking expert problem-solving.
        """

        # Step 1: Generate multiple initial solutions via parallel ensemble (fan-out)
        solutions = []
        for i in range(3):  # Three independent attempts with different reasoning styles
            instruction = f"Attempt {i+1}: Solve the problem by focusing on step-by-step decomposition and clear explanation."
            sol = await self.custom(instruction=instruction)
            solutions.append(sol)

        # Step 2: Use ScEnsemble to select the most promising solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the selected solution to uncover hidden flaws or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Conditional logic based on reflection content — if reflection indicates uncertainty, regenerate
        if "uncertain" in reflection.lower() or "assumption" in reflection.lower() or "missing" in reflection.lower():
            # Regenerate using reflection as guidance — this is a meta-cognitive loop
            final_instruction = f"Based on the following reflection:\n{reflection}\n\nRe-solve the problem with improved clarity and attention to potential gaps."
            final_solution = await self.custom(instruction=final_instruction)
        else:
            # If reflection is positive, just return the best solution
            final_solution = best_solution

        return final_solution