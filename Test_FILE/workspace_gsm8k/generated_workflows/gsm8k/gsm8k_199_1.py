# Workflow ID: gsm8k_199_1
# Benchmark: gsm8k
# Data Indices: [321, 262, 23]

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
        Step 1: Generate 3 solutions via different FlexibleCustom strategies (sequential, iterative, branching).
        Step 2: Use ScEnsemble to select the best candidate.
        Step 3: Critically reflect on the selected solution to identify potential blind spots or assumptions.
        Step 4: Regenerate a new solution based on that reflection — this mimics meta-cognitive learning.
        This structure ensures both diversity in initial reasoning and a reflective loop for deeper improvement.
        """
        # --- STEP 1: Parallel Ensemble of Diverse Reasoning Strategies ---
        solutions = []
        for i in range(3):
            if i == 0:
                solution = await self.flexible_custom(
                    custom_instruction="Break down the problem step-by-step using clear, logical progression.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "apply_formulas", "compute_final"]
                )
            elif i == 1:
                solution = await self.flexible_custom(
                    custom_instruction="Start with an approximate answer, then refine iteratively for accuracy.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2
                )
            else:
                solution = await self.flexible_custom(
                    custom_instruction="Consider at least two distinct approaches to solving the problem; compare them.",
                    reasoning_pattern="branching",
                    steps=["approach_a", "approach_b", "resolve_conflict"]
                )
            solutions.append(solution)

        # --- STEP 2: Select Best Initial Solution Using Ensemble ---
        best_initial = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect on the Best Solution to Identify Weaknesses ---
        reflection = await self.reflect(pre_solution=best_initial)

        # --- STEP 4: Regenerate Based on Reflection — Meta-Cognitive Loop ---
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again, ensuring you address any overlooked aspects. Provide a fully revised and improved solution."
        )

        return final_answer