# Workflow ID: gsm8k_365_1
# Benchmark: gsm8k
# Data Indices: [347, 77, 465]

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
        This is a diverse and robust workflow using the Reflect and Regenerate pattern.
        It first generates an initial solution, then critically reflects on it to identify potential flaws or missed insights,
        and finally uses that reflection to guide a new, improved solution — mimicking human metacognition.
        This approach prioritizes depth over breadth: one strong cycle of critique and refinement rather than parallel solutions.
        """

        # Step 1: Generate an initial solution using a structured sequential approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by clearly breaking it into steps: identify knowns, unknowns, apply relevant operations, and verify.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_operations", "verify"]
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution
        final_answer = await self.custom(
            instruction=f"Given the following initial solution and the reflection below, produce a corrected and improved answer:\n\nInitial Solution:\n{initial_solution}\n\nReflection:\n{reflection}"
        )

        return final_answer