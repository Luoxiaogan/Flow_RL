# Workflow ID: gsm8k_162_1
# Benchmark: gsm8k
# Data Indices: [383, 218, 929]

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
        This is a diverse and effective workflow using the 'Iterative Refinement' pattern with FlexibleCustom.
        It leverages structured, multi-step reasoning via the FlexibleCustom operator in iterative mode,
        allowing for progressive improvement without needing to manually loop. The final solution
        benefits from internal refinement based on prior steps, making it robust and adaptive.
        """
        # Step 1: Use FlexibleCustom in iterative mode to generate an initial solution with structured steps
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying key quantities and relationships in the problem.",
            reasoning_pattern="iterative",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify_result"],
            max_iterations=2
        )

        # Step 2: Critically reflect on the initial solution to uncover potential blind spots
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, more targeted solution via a fresh Custom call
        refined_instruction = (
            f"Based on this reflection: '{reflection}', re-solve the problem with enhanced precision. "
            "Ensure each step is logically sound and explicitly justified."
        )
        final_solution = await self.custom(instruction=refined_instruction)

        return final_solution