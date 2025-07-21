# Workflow ID: gsm8k_172_1
# Benchmark: gsm8k
# Data Indices: [947, 871]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Robust parallel ensemble workflow using three distinct reasoning strategies.
        This approach generates multiple independent solutions to reduce bias and increase accuracy.
        Final review ensures clarity and correctness before return.
        """
        # Step 1: Generate 3 diverse solutions using different reasoning patterns
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential breakdown with clear steps
                sol = await self.flexible_custom(
                    custom_instruction="Solve the problem by breaking it into logical steps: identify knowns, unknowns, relationships, and compute.",
                    reasoning_pattern="sequential",
                    steps=["identify", "relate", "compute", "validate"]
                )
            elif i == 1:
                # Strategy 2: Iterative refinement starting from an estimate
                sol = await self.flexible_custom(
                    custom_instruction="Begin with a rough estimate, then refine iteratively. Focus on validating assumptions at each step.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "verify"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Parallel thinking — explore two possible interpretations
                sol = await self.flexible_custom(
                    custom_instruction="Consider multiple potential approaches to solving this type of problem. Choose the most consistent one.",
                    reasoning_pattern="parallel",
                    steps=["approach_a", "approach_b", "compare"]
                )
            solution_list.append(sol)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish and ensure clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer