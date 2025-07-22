# Workflow ID: gsm8k_295_1
# Benchmark: gsm8k
# Data Indices: [34, 162, 177]

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
        Diverse and efficient workflow using a Parallel Ensemble + Reflect-and-Regenerate strategy.
        This approach first explores multiple solution paths in parallel (robustness), then uses reflection to guide a final refined solution.
        Unlike the existing workflow, this one starts with diversity (parallel solutions) and ends with meta-cognitive refinement — not iterative passes.
        """
        # Step 1: Generate 3 independent solutions via FlexibleCustom in parallel mode
        # Each uses a different reasoning strategy to encourage diverse thinking
        solutions = []
        for i in range(3):
            instruction = {
                0: "Solve by breaking the problem into clear steps and labeling each part.",
                1: "Solve using a visual or numerical representation (e.g., diagrams, tables).",
                2: "Solve by assuming a value, testing it, and adjusting if needed."
            }[i]
            
            solution = await self.flexible_custom(
                custom_instruction=instruction,
                reasoning_pattern="parallel",
                steps=["analyze", "plan", "solve", "verify"],
                use_structured_output=True
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the best candidate based on internal evaluation
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the selected solution to uncover hidden assumptions or gaps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on reflection, generate a new solution that explicitly addresses the critique
        final_instruction = (
            f"Given the following reflection on the best solution: {reflection}. "
            "Now, provide a revised answer that addresses these concerns while maintaining clarity and correctness."
        )
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution