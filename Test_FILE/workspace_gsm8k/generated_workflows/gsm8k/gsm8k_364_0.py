# Workflow ID: gsm8k_364_0
# Benchmark: gsm8k
# Data Indices: [678, 676, 535]

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
        Diverse and efficient workflow using iterative refinement with a flexible custom operator.
        This approach balances simplicity with structured reasoning — ideal for multi-step math problems.
        """
        # Step 1: Use FlexibleCustom in iterative mode to systematically break down the problem
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this step-by-step by identifying knowns, unknowns, and applying relevant formulas.",
            reasoning_pattern="iterative",
            steps=["identify_knowns", "formulate_plan", "compute", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect on the solution to catch potential oversights (e.g., unit errors, missed conditions)
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Generate a final refined answer based on both the original solution and the reflection
        final_answer = await self.custom(
            instruction=f"Given the following initial solution:\n{initial_solution}\n\nAnd this reflection on possible flaws:\n{reflection}\n\nProvide a corrected and complete answer."
        )

        return final_answer