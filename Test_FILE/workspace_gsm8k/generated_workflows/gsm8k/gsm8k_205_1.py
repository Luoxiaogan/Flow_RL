# Workflow ID: gsm8k_205_1
# Benchmark: gsm8k
# Data Indices: [348, 345]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate
        1. Generate 3 independent solutions via parallel approach (Parallel Ensemble pattern).
        2. Select the best solution using ScEnsemble.
        3. Reflect on that best solution to identify potential blind spots or assumptions.
        4. Use the reflection to guide a new, targeted Custom call for final refinement.
        
        This combines robustness (parallel exploration) with meta-cognition (reflection-based improvement),
        creating a fundamentally different logic flow from iterative review alone.
        """
        # Step 1: Generate multiple candidate solutions in parallel
        solution_candidates = []
        for i in range(3):  # Three diverse attempts
            candidate = await self.flexible_custom(
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"],
                custom_instruction=f"Approach the problem with a unique strategy: attempt {i+1}. Be explicit about your assumptions."
            )
            solution_candidates.append(candidate)

        # Step 2: Choose the strongest candidate using ensemble evaluation
        best_candidate = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Critically reflect on the best solution — do not rewrite yet
        reflection = await self.reflect(pre_solution=best_candidate)

        # Step 4: Regenerate a refined solution informed by the reflection
        final_answer = await self.custom(
            instruction=f"""
            Based on the following initial solution and reflection, provide a revised answer:
            
            Initial Solution:
            {best_candidate}
            
            Reflection:
            {reflection}
            
            Now, address any overlooked aspects, clarify ambiguous steps, and ensure completeness.
            """
        )

        return final_answer