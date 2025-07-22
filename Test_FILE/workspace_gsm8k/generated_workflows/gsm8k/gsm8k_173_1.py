# Workflow ID: gsm8k_173_1
# Benchmark: gsm8k
# Data Indices: [928, 856, 808]

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
        Diverse and complex workflow combining Iterative Refinement + Reflect-and-Regenerate.
        1. Start with a basic solution using Custom.
        2. Use Review to improve it iteratively (up to 3 times).
        3. After each review, reflect on the current state to detect if further improvement is possible.
        4. If reflection suggests deeper issues, regenerate using FlexibleCustom in branching mode to explore alternative reasoning paths.
        5. This creates a hybrid loop: iterative refinement guided by meta-cognition.
        """

        # Step 1: Initial solution
        current_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Iterative refinement using Review (max 3 rounds)
        for attempt in range(3):
            # Critique and improve the current solution
            improved_solution = await self.review(pre_solution=current_solution)

            # Reflect on the improved solution — check if it's still flawed or could be better
            reflection = await self.reflect(pre_solution=improved_solution)

            # If reflection indicates potential for deeper improvements (e.g., missing assumptions, edge cases), branch into new reasoning
            if "incomplete" in reflection.lower() or "assumption" in reflection.lower() or "missing" in reflection.lower():
                # Use FlexibleCustom in branching pattern to explore alternative approaches
                new_solution = await self.flexible_custom(
                    custom_instruction="Based on this reflection, try an alternative approach: " + reflection,
                    reasoning_pattern="branching",
                    steps=["rethink_assumptions", "explore_alternatives", "validate_new_approach"],
                    use_structured_output=True
                )
                return new_solution

            # Otherwise, update the current solution and continue refining
            current_solution = improved_solution

        # If no significant flaws were found after 3 reviews, return the final refined solution
        return current_solution