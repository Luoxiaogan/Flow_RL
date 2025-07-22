# Workflow ID: gsm8k_390_0
# Benchmark: gsm8k
# Data Indices: [691, 510]

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
        1. Generate 3 independent solutions via parallel ensemble (robustness).
        2. Select best solution using ScEnsemble.
        3. Reflect on the selected solution to identify potential flaws or improvements.
        4. Use reflection to guide a new, targeted custom generation for final answer.
        This creates a meta-cognitive loop that improves accuracy beyond a single pass.
        """

        # --- STEP 1: Parallel Ensemble (Fan-out) ---
        solution_list = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step with clear reasoning. Focus on breaking it into logical parts.")
            solution_list.append(sol)

        # --- STEP 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Based on Reflection (Reflect-and-Regenerate Pattern) ---
        final_instruction = f"Given the initial solution and the following reflection: {reflection}. Now, provide a refined and improved solution that addresses the identified weaknesses."
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer