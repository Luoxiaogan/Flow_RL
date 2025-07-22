# Workflow ID: gsm8k_393_1
# Benchmark: gsm8k
# Data Indices: [58, 351, 355]

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
        Instead of generating solutions first and then ensembling, we use reflection to guide regeneration — 
        ensuring that each solution benefits from meta-cognitive critique before being considered in the ensemble.
        
        Key differences from existing:
        - Uses `Reflect` to analyze each candidate solution before final selection
        - Each solution is refined based on its own reflection (not just a generic review)
        - No single solution is assumed correct — all are evaluated via reflection + ensemble
        - Combines iterative improvement (via reflection) with parallel diversity
        """

        # --- Step 1: Generate 3 diverse solutions using FlexibleCustom with different reasoning patterns ---
        solutions = []

        for i in range(3):
            # Use flexible_custom with unique reasoning strategies per iteration
            if i == 0:
                sol = await self.flexible_custom(
                    custom_instruction="Solve this math problem using a step-by-step logical breakdown.",
                    reasoning_pattern="sequential",
                    steps=["analyze", "plan", "compute", "check"]
                )
            elif i == 1:
                sol = await self.flexible_custom(
                    custom_instruction="Approach the problem by estimating first, then calculating precisely.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "verify"],
                    max_iterations=2
                )
            else:
                sol = await self.flexible_custom(
                    custom_instruction="Consider multiple potential interpretations of the problem and solve them separately.",
                    reasoning_pattern="parallel",
                    steps=["interpret_a", "interpret_b", "resolve"]
                )
            solutions.append(sol)

        # --- Step 2: For each solution, reflect on its weaknesses or assumptions ---
        reflections = []
        for sol in solutions:
            reflection = await self.reflect(pre_solution=sol)
            reflections.append(reflection)

        # --- Step 3: Use reflections to guide generation of improved versions ---
        improved_solutions = []
        for i, sol in enumerate(solutions):
            improved = await self.custom(
                instruction=f"Based on the following reflection: '{reflections[i]}', improve the solution below:\n\n{sol}"
            )
            improved_solutions.append(improved)

        # --- Step 4: Final ensemble to select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=improved_solutions)

        # --- Step 5: Final clarity check via Review ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer