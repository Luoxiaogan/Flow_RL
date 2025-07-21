# Workflow ID: gsm8k_13_1
# Benchmark: gsm8k
# Data Indices: [843, 419]

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
        Diverse workflow combining Iterative Refinement + Branching Logic.
        Step 1: Use FlexibleCustom with iterative reasoning to generate an initial solution through multiple passes.
        Step 2: Evaluate the final iterative result via Reflect to identify potential flaws or missed constraints.
        Step 3: Based on reflection, decide whether to use a parallel ensemble (if uncertainty exists) or a single Review pass for final polish.
        This creates a hybrid strategy that balances depth of iteration with robustness from ensembling when needed.
        """
        # --- ITERATIVE REFINEMENT (Sequential + Multi-pass) ---
        iterative_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=3,
            custom_instruction="Solve the problem using iterative refinement. Each iteration should improve clarity and correctness."
        )

        # --- REFLECT ON FINAL ITERATIVE RESULT ---
        reflection = await self.reflect(pre_solution=iterative_solution)

        # --- BRANCHING DECISION BASED ON REFLECTION ---
        if "uncertain" in reflection.lower() or "assumption" in reflection.lower() or "missing" in reflection.lower():
            # If reflection suggests doubt, fall back to Parallel Ensemble for robustness
            solution_list = []
            for _ in range(4):  # Generate more solutions for stronger ensemble
                sol = await self.custom(instruction="Solve the problem step-by-step, focusing on clear logic and constraint handling.")
                solution_list.append(sol)
            final_answer = await self.sc_ensemble(solutions=solution_list)
        else:
            # If reflection indicates confidence, just do one final review pass
            final_answer = await self.review(pre_solution=iterative_solution)

        return final_answer