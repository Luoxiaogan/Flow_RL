# Workflow ID: gsm8k_162_1
# Benchmark: gsm8k
# Data Indices: [452, 439]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern with Parallel Ensemble.
        It first generates three distinct solutions using varied reasoning strategies, then uses reflection to critique each one.
        Based on reflections, it regenerates improved versions, and finally selects the best among all candidates via ScEnsemble.
        This structure introduces meta-cognition (reflection) before final selection, making it fundamentally different from the existing logic.
        """

        # --- Step 1: Generate 3 diverse initial solutions ---
        solution_list = []
        for i in range(3):
            if i == 0:
                # Sequential approach: structured breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Solve step-by-step using clear logical progression.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "define_units", "compute_intermediate", "derive_final"]
                )
            elif i == 1:
                # Iterative refinement: start rough, improve
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an estimate, then refine iteratively.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2
                )
            else:
                # Creative explanation: teach like a novice
                solution = await self.custom(
                    instruction="Explain this as if you're teaching someone unfamiliar with math. Use analogies or simple language."
                )
            solution_list.append(solution)

        # --- Step 2: Reflect on each solution independently ---
        reflected_solutions = []
        for sol in solution_list:
            reflection = await self.reflect(pre_solution=sol)
            # Store both original and reflection for later use in regeneration
            reflected_solutions.append((sol, reflection))

        # --- Step 3: Regenerate new solutions based on reflection ---
        improved_solutions = []
        for original_sol, reflection in reflected_solutions:
            improved = await self.custom(
                instruction=f"Based on the following reflection about the previous attempt: '{reflection}'. "
                            f"Provide a corrected and clearer version of the solution: {original_sol}"
            )
            improved_solutions.append(improved)

        # --- Step 4: Enforce consensus via ScEnsemble on the improved set ---
        final_answer = await self.sc_ensemble(solutions=improved_solutions)

        # --- Step 5: Final polish via Review ---
        polished_answer = await self.review(pre_solution=final_answer)

        return polished_answer