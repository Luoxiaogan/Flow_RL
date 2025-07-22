# Workflow ID: gsm8k_387_1
# Benchmark: gsm8k
# Data Indices: [375, 109, 566]

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
        Reflect and Regenerate Workflow: 
        This structure uses meta-cognition — first generate a solution, then critically reflect on it to identify weaknesses or missed opportunities, 
        and finally use that reflection to guide the creation of a superior, more robust final answer.
        Unlike iterative refinement, this approach leverages insight from critique rather than mechanical rewriting.
        """
        # Step 1: Generate an initial solution using a structured, sequential reasoning pattern
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Solve the problem step-by-step with clear logical progression."
        )

        # Step 2: Critically reflect on the initial solution — do not rewrite yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a new, improved instruction for a fresh solution
        refined_instruction = f"Given the following reflection on the initial attempt: '{reflection}'. Now solve the problem again, ensuring all potential flaws or oversights are addressed."

        # Step 4: Generate a final solution informed by the reflection
        final_solution = await self.custom(instruction=refined_instruction)

        return final_solution