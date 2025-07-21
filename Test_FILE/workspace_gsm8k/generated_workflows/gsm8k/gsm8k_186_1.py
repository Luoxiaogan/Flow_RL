# Workflow ID: gsm8k_186_1
# Benchmark: gsm8k
# Data Indices: [611, 33]

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
        Reflect and Regenerate Pattern: A deep-cognitive loop where the model first generates a solution,
        then critically reflects on it to identify blind spots or assumptions, and finally uses that reflection
        to produce a more robust, well-justified answer. This mimics expert problem-solving behavior.
        """
        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["understand", "model", "compute", "validate"],
            custom_instruction="Solve the problem by first understanding what is given, modeling the relationships, computing the result, and validating your answer."
        )

        # Step 2: Critically reflect on the initial solution — do not rewrite yet
        reflection = await self.reflect(initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution via Custom
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Re-solve the problem from scratch, incorporating insights from the reflection to avoid errors, clarify logic, and ensure completeness. Be thorough and precise."
        )

        return final_solution