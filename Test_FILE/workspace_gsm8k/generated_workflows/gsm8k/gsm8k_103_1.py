# Workflow ID: gsm8k_103_1
# Benchmark: gsm8k
# Data Indices: [46, 454]

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
        This pattern leverages meta-cognition by first generating a solution, then critically reflecting on it to guide a superior final answer.
        It avoids iterative refinement (which the existing workflow uses) and instead uses reflection as a catalyst for improvement.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Critically reflect on the initial solution — identify potential flaws, assumptions, or missing elements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a new, improved instruction for a fresh solution
        improved_instruction = f"Given the following reflection on the initial attempt: '{reflection}'. Now, solve the problem again with greater accuracy and clarity, addressing all identified issues."

        # Step 4: Generate a final solution based on the reflective critique
        final_solution = await self.custom(instruction=improved_instruction)

        return final_solution