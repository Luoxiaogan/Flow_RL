# Workflow ID: gsm8k_149_0
# Benchmark: gsm8k
# Data Indices: [480, 15]

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
        Generates 3 different solutions via varied custom instructions, then ensembles them.
        A final review ensures polish and consistency.
        """
        # Step 1: Generate 3 diverse initial solutions using different reasoning strategies
        solution_list = []
        
        # Solution 1: Direct step-by-step calculation approach
        sol1 = await self.custom(instruction="Solve the problem by breaking it into clear, sequential steps. First identify all inputs, then calculate totals, then derive the final answer.")
        
        # Solution 2: Use FlexibleCustom with a parallel reasoning pattern to explore multiple angles
        sol2 = await self.flexible_custom(
            custom_instruction="Apply a parallel reasoning strategy: analyze each input type separately, compute their contributions, then combine results.",
            reasoning_pattern="parallel",
            steps=["analyze_input", "compute_contribution", "aggregate_results"]
        )
        
        # Solution 3: Use iterative refinement via FlexibleCustom for structured improvement
        sol3 = await self.flexible_custom(
            custom_instruction="Use an iterative process: start with an estimate, refine based on intermediate checks, and finalize with verification.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "verify"],
            max_iterations=2
        )

        solution_list.extend([sol1, sol2, sol3])

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review to ensure clarity, correctness, and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer