# Workflow ID: gsm8k_132_0
# Benchmark: gsm8k
# Data Indices: [721, 858, 746]

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
        Generates 3 independent solutions via varied reasoning strategies, then selects the best.
        Final review ensures clarity and correctness.
        """
        # --- STEP 1: Generate 3 different solutions using varied approaches ---
        solution_list = []

        # Solution 1: Sequential decomposition (like breaking down math problems step-by-step)
        seq_solution = await self.flexible_custom(
            custom_instruction="Solve this problem by first identifying known quantities, then applying relevant formulas or operations in sequence.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_relationships", "apply_operations", "compute_final_answer"]
        )
        solution_list.append(seq_solution)

        # Solution 2: Iterative refinement (start with an estimate, improve it)
        iter_solution = await self.flexible_custom(
            custom_instruction="Begin with a rough estimation of the answer, then refine your approach through iterative improvements.",
            reasoning_pattern="iterative",
            steps=["initial_estimate", "refine_logic", "validate_result"],
            max_iterations=2
        )
        solution_list.append(iter_solution)

        # Solution 3: Parallel exploration (consider multiple interpretations or methods)
        parallel_solution = await self.flexible_custom(
            custom_instruction="Explore multiple possible ways to interpret and solve this problem. Choose the most logical path.",
            reasoning_pattern="parallel",
            steps=["analyze_possibilities", "evaluate_approaches", "select_best_method", "execute"]
        )
        solution_list.append(parallel_solution)

        # --- STEP 2: Use ScEnsemble to select the best among the three ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final Review for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer