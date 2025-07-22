# Workflow ID: gsm8k_227_1
# Benchmark: gsm8k
# Data Indices: [175, 967, 507]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern combined with Parallel Ensemble.
        It generates 3 independent solutions, then uses Reflect to critique each one individually before selecting the best via ScEnsemble.
        This approach ensures both diversity in initial reasoning and meta-cognitive quality control.
        """
        # Step 1: Generate 3 distinct solutions using different reasoning strategies
        solutions = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Direct step-by-step solution (Sequential)
                solution = await self.flexible_custom(
                    custom_instruction="Solve the problem by breaking it into clear, logical steps.",
                    reasoning_pattern="sequential",
                    steps=["analyze", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Strategy 2: Iterative refinement (Iterative)
                solution = await self.flexible_custom(
                    custom_instruction="Start with an estimate, then refine through multiple passes.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Structured variable-based approach (Sequential but more formal)
                solution = await self.flexible_custom(
                    custom_instruction="Define variables, write equations, solve algebraically.",
                    reasoning_pattern="sequential",
                    steps=["define_variables", "write_equations", "solve_system", "check_solution"]
                )
            solutions.append(solution)

        # Step 2: Critique each solution independently using Reflect
        reflections = []
        for sol in solutions:
            reflection = await self.reflect(pre_solution=sol)
            reflections.append(reflection)

        # Step 3: Use reflections to guide final generation of improved versions
        improved_solutions = []
        for i, sol in enumerate(solutions):
            improved = await self.custom(
                instruction=f"Based on the following reflection: '{reflections[i]}'. Now, rewrite the solution clearly and accurately. Do not repeat the same mistakes."
            )
            improved_solutions.append(improved)

        # Step 4: Final selection using ScEnsemble on the improved set
        best_solution = await self.sc_ensemble(solutions=improved_solutions)

        # Step 5: Polish the final answer with Review
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer