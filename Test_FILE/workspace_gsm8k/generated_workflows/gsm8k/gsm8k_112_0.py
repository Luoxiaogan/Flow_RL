# Workflow ID: gsm8k_112_0
# Benchmark: gsm8k
# Data Indices: [604, 123, 848]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions via parallel ensemble (fan-out).
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect critically on that solution to uncover potential blind spots.
        Step 4: Use the reflection to guide a new Custom call for an improved final answer.
        """
        # --- PARALLEL ENSEMBLE (Fan-out) ---
        solution_list = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve the problem step-by-step, showing all calculations clearly. Assume nothing. Be precise with units."
            )
            solution_list.append(sol)

        # --- SCENSEMBLE (Fan-in) ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- REFLECT (Critical Meta-Cognition) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE BASED ON REFLECTION (Reflect-and-Regenerate Pattern) ---
        final_answer = await self.custom(
            instruction=f"Given the following initial solution:\n{best_solution}\n\nAnd this reflection on its weaknesses or assumptions:\n{reflection}\n\nNow, provide a revised, more accurate solution that addresses the issues raised in the reflection."
        )

        return final_answer