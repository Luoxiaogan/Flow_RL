# Workflow ID: gsm8k_268_1
# Benchmark: gsm8k
# Data Indices: [718, 25]

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
        Reflect and Regenerate Workflow: Generate an initial solution, reflect on its potential flaws or assumptions, 
        then use that reflection to guide a new, improved solution. This mimics meta-cognitive reasoning by explicitly 
        analyzing the quality of the first attempt before proceeding.
        
        This pattern is fundamentally different from iterative refinement because it introduces a reflective layer 
        that guides the next step rather than just improving the same output through repeated edits.
        """
        # Step 1: Generate an initial solution using general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down the problem into logical components."
        )

        # Step 2: Critically reflect on the solution — identify possible gaps, oversights, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a targeted instruction for a new solution
        final_instruction = f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses these points."

        # Step 4: Generate a refined solution based on the reflection
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution