# Workflow ID: gsm8k_141_0
# Benchmark: gsm8k
# Data Indices: [883, 2]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate multiple independent solutions (Parallel Ensemble).
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect on the selected solution to identify potential flaws or improvements.
        Step 4: Use the reflection to guide a new Custom call for final refinement.
        This creates a two-stage reasoning loop with diversity in initial exploration and meta-cognition in final polishing.
        """

        # --- STEP 1: Parallel Ensemble ---
        # Generate 3 different solutions using independent reasoning paths
        solutions = []
        for i in range(3):
            instruction = f"Approach the problem from a unique perspective: {['logical breakdown', 'step-by-step deduction', 'case analysis'][i]}"
            sol = await self.custom(instruction=instruction)
            solutions.append(sol)

        # --- STEP 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Based on Reflection ---
        # Use the reflection as context to generate an improved final answer
        final_instruction = f"Given the following reflection on the current solution:\n{reflection}\n\nRevise the solution accordingly to address any weaknesses or assumptions."
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer