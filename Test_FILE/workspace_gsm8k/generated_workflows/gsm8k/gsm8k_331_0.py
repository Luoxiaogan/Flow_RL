# Workflow ID: gsm8k_331_0
# Benchmark: gsm8k
# Data Indices: [727, 990, 339]

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
        This is a diverse and efficient workflow using iterative refinement with reflection.
        It leverages the Reflect operator to critique the initial solution, then uses that insight
        to guide a new, improved solution via FlexibleCustom in an iterative pattern.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Critically reflect on the initial solution to identify potential flaws or missed steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a structured, iterative refinement process
        refined_solution = await self.flexible_custom(
            custom_instruction="Based on the following reflection, solve the problem again with improved clarity and accuracy.",
            previous_results=[reflection],
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "reconstruct_reasoning", "verify_solution"],
            max_iterations=2
        )

        return refined_solution