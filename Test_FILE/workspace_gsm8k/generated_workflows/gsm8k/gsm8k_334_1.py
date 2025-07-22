# Workflow ID: gsm8k_334_1
# Benchmark: gsm8k
# Data Indices: [911, 104, 235]

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
        This workflow combines two distinct patterns:
        1. Parallel Ensemble (Fan-out/Fan-in) — generate 3 independent solutions
        2. Reflect-and-Regenerate — reflect on the best solution and refine it further
        
        Key differences from the existing logic:
        - Uses parallel generation first (not sequential)
        - Employs ScEnsemble to select a winner before any reflection
        - Only then applies a meta-cognitive loop using Reflect + Custom for final refinement
        - Avoids iterative review loops; instead, uses one-shot ensemble followed by targeted regeneration
        """

        # Step 1: Generate 3 diverse initial solutions in parallel via flexible custom
        # Each uses a different reasoning pattern to ensure diversity
        solution1 = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Solve the problem step-by-step with clear logical progression."
        )
        
        solution2 = await self.flexible_custom(
            reasoning_pattern="branching",
            steps=["identify_knowns", "consider_alternatives", "choose_best_approach", "compute"],
            custom_instruction="Consider multiple interpretations of the problem and choose the most plausible path."
        )

        solution3 = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2,
            custom_instruction="Start with an estimate, then refine based on constraints."
        )

        # Step 2: Use ScEnsemble to pick the best solution among the three
        candidate_solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=candidate_solutions)

        # Step 3: Critically reflect on the best solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}'. "
                        "Now, synthesize a final answer that addresses all identified concerns while preserving correctness and clarity."
        )

        return final_answer