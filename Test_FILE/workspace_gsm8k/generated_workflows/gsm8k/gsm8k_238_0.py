# Workflow ID: gsm8k_238_0
# Benchmark: gsm8k
# Data Indices: [698, 935, 415]

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
        Step 1: Generate 3 independent solutions via parallel ensemble.
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect on it to uncover hidden assumptions or gaps.
        Step 4: Use that reflection to guide a targeted regeneration for an improved final answer.
        """
        # --- STEP 1: Parallel Ensemble (Fan-out) ---
        solution_list = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve this math problem by breaking it into clear steps. Focus on identifying knowns, unknowns, and relationships."
            )
            solution_list.append(solution)

        # --- STEP 2: Ensembling (Fan-in) ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate based on reflection ---
        final_instruction = (
            "Given the initial solution and the following reflection on its potential weaknesses:\n"
            f"{reflection}\n\n"
            "Now, provide a new, more accurate and comprehensive solution that addresses the issues identified above."
        )
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution