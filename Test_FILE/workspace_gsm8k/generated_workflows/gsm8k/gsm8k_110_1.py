# Workflow ID: gsm8k_110_1
# Benchmark: gsm8k
# Data Indices: [356, 920]

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
        This is a diverse and effective workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out/Fan-in): Generate 3 independent solutions via FlexibleCustom with different reasoning strategies.
        2. Reflect and Regenerate: Critically reflect on the best solution from the ensemble, then regenerate a refined answer based on that reflection.

        This structure ensures robustness through diversity in initial approaches, followed by metacognitive refinement — a powerful combination not used in the existing workflow.
        """
        # Step 1: Generate multiple independent solutions using parallel reasoning patterns
        solution_a = await self.flexible_custom(
            custom_instruction="Use a step-by-step arithmetic breakdown for clarity.",
            reasoning_pattern="sequential",
            steps=["identify_items", "sum_costs", "return_total"]
        )

        solution_b = await self.flexible_custom(
            custom_instruction="Think like a cashier: process each item one at a time, updating running total.",
            reasoning_pattern="iterative",
            steps=["process_item", "update_total", "check_end"],
            max_iterations=5
        )

        solution_c = await self.flexible_custom(
            custom_instruction="Consider all items together first before calculating totals.",
            reasoning_pattern="parallel",
            steps=["group_items", "calculate_group_totals", "combine_totals"]
        )

        # Step 2: Ensembe the three solutions to pick the most accurate one
        candidate_solutions = [solution_a, solution_b, solution_c]
        best_solution = await self.sc_ensemble(solutions=candidate_solutions)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or missed logic
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution — this is the key difference from the original
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}'. "
                       "Now, produce a completely reworked and more precise solution. Ensure no logical gaps remain."
        )

        return final_solution