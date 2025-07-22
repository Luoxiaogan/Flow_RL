# Workflow ID: gsm8k_17_0
# Benchmark: gsm8k
# Data Indices: [89, 476]

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
        Generates 3 different solutions via varied instructions, then selects the best one.
        A final review step ensures clarity and correctness.
        """
        # --- Step 1: Generate 3 diverse solutions using different reasoning approaches ---
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve this math word problem by first identifying all quantities and their relationships. Then, write out each calculation step-by-step."
            elif i == 1:
                instruction = "Break down the problem into smaller sub-problems. Solve each part independently before combining the results. Show your work clearly."
            else:
                instruction = "Use a systematic approach: define variables, set up equations, solve them, and verify your answer. Explain every logical transition."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- Step 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final Review for clarity, completeness, and error correction ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer