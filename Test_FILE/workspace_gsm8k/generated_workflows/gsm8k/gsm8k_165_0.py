# Workflow ID: gsm8k_165_0
# Benchmark: gsm8k
# Data Indices: [753, 190, 50]

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
        It generates 3 distinct solutions via varied instructions, then selects the best one.
        A final review ensures clarity and correctness.
        """
        # --- Generate 3 diverse solutions using different reasoning strategies ---
        solution_list = []
        
        # Solution 1: Step-by-step decomposition (Sequential reasoning)
        sol1 = await self.flexible_custom(
            custom_instruction="Break the problem into clear steps: identify knowns, unknowns, and relationships.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_relationships", "perform_calculation", "verify"]
        )
        solution_list.append(sol1)

        # Solution 2: Estimation-first approach with iterative refinement
        sol2 = await self.flexible_custom(
            custom_instruction="Start with rough estimates, then refine your answer through logical adjustments.",
            reasoning_pattern="iterative",
            steps=["estimate", "adjust", "recheck"],
            max_iterations=2
        )
        solution_list.append(sol2)

        # Solution 3: Multi-angle analysis (Parallel reasoning)
        sol3 = await self.flexible_custom(
            custom_instruction="Consider multiple interpretations or methods to solve the same problem.",
            reasoning_pattern="parallel",
            steps=["method_a", "method_b", "compare_methods"]
        )
        solution_list.append(sol3)

        # --- Select the best solution using ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Final quality check via Review ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer