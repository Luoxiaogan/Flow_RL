# Workflow ID: gsm8k_360_1
# Benchmark: gsm8k
# Data Indices: [840, 898]

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
        This is a diverse and complex workflow that uses the 'Reflect and Regenerate' pattern as its core logic.
        
        Key differences from existing workflow:
        - No parallel ensemble at start; instead, we use a single initial solution followed by deep reflection
        - Uses iterative refinement *after* reflection, not before
        - Leverages FlexibleCustom with a branching reasoning pattern to explore alternative paths based on reflection
        - Only one initial solution is generated — no fan-out of multiple solutions
        - The reflection directly guides a structured re-solution via FlexibleCustom with branching logic
        """

        # Step 1: Generate an initial solution using flexible custom with sequential steps
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem systematically.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Critically reflect on the initial solution — identify flaws, assumptions, or missing elements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution via FlexibleCustom with branching logic
        # This allows us to dynamically choose different strategies based on the reflection
        final_answer = await self.flexible_custom(
            custom_instruction=f"Re-solve the problem with the following reflection in mind: '{reflection}'. "
                               f"Use a branching approach to consider alternative interpretations if needed.",
            reasoning_pattern="branching",
            steps=["re-evaluate_assumptions", "explore_alternatives", "refine_calculation", "validate_final"]
        )

        # Step 4: Optional polish — review the final answer for clarity and correctness
        polished_answer = await self.review(pre_solution=final_answer)

        return polished_answer