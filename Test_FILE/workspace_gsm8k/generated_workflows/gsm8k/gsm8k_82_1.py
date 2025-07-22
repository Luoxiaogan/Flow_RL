# Workflow ID: gsm8k_82_1
# Benchmark: gsm8k
# Data Indices: [283, 179]

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
        This is a diverse workflow using two distinct patterns:
        1. Iterative Refinement (via FlexibleCustom with iterative pattern)
        2. Reflect-and-Regenerate (using the new Reflect operator to guide improvement)

        Steps:
        - First, generate an initial solution using a structured sequential approach.
        - Then, use iterative refinement to improve it over multiple passes.
        - After refinement, reflect on the final result to identify potential blind spots.
        - Finally, regenerate a polished answer based on that reflection — this ensures meta-cognitive awareness and robustness.
        
        This logic differs fundamentally from the existing workflow by:
        - Using iterative refinement instead of parallel ensemble
        - Adding a reflection step that directly influences the final output (not just review)
        - Avoiding ScEnsemble entirely — instead relying on internal improvement loops
        """
        # Step 1: Initial solution via flexible custom in sequential mode
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_formula", "calculate"],
            custom_instruction="Break down the problem logically into known values, unknowns, and required operations."
        )

        # Step 2: Iterative refinement — improve the solution through multiple passes
        refined_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "finalize"],
            max_iterations=3,
            custom_instruction="Start with estimation, then refine your calculations iteratively for accuracy."
        )

        # Step 3: Reflect on the refined solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=refined_solution)

        # Step 4: Regenerate final answer using reflection as a guide — this is the key difference!
        final_answer = await self.custom(
            instruction=f"Based on the following reflection on the previous solution: '{reflection}'. "
                        f"Provide a final, improved, and thoroughly justified answer."
        )

        return final_answer