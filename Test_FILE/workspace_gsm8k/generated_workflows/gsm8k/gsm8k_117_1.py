# Workflow ID: gsm8k_117_1
# Benchmark: gsm8k
# Data Indices: [365, 899, 651]

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
        Generate an initial solution, then use a reflective critique to guide iterative improvements.
        This pattern introduces meta-cognition by analyzing the solution before refining it—leading to more targeted and effective revisions.
        """
        # Step 1: Generate an initial solution using general-purpose reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into logical parts and show your work clearly."
        )

        # Step 2: Critically reflect on the initial solution to identify potential flaws or missed steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new custom attempt that addresses the identified weaknesses
        guided_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. Now, solve the problem again with improved clarity and completeness."
        )

        # Step 4: First refinement — improve based on internal review of the guided solution
        first_refined = await self.review(pre_solution=guided_solution)

        # Step 5: Second refinement — further enhance the already-improved solution
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined