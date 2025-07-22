# Workflow ID: gsm8k_113_0
# Benchmark: gsm8k
# Data Indices: [130, 477, 785]

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
        Generates 3 different solutions via varied reasoning strategies, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # --- STEP 1: Generate 3 diverse solutions using different reasoning patterns ---
        solution_list = []
        
        # Solution 1: Sequential reasoning — step-by-step breakdown
        seq_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into clear steps.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )
        solution_list.append(seq_solution)

        # Solution 2: Iterative refinement — start with estimation, then improve
        iter_solution = await self.flexible_custom(
            custom_instruction="Begin with an estimate, then refine your approach through multiple iterations.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "finalize"],
            max_iterations=2
        )
        solution_list.append(iter_solution)

        # Solution 3: Parallel exploration — consider multiple interpretations
        par_solution = await self.flexible_custom(
            custom_instruction="Explore multiple possible ways to interpret and solve the problem.",
            reasoning_pattern="parallel",
            steps=["interpret", "calculate_alternatives", "compare"]
        )
        solution_list.append(par_solution)

        # --- STEP 2: Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final Review for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer