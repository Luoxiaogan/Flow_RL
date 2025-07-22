# Workflow ID: gsm8k_163_1
# Benchmark: gsm8k
# Data Indices: [108, 488, 661]

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
        1. Parallel Ensemble (Fan-out/Fan-in) — Generate multiple independent solutions.
        2. Reflect and Regenerate — Critically reflect on the best solution, then regenerate with improved reasoning.

        This logic differs fundamentally from the existing workflow by:
        - Starting with parallel generation instead of sequential initial solve
        - Using ScEnsemble to select the best candidate before any reflection or refinement
        - Applying a meta-cognitive loop (reflect → regenerate) only once, but on the *best* result
        - Avoiding iterative refinement entirely — instead, it leverages diversity first, then deep reflection

        The structure ensures robustness through ensemble selection and then applies targeted improvement based on critical insight.
        """
        # Step 1: Generate multiple solutions in parallel using FlexibleCustom with different reasoning strategies
        solution_pool = []
        for strategy in ["sequential", "iterative", "branching"]:
            solution = await self.flexible_custom(
                custom_instruction="Solve this problem step-by-step using a structured approach.",
                reasoning_pattern=strategy,
                steps=["analyze", "plan", "solve", "verify"]
            )
            solution_pool.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution from the pool
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the best solution — no rewrite yet
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on the reflection, generate a final refined solution
        final_answer = await self.custom(
            instruction=f"Given the following reflection:\n{reflection}\n\nRevise the previous solution accordingly to improve clarity, accuracy, and completeness."
        )

        return final_answer