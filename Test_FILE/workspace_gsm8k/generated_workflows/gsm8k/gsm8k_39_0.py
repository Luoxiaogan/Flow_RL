# Workflow ID: gsm8k_39_0
# Benchmark: gsm8k
# Data Indices: [12, 401]

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
        Diverse and robust workflow using Parallel Ensemble with iterative refinement.
        Generates 3 distinct solutions via different reasoning patterns, then ensembles them.
        Final review ensures clarity and correctness.
        """
        # Step 1: Generate 3 diverse solutions using FlexibleCustom with different patterns
        solutions = []
        
        # Solution 1: Sequential approach — systematic breakdown
        sol1 = await self.flexible_custom(
            custom_instruction="Break the problem into knowns, unknowns, and relationships.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_relationships", "solve_equations", "verify"]
        )
        
        # Solution 2: Iterative approach — start with estimation, refine
        sol2 = await self.flexible_custom(
            custom_instruction="Start with an initial guess, then refine step-by-step.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "adjust_based_on_constraints", "recheck"],
            max_iterations=2
        )
        
        # Solution 3: Parallel approach — explore multiple interpretations
        sol3 = await self.flexible_custom(
            custom_instruction="Consider alternative interpretations of the problem statement.",
            reasoning_pattern="parallel",
            steps=["interpretation_a", "interpretation_b", "compare_results"]
        )

        solutions.extend([sol1, sol2, sol3])

        # Step 2: Use ScEnsemble to pick the most consistent solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final Review for polish and accuracy
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer