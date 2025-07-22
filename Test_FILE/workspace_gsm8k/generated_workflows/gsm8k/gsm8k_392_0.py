# Workflow ID: gsm8k_392_0
# Benchmark: gsm8k
# Data Indices: [500, 591]

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
        Diverse workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions using parallel approach.
        Step 2: Select the best one via ScEnsemble.
        Step 3: Reflect on its potential weaknesses or assumptions.
        Step 4: Use that reflection to guide a new Custom solution for refinement.
        """
        # --- PARALLEL ENSEMBLE (Fan-out) ---
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve this math problem step-by-step. Consider multiple interpretations of the question if applicable.")
            solutions.append(sol)

        # --- SCENSBLE (Fan-in) ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- REFLECT ON BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- USE REFLECTION TO REGENERATE A BETTER SOLUTION ---
        final_instruction = f"Based on the following reflection:\n{reflection}\n\nRevise your solution accordingly, focusing on addressing the identified concerns and improving clarity."
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution