# Workflow ID: gsm8k_87_0
# Benchmark: gsm8k
# Data Indices: [574, 380]

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
        Efficient and diverse workflow using Reflect + FlexibleCustom (Iterative Pattern).
        This approach first generates an initial solution, then reflects on it to identify potential issues,
        and finally uses an iterative flexible custom operator to refine the solution in a structured way.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(instruction="Solve the problem by breaking it into clear steps: identify quantities, prices, and total costs. Show each calculation explicitly.")

        # Step 2: Reflect on the initial solution — look for missing steps, arithmetic errors, or unclear logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use iterative flexible custom to refine the solution based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction="Based on the following reflection, improve the solution: " + reflection,
            reasoning_pattern="iterative",
            steps=["verify_calculation", "clarify_steps", "finalize_answer"],
            max_iterations=2
        )

        return refined_solution