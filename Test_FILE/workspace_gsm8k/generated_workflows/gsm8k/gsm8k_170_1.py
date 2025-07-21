# Workflow ID: gsm8k_170_1
# Benchmark: gsm8k
# Data Indices: [978, 590]

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
        This is a diverse and complex workflow combining:
        1. Iterative Refinement (using Review) to improve an initial solution step-by-step
        2. Branching Logic based on Reflection — if the reflection suggests ambiguity or error, we trigger a parallel exploration via FlexibleCustom with "parallel" pattern
        """

        # Step 1: Generate an initial solution using a general instruction
        initial_solution = await self.custom(instruction="Solve the problem by identifying all relevant quantities, computing profits for each product, and comparing them.")

        # Step 2: Critique and refine iteratively (3 rounds max)
        refined_solution = initial_solution
        for _ in range(3):
            revised = await self.review(pre_solution=refined_solution)
            # If no improvement, break early to avoid infinite loops
            if revised == refined_solution:
                break
            refined_solution = revised

        # Step 3: Reflect on the final refined solution
        reflection = await self.reflect(pre_solution=refined_solution)

        # Step 4: Conditional branching logic — if reflection indicates uncertainty or potential flaw, explore alternatives in parallel
        if "uncertain" in reflection.lower() or "assumption" in reflection.lower() or "error" in reflection.lower():
            # Use FlexibleCustom with "parallel" reasoning pattern to explore multiple interpretations
            alternative_solutions = await self.flexible_custom(
                custom_instruction="Explore different possible interpretations of the problem statement.",
                reasoning_pattern="parallel",
                steps=["interpret_assumptions", "recompute_with_new_assumptions", "compare_outcomes"],
                use_structured_output=True
            )
            
            # Now evaluate which interpretation leads to most consistent result
            final_solution = await self.sc_ensemble(solutions=[refined_solution, alternative_solutions])
        else:
            # If reflection shows confidence, return the refined solution as-is
            final_solution = refined_solution

        return final_solution