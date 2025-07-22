# Workflow ID: gsm8k_212_0
# Benchmark: gsm8k
# Data Indices: [114, 302, 913]

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
        Robust parallel ensemble workflow using diverse reasoning strategies.
        Generates 3 different solutions via varied instructions and flexible patterns,
        then selects the best one. Final review ensures clarity and correctness.
        """
        # --- PARALLEL ENSEMBLE: Generate 3 distinct solutions ---
        solution_list = []
        
        # Solution 1: Sequential breakdown (step-by-step logic)
        sol1 = await self.flexible_custom(
            custom_instruction="Apply a step-by-step approach to solve math problems.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_relationships", "apply_math_operations", "verify"]
        )
        solution_list.append(sol1)

        # Solution 2: Iterative refinement (start with estimate, improve)
        sol2 = await self.flexible_custom(
            custom_instruction="Begin with an estimation strategy, then refine for accuracy.",
            reasoning_pattern="iterative",
            steps=["initial_estimate", "adjust_for_accuracy", "final_calculation"],
            max_iterations=2
        )
        solution_list.append(sol2)

        # Solution 3: Parallel exploration (multiple interpretations)
        sol3 = await self.flexible_custom(
            custom_instruction="Explore multiple possible interpretations of the problem structure.",
            reasoning_pattern="parallel",
            steps=["interpret_possibility_a", "interpret_possibility_b", "combine_insights"]
        )
        solution_list.append(sol3)

        # --- SCENSEMBLE: Select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- FINAL REVIEW: Improve clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer