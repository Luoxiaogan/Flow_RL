# Workflow ID: gsm8k_157_1
# Benchmark: gsm8k
# Data Indices: [460, 934, 680]

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
        This is a diverse workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out/Fan-in) — generate multiple solutions independently
        2. Reflect and Regenerate — use reflection from the best solution to produce a final improved answer
        
        Unlike the existing workflow, this one first explores multiple reasoning paths in parallel,
        then applies meta-cognition on the top-performing solution rather than just refining a single one.
        This introduces both diversity in initial approaches and targeted improvement via reflection.
        """
        # Step 1: Generate 3 independent solutions using different reasoning strategies
        solution_pool = []
        for i in range(3):
            strategy_prompt = {
                0: "Solve by setting up an equation based on total quantities.",
                1: "Break the problem into parts: find what's known, then calculate unknowns step-by-step.",
                2: "Use estimation first, then verify with exact computation."
            }
            solution = await self.custom(instruction=strategy_prompt[i])
            solution_pool.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution from the pool
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the best solution to uncover potential flaws or improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, targeted refinement — not just re-asking, but informed by critique
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the best solution: '{reflection}'. "
                        f"Rewrite the solution to address any identified weaknesses while preserving its core correctness."
        )

        return final_answer