# Workflow ID: gsm8k_388_1
# Benchmark: gsm8k
# Data Indices: [344, 406, 110]

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
        Reflect and Regenerate Workflow: Generate an initial solution, critically reflect on it to uncover flaws or missed insights, then use that reflection to guide a new, improved solution.
        This pattern mimics human metacognition — learning from mistakes and refining reasoning iteratively.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify what is being asked. Then break down the problem into smaller parts. Finally, compute the answer logically."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, potential errors, or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a more informed and precise instruction for a new solution
        final_instruction = (
            f"Given the initial solution and the following reflection:\n"
            f"{reflection}\n\n"
            f"Based on this critique, provide a revised, improved solution that addresses any weaknesses or ambiguities in the first attempt."
        )

        # Step 4: Generate a refined solution using the reflection as context
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution