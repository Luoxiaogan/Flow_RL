# Workflow ID: gsm8k_114_0
# Benchmark: gsm8k
# Data Indices: [400, 818, 419]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates 3 different solutions via varied reasoning strategies, then ensembles them.
        A final review ensures clarity and correctness.
        """
        # --- Step 1: Generate 3 diverse solutions using parallel approaches ---
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential step-by-step decomposition (FlexibleCustom)
                solution = await self.flexible_custom(
                    custom_instruction="Break the problem into clear steps: identify knowns, unknowns, apply operations, verify.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "identify_unknowns", "apply_operations", "verify"]
                )
            elif i == 1:
                # Strategy 2: Iterative refinement (FlexibleCustom with multiple passes)
                solution = await self.flexible_custom(
                    custom_instruction="Start with an initial estimate, then refine iteratively for accuracy.",
                    reasoning_pattern="iterative",
                    steps=["initial_approach", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Direct custom instruction focusing on logical structure
                solution = await self.custom(
                    instruction="Solve this math problem by identifying relationships between quantities, setting up equations, and computing step-by-step."
                )
            solution_list.append(solution)

        # --- Step 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final Review to polish the chosen solution ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer