# Workflow ID: gsm8k_194_0
# Benchmark: gsm8k
# Data Indices: [37, 331, 933]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        Step 1: Generate 3 independent solutions using parallel ensemble (fan-out).
        Step 2: Select the best solution via ScEnsemble.
        Step 3: Reflect on the selected solution to identify weaknesses or missed assumptions.
        Step 4: Use reflection to guide a new Custom call for a refined final answer.
        """
        # --- Phase 1: Parallel Ensemble (Fan-out) ---
        solutions = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step. Break it into logical sub-problems and justify each step clearly."
            )
            solutions.append(solution)

        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Phase 2: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Phase 3: Regenerate Based on Reflection ---
        final_instruction = (
            "Given the following initial solution and reflection, produce an improved, more accurate answer:\n\n"
            f"Initial Solution:\n{best_solution}\n\n"
            f"Reflection:\n{reflection}\n\n"
            "Now, solve again with greater precision, addressing any flaws or gaps identified in the reflection."
        )

        final_answer = await self.custom(instruction=final_instruction)

        return final_answer