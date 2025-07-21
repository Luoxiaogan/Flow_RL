# Workflow ID: gsm8k_191_1
# Benchmark: gsm8k
# Data Indices: [198, 617, 69]

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
        This workflow uses a novel 'Reflect and Regenerate' pattern with a twist:
        - First, generate an initial solution using a structured FlexibleCustom approach.
        - Then, reflect on it to uncover hidden assumptions or logical gaps.
        - Finally, use that reflection to guide a targeted, iterative refinement via another FlexibleCustom call (iterative pattern).
        
        This structure avoids the single-solution path of the existing workflow and introduces a meta-cognitive loop with explicit iteration — making it more robust than simple reflection.
        """
        # Step 1: Generate a structured initial solution using FlexibleCustom in sequential mode
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying all known quantities and unknowns, then apply relevant formulas or logic.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "apply_logic", "compute"]
        )

        # Step 2: Critically reflect on the initial solution — identify potential flaws, oversights, or ambiguities
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new solution via iterative refinement (FlexibleCustom in iterative mode)
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. "
                               f"Refine your approach step-by-step through multiple iterations to ensure accuracy.",
            reasoning_pattern="iterative",
            steps=["initial_approach", "check_assumptions", "adjust_method", "verify_final"],
            max_iterations=3
        )

        return refined_solution