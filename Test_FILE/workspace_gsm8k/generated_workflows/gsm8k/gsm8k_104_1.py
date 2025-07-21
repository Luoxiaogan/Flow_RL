# Workflow ID: gsm8k_104_1
# Benchmark: gsm8k
# Data Indices: [393, 743]

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
        A diverse and robust workflow using Parallel Ensemble with varied reasoning strategies.
        This approach generates three distinct solutions using different reasoning patterns (sequential, iterative, branching),
        then ensembles them to select the most consistent answer. Finally, a review step ensures clarity and correctness.
        """
        # Step 1: Generate multiple solutions via parallel ensemble
        solution_list = []
        
        # Solution 1: Sequential reasoning — clear step-by-step breakdown
        sol1 = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into logical steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify"]
        )
        
        # Solution 2: Iterative refinement — start simple, improve progressively
        sol2 = await self.flexible_custom(
            custom_instruction="Begin with an initial estimate, then refine through multiple passes.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2
        )
        
        # Solution 3: Branching logic — explore alternative interpretations or paths
        sol3 = await self.flexible_custom(
            custom_instruction="Consider multiple possible interpretations of the problem statement.",
            reasoning_pattern="branching",
            steps=["analyze_options", "evaluate_paths", "choose_best"]
        )

        solution_list.extend([sol1, sol2, sol3])

        # Step 2: Use ScEnsemble to pick the most consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review for clarity and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer