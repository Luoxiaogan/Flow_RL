# Workflow ID: gsm8k_237_0
# Benchmark: gsm8k
# Data Indices: [257, 146]

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
        Generates 3 independent solutions via varied custom instructions,
        then uses ScEnsemble to select the most consistent one, followed by a final review.
        """
        # --- STEP 1: Generate multiple solutions in parallel (fan-out) ---
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step using arithmetic operations only. Break down each part clearly."
            elif i == 1:
                instruction = "Approach this as a word problem: identify what is given, what is asked, and how they relate."
            else:
                instruction = "Use algebraic reasoning: define variables, set up equations, and solve systematically."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- STEP 2: Use ensemble to pick the best solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final refinement via review ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer