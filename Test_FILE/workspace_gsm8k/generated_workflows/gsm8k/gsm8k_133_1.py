# Workflow ID: gsm8k_133_1
# Benchmark: gsm8k
# Data Indices: [925, 53]

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
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Reflect-and-Regenerate Workflow: Generate an initial solution, reflect on its potential flaws, then use that reflection to guide a targeted re-solution.
        This meta-cognitive loop mimics how humans identify and correct reasoning errors — efficient, focused, and logically distinct from iterative refinement.
        """
        # Step 1: Initial solution using flexible custom with structured sequential steps
        initial_solution = await self.flexible_custom(
            custom_instruction="Break the problem into clear steps: identify quantities, operations, and apply them in order.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_operations", "perform_calculation", "present_answer"]
        )

        # Step 2: Reflect on the solution — critique assumptions, logic gaps, or ambiguities
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a new, improved instruction for a fresh solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. Now solve the problem again, focusing on addressing these points."
        )

        return final_solution