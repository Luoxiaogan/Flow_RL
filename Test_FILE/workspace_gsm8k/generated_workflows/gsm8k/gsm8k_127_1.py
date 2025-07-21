# Workflow ID: gsm8k_127_1
# Benchmark: gsm8k
# Data Indices: [100, 98]

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
        This workflow uses the 'Reflect and Regenerate' pattern — a meta-cognitive loop.
        Step 1: Generate an initial solution using a general reasoning instruction.
        Step 2: Critically reflect on that solution to identify potential flaws or missed steps.
        Step 3: Use the reflection to guide a new, improved solution via a custom instruction.
        This mimics how humans improve answers by self-assessment and targeted revision.
        """
        # --- Step 1: Generate an initial solution with clear, step-by-step reasoning ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, understand what is being asked. Then, break it into parts, apply relevant logic or math, and finally verify your answer."
        )

        # --- Step 2: Reflect critically on the initial solution without rewriting it ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Generate a final solution based on the reflection ---
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. Now, provide a refined, more accurate, and clearer solution that addresses the identified concerns."
        )

        return final_solution