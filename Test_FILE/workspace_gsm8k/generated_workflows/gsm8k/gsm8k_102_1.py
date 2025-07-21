# Workflow ID: gsm8k_102_1
# Benchmark: gsm8k
# Data Indices: [481, 820]

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
        This workflow uses the 'Reflect and Regenerate' pattern in a novel way:
        - First, generate an initial solution using a flexible custom approach with branching logic.
        - Then, reflect deeply on that solution to uncover hidden assumptions or alternative interpretations.
        - Finally, use the reflection as a guide to craft a superior, more robust final answer.
        
        Unlike the existing workflow, this one emphasizes meta-cognition by explicitly prompting for multiple reasoning paths (branching) before reflection — making it more adaptive and reflective of human-like problem-solving.
        """
        # Step 1: Use FlexibleCustom with a branching reasoning pattern to explore different logical pathways
        initial_solution = await self.flexible_custom(
            reasoning_pattern="branching",
            steps=["analyze", "consider_alternatives", "select_best_approach", "solve"],
            custom_instruction="Explore multiple possible approaches to solving the problem. Compare their logic and select the most reasonable path based on clarity and correctness."
        )

        # Step 2: Critically reflect on the initial solution — identify any flawed assumptions, missing constraints, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Generate a final improved solution guided by the reflection — this is where true insight emerges
        final_solution = await self.custom(
            instruction=f"Using the following reflection on the initial solution: '{reflection}'. Now, provide a fully reasoned, logically sound, and comprehensive answer. Ensure all assumptions are justified and no critical step is omitted."
        )

        return final_solution