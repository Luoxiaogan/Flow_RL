# Workflow ID: gsm8k_140_1
# Benchmark: gsm8k
# Data Indices: [169, 228]

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
        Iterative Refinement with Reflective Guidance: 
        Generate an initial solution, then use reflection to guide two rounds of refinement.
        This approach leverages meta-cognition — the model critiques its own reasoning to improve accuracy.
        """
        # Step 1: Generate an initial solution using a flexible custom operator with iterative pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, starting with a clear plan.",
            reasoning_pattern="iterative",
            steps=["plan", "execute", "verify"],
            max_iterations=1
        )

        # Step 2: Critically reflect on the initial solution to identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a revised solution that addresses the identified issues
        first_refined = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Revise the solution accordingly, focusing on clarity and correctness."
        )

        # Step 4: Review the first revision to further polish it
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined