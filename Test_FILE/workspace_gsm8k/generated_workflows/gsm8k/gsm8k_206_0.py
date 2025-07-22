# Workflow ID: gsm8k_206_0
# Benchmark: gsm8k
# Data Indices: [669, 910]

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
        1. Generate multiple solutions in parallel (Parallel Ensemble).
        2. Select the best one using ScEnsemble.
        3. Reflect critically on that best solution to identify potential flaws or improvements.
        4. Use the reflection to guide a new Custom call for a refined final answer.
        This structure ensures robustness (from ensemble) and meta-cognition (from reflection).
        """

        # --- STEP 1: Parallel Ensemble — Generate 3 diverse initial solutions ---
        solution_list = []
        for i in range(3):
            instruction = "Solve this math problem step-by-step by breaking it into clear logical parts."
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- STEP 2: Select the best solution via ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Reflect on the best solution to uncover hidden assumptions or errors ---
        reflection_text = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate using reflection as guidance — critical refinement loop ---
        final_instruction = f"Given the following reflection on the previous solution:\n{reflection_text}\n\nNow, provide a corrected and improved solution based on this critique."
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer