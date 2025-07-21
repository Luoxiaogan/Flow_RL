# Workflow ID: gsm8k_36_0
# Benchmark: gsm8k
# Data Indices: [996, 516]

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
        This is a robust, diverse workflow using Parallel Ensemble with iterative refinement.
        Generates 3 distinct solutions via FlexibleCustom with different reasoning patterns,
        then ensembles the best one. Final review ensures clarity and correctness.
        """
        # --- Step 1: Generate 3 diverse solutions using Parallel Ensemble pattern ---
        solution_list = []
        
        # Solution 1: Sequential reasoning — clear step-by-step breakdown
        sol1 = await self.flexible_custom(
            custom_instruction="Break the problem into logical steps: identify inputs, compute outputs, and verify consistency.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "setup_equation", "solve", "verify"]
        )
        
        # Solution 2: Iterative refinement — start rough, improve over rounds
        sol2 = await self.flexible_custom(
            custom_instruction="Start with an initial estimate, then refine iteratively based on intermediate checks.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "check_consistency", "adjust"],
            max_iterations=2
        )
        
        # Solution 3: Branching logic — explore multiple interpretations of the problem
        sol3 = await self.flexible_custom(
            custom_instruction="Consider alternative interpretations of the scenario and resolve ambiguity through logic.",
            reasoning_pattern="branching",
            steps=["analyze_assumptions", "resolve_conflicts", "conclude"]
        )

        solution_list.extend([sol1, sol2, sol3])

        # --- Step 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final Review for clarity, completeness, and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer