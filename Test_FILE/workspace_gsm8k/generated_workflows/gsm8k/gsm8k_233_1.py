# Workflow ID: gsm8k_233_1
# Benchmark: gsm8k
# Data Indices: [590, 429]

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
        Reflect and Regenerate Workflow: Generate an initial solution, critically reflect on it,
        then use that reflection to guide a targeted re-generation for a superior final answer.
        This meta-cognitive loop ensures deep reasoning and self-correction — fundamentally different from iterative refinement.
        """
        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Break the problem into logical steps and solve systematically.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "validate"]
        )

        # Step 2: Critically reflect on the solution — identify potential flaws, assumptions, or missed logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind. Be precise, clear, and logically rigorous."
        )

        return final_solution