# Workflow ID: gsm8k_26_1
# Benchmark: gsm8k
# Data Indices: [919, 426]

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
        This is a diverse and effective workflow using the 'Iterative Refinement' pattern with a twist:
        - Generate an initial solution via FlexibleCustom (sequential reasoning).
        - Critically reflect on it to uncover potential blind spots.
        - Use that reflection to guide a second, more targeted Custom call.
        - Finally, apply iterative refinement via Review to polish the result — ensuring clarity, completeness, and logical rigor.
        
        This structure emphasizes meta-cognition and progressive improvement over a single pass.
        """
        # Step 1: Generate an initial solution using structured sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into knowns, unknowns, and steps needed for resolution.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "formulate_plan", "execute_calculation"]
        )

        # Step 2: Reflect deeply on the initial solution — look for assumptions, missing logic, or ambiguity
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to craft a new, improved solution that addresses weaknesses
        guided_solution = await self.custom(
            instruction=f"Based on the following reflection:\n{reflection}\n\n"
                       "Rewrite the solution with clearer reasoning, explicit assumptions, and no gaps in logic."
        )

        # Step 4: Apply iterative refinement — review the guided solution to enhance clarity and correctness
        final_solution = await self.review(pre_solution=guided_solution)

        return final_solution