# Workflow ID: gsm8k_295_0
# Benchmark: gsm8k
# Data Indices: [34, 162, 177]

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
        Diverse and efficient workflow using iterative refinement with a structured approach.
        Uses FlexibleCustom in iterative mode to progressively refine the solution.
        This avoids unnecessary complexity while ensuring robustness through multiple passes.
        """
        # Step 1: Use iterative FlexibleCustom for systematic problem solving
        solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step by identifying knowns, unknowns, applying operations, and verifying results.",
            reasoning_pattern="iterative",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify_solution"],
            max_iterations=2
        )

        # Step 2: Reflect on the solution to catch potential flaws or assumptions
        reflection = await self.reflect(pre_solution=solution)

        # Step 3: Use the reflection to guide a final custom refinement
        final_solution = await self.custom(
            instruction=f"Given the initial solution and this reflection: {reflection}. Now provide a polished, accurate answer."
        )

        return final_solution