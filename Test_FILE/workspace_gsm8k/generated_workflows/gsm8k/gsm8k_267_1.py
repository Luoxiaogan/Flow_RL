# Workflow ID: gsm8k_267_1
# Benchmark: gsm8k
# Data Indices: [98, 793, 998]

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
        This is a diverse and effective workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out/Fan-in): Generate multiple independent solutions.
        2. Reflect and Regenerate: Critically reflect on the best solution and regenerate with improved reasoning.

        This approach combines robustness (multiple starting points) with meta-cognitive refinement (reflection-driven improvement).
        It's fundamentally different from the existing workflow which uses a single initial generation followed by reflection.
        """
        # Step 1: Generate 3 independent solutions using parallel reasoning (via loop + FlexibleCustom in sequential mode)
        solutions = []
        for i in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Solve the problem step-by-step, focusing on clarity and logical consistency.",
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution — identify assumptions, potential flaws, or missed opportunities
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on the reflection, generate a final improved solution using Custom with targeted instruction
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}'. "
                        "Now, provide a revised, more thorough, and logically sound answer that addresses all concerns raised."
        )

        return final_answer