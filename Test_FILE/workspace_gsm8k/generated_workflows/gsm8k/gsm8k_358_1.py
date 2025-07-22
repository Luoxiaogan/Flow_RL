# Workflow ID: gsm8k_358_1
# Benchmark: gsm8k
# Data Indices: [948, 865]

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
        Diverse workflow combining Iterative Refinement + Reflect-and-Regenerate.
        1. Use FlexibleCustom in iterative mode to generate a progressively refined solution.
        2. After each iteration, reflect on the current state to detect potential flaws or missed opportunities.
        3. If reflection indicates a major issue (e.g., "incomplete logic", "assumption error"), regenerate using a new strategy.
        4. Otherwise, continue refining until max iterations reached.
        This creates a meta-cognitive loop that adapts based on internal critique — fundamentally different from static ensembling or fixed sequences.
        """

        # Step 1: Start with an iterative flexible custom approach
        iterative_solver = self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=3,
            custom_instruction="Begin with a clear breakdown of knowns and unknowns, then build toward a solution."
        )
        initial_solution = await iterative_solver

        # Step 2: Run a reflective loop — check after each iteration
        current_solution = initial_solution
        for i in range(2):  # Only one more iteration beyond initial
            reflection = await self.reflect(pre_solution=current_solution)

            # Conditional logic: if reflection suggests critical flaw, regenerate with fresh strategy
            if "assumption" in reflection.lower() or "error" in reflection.lower() or "missed" in reflection.lower():
                # Regenerate using a completely new plan informed by reflection
                new_strategy = f"Based on the reflection: '{reflection}'. Solve this problem using a structured step-by-step method focusing on assumptions and verification at each stage."
                current_solution = await self.custom(instruction=new_strategy)
            else:
                # Continue refinement via review
                current_solution = await self.review(pre_solution=current_solution)

        return current_solution