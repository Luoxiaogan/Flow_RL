# Workflow ID: gsm8k_1_1
# Benchmark: gsm8k
# Data Indices: [313, 203, 892]

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
        Generate an initial solution, critically reflect on its potential flaws or gaps, 
        then use that reflection to guide a new, improved solution. This mimics meta-cognitive reasoning.
        """
        # Step 1: Generate an initial solution using flexible custom with structured steps
        initial_solution = await self.flexible_custom(
            custom_instruction="Break the problem into clear logical components and solve step-by-step.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: Critically reflect on the solution — identify assumptions, missing logic, or unclear reasoning
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a superior final solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                       f"Reconstruct the answer with clearer logic, better structure, and no unresolved assumptions."
        )

        return final_solution