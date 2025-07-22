# Workflow ID: gsm8k_287_1
# Benchmark: gsm8k
# Data Indices: [983, 121]

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
        This workflow implements the Iterative Refinement pattern with a key twist:
        - Start with a simple initial solution
        - Apply Review twice to progressively refine it
        - After each review, use Reflect to generate insights that inform the next refinement
        - This creates a meta-cognitive loop where reflection guides improvement, not just direct fixes
        
        Unlike the existing workflow, this one focuses on iterative enhancement through structured feedback,
        rather than parallel generation or ensemble selection. It also uses Reflect to drive the refinement process
        instead of simply applying Review blindly.
        """

        # --- STEP 1: Generate Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step using clear reasoning. Be concise but thorough."
        )

        # --- STEP 2: First Iteration of Refinement ---
        first_reflection = await self.reflect(pre_solution=initial_solution)
        refined_solution_1 = await self.review(pre_solution=initial_solution)

        # --- STEP 3: Second Iteration of Refinement ---
        second_reflection = await self.reflect(pre_solution=refined_solution_1)
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        # --- STEP 4: Final Evaluation and Optional Regeneration ---
        final_reflection = await self.reflect(pre_solution=refined_solution_2)

        # If reflection indicates significant issues, regenerate once more using flexible custom
        if "error" in final_reflection.lower() or "assumption" in final_reflection.lower():
            final_answer = await self.flexible_custom(
                custom_instruction=f"Based on the following reflections from two refinement steps: {first_reflection} and {second_reflection}. Now solve again with improved clarity and logic.",
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"]
            )
        else:
            final_answer = refined_solution_2

        return final_answer