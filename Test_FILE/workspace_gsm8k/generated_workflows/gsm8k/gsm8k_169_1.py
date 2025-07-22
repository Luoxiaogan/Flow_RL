# Workflow ID: gsm8k_169_1
# Benchmark: gsm8k
# Data Indices: [602, 218, 363]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern with Reflect-based refinement.
        It generates 3 independent solutions via different FlexibleCustom strategies, then uses Reflect to critique each before selecting the best via ScEnsemble.
        This approach adds meta-cognitive depth by evaluating potential flaws in each solution before final selection — a novel logic not used in the existing workflow.
        """

        # --- Step 1: Generate 3 distinct solutions using varied reasoning patterns ---
        solutions = []

        # Solution 1: Use sequential breakdown for clarity
        sol1 = await self.flexible_custom(
            custom_instruction="Solve step-by-step, focusing on identifying knowns, unknowns, and applying relevant operations.",
            reasoning_pattern="sequential",
            steps=["identify", "analyze", "compute", "verify"]
        )

        # Solution 2: Use iterative refinement to improve accuracy
        sol2 = await self.flexible_custom(
            custom_instruction="Start with an initial estimate or guess, then refine it through logical adjustments.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2
        )

        # Solution 3: Use branching logic to explore multiple interpretations
        sol3 = await self.flexible_custom(
            custom_instruction="Consider alternative ways the problem might be interpreted, then choose the most consistent path.",
            reasoning_pattern="branching",
            steps=["explore_options", "evaluate_consistency", "select_best"]
        )

        solutions.extend([sol1, sol2, sol3])

        # --- Step 2: Critique each solution using Reflect (novel logic!) ---
        reflections = []
        for sol in solutions:
            reflection = await self.reflect(pre_solution=sol)
            reflections.append(reflection)

        # --- Step 3: Use ScEnsemble on original solutions + reflections as context for better judgment ---
        # Here we use a trick: pass both solutions and their reflections to ScEnsemble
        # This allows the ensemble to consider not just correctness but also internal consistency and awareness of limitations
        enriched_solutions = [
            f"Solution: {sol}\nReflection: {refl}"
            for sol, refl in zip(solutions, reflections)
        ]

        # --- Step 4: Final selection using ScEnsemble with enriched inputs ---
        best_solution = await self.sc_ensemble(solutions=enriched_solutions)

        # --- Step 5: Final polish via Review to ensure clarity and completeness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer