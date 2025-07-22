# Workflow ID: gsm8k_123_1
# Benchmark: gsm8k
# Data Indices: [5, 41]

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
        This is a diverse and complex workflow using the Parallel Ensemble pattern with a twist:
        1. Generate 3 solutions using different reasoning strategies via FlexibleCustom (sequential, iterative, branching).
        2. Use ScEnsemble to select the most consistent solution from the three.
        3. Apply a final Review step to polish the selected solution for clarity and correctness — not to fix errors, but to ensure it's well-structured and readable.
        
        This differs from the existing workflow by:
        - Using FlexibleCustom with distinct reasoning patterns instead of generic Custom calls
        - Employing a single ensemble selection followed by a structured review (not reflection + regeneration)
        - Avoiding any post-ensemble reflection or regenerating logic
        - Emphasizing diversity in initial reasoning approaches rather than just multiple attempts at the same approach
        """
        # --- Step 1: Generate 3 diverse solutions using FlexibleCustom with different patterns ---
        solutions = []

        # Sequential: Break down the problem into steps explicitly
        seq_solution = await self.flexible_custom(
            custom_instruction="Solve this problem systematically by breaking it into clear steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )
        solutions.append(seq_solution)

        # Iterative: Start with an estimate and refine
        iter_solution = await self.flexible_custom(
            custom_instruction="Begin with a rough estimate, then refine your answer through logical iterations.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "finalize"],
            max_iterations=2
        )
        solutions.append(iter_solution)

        # Branching: Explore alternative interpretations or methods
        branch_solution = await self.flexible_custom(
            custom_instruction="Consider multiple possible ways to interpret or solve the problem, then choose the most logical path.",
            reasoning_pattern="branching",
            steps=["explore_options", "evaluate", "select_best"]
        )
        solutions.append(branch_solution)

        # --- Step 2: Select the best solution using ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Final polishing via Review (not reflection-based) ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer