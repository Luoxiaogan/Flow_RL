# Workflow ID: gsm8k_54_1
# Benchmark: gsm8k
# Data Indices: [736, 752]

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
        it combines both iterative improvement via Review and meta-cognitive reflection to guide deeper iterations.
        
        Key innovation: After each refinement, we reflect on the *process* of solving—not just the result—leading to increasingly robust reasoning cycles.
        """
        # Step 1: Generate an initial solution using flexible custom with iterative reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying key variables and relationships in the problem.",
            reasoning_pattern="iterative",
            steps=["identify", "model", "compute", "validate"],
            max_iterations=2
        )

        # Step 2: Critically reflect on the initial solution's logic and assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a new solution attempt that explicitly addresses weaknesses
        improved_solution = await self.custom(
            instruction=f"Based on this reflection: {reflection}, solve the problem again. "
                        f"Focus on correcting logical gaps, clarifying ambiguous steps, and ensuring all intermediate results are justified."
        )

        # Step 4: Apply iterative refinement to further improve the improved solution
        refined_solution = await self.review(pre_solution=improved_solution)

        # Step 5: Final reflection on the refined solution to ensure completeness and clarity
        final_reflection = await self.reflect(pre_solution=refined_solution)

        # Step 6: Generate a polished final answer informed by both the solution and its reflective critique
        final_answer = await self.custom(
            instruction=f"Using the following refined solution: {refined_solution} and this final reflection: {final_reflection}, "
                        f"produce a complete, well-structured, and logically sound answer. "
                        f"Ensure every step is clearly explained and mathematically consistent."
        )

        return final_answer