# Workflow ID: gsm8k_190_1
# Benchmark: gsm8k
# Data Indices: [990, 511, 499]

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
        Diverse workflow using the 'Reflect and Regenerate' pattern with iterative refinement.
        This approach first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to guide a structured, multi-step improvement process.
        It leverages FlexibleCustom in iterative mode for deeper reasoning refinement.
        """

        # Step 1: Generate an initial solution using general step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into clear, logical steps. Explain each step thoroughly."
        )

        # Step 2: Critically reflect on the initial solution to uncover potential flaws or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a flexible custom reasoning loop with iterative refinement
        refined_solution = await self.flexible_custom(
            custom_instruction="Based on the following reflection, refine the solution iteratively: " + reflection,
            reasoning_pattern="iterative",
            steps=["analyze_assumptions", "correct_errors", "validate_logic"],
            max_iterations=2,
            use_structured_output=True
        )

        return refined_solution