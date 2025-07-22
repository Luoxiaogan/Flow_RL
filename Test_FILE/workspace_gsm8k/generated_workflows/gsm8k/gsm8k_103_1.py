# Workflow ID: gsm8k_103_1
# Benchmark: gsm8k
# Data Indices: [163, 209]

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
        This is a diverse and efficient workflow using Iterative Refinement with Reflect-based feedback.
        1. Generate an initial solution.
        2. Use Reflect to critique it without rewriting — this captures meta-cognitive insight.
        3. Use that reflection as input to a FlexibleCustom operator in iterative mode for refinement.
        4. Return the final refined solution after one iteration (efficient yet effective).
        
        This differs from the existing workflow by:
        - Using Reflect not just for critique but as a direct input to guided re-reasoning
        - Avoiding parallel ensemble entirely — focusing on depth over breadth
        - Leveraging FlexibleCustom's iterative pattern for structured improvement
        - Maintaining simplicity: only 3 main steps total
        """
        # --- Step 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly and thoroughly."
        )

        # --- Step 2: Reflect on Reasoning Flaws or Assumptions ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Refine Using Reflection + Iterative Pattern ---
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: {reflection}. "
                              "Now solve the problem again using an iterative approach: "
                              "first analyze the original logic, then refine based on identified issues.",
            reasoning_pattern="iterative",
            steps=["analyze", "refine", "verify"],
            max_iterations=1,  # Minimal refinement — efficient and focused
            use_structured_output=True
        )

        return final_solution