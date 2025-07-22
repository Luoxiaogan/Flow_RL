# Workflow ID: gsm8k_382_1
# Benchmark: gsm8k
# Data Indices: [663, 207, 333]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and robust workflow using the Iterative Refinement pattern with Reflect-based guidance.
        Starts with an initial solution, then uses reflection to guide improvements over two iterations.
        This creates a meta-cognitive loop where each refinement is informed by critical self-assessment.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem step-by-step, focusing on clarity and correctness.",
            reasoning_pattern="sequential",
            steps=["understand", "identify_knowns", "apply_logic", "compute", "verify"]
        )

        # Step 2: First iteration - Reflect on the solution to identify potential flaws or missed details
        reflection_1 = await self.reflect(pre_solution=initial_solution)

        # Step 3: Second iteration - Use the reflection to guide a more refined solution
        improved_solution_1 = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection_1}'. "
                        f"Revise your solution accordingly, ensuring all steps are logically sound and complete."
        )

        # Step 4: Second reflection - Critically assess the improved solution for deeper issues
        reflection_2 = await self.reflect(pre_solution=improved_solution_1)

        # Step 5: Final iteration - Generate the final solution based on both reflections
        final_solution = await self.custom(
            instruction=f"Based on the following two reflections:\n"
                        f"1. '{reflection_1}'\n"
                        f"2. '{reflection_2}'\n"
                        f"Provide a fully revised and accurate solution that addresses all identified concerns."
        )

        return final_solution