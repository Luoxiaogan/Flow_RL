# Workflow ID: gsm8k_317_0
# Benchmark: gsm8k
# Data Indices: [534, 986, 786]

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
        This structure encourages deep metacognition: generate → reflect → improve.
        """
        # Step 1: Generate an initial solution using a flexible custom approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Apply systematic reasoning to solve the problem.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "solve", "verify"]
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Reconstruct the solution with improved clarity, accuracy, and completeness."
        )

        return final_solution