# Workflow ID: gsm8k_280_1
# Benchmark: gsm8k
# Data Indices: [271, 973, 236]

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
        Diverse and robust workflow using Parallel Ensemble with varied reasoning strategies.
        1. Generate 3 solutions using FlexibleCustom with different reasoning patterns (sequential, iterative, branching).
        2. Use ScEnsemble to select the most consistent solution from these diverse approaches.
        3. Perform a final review to polish clarity and correctness — ensuring high-quality output without overfitting to any single method.
        
        This approach leverages diversity in strategy (not just content) to enhance robustness and avoid blind spots in any one reasoning style.
        """
        # Step 1: Generate 3 distinct solutions using FlexibleCustom with different patterns
        solutions = []

        # Sequential: Clear step-by-step breakdown
        seq_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "apply_logic", "compute"],
            custom_instruction="Solve this problem by systematically identifying knowns, unknowns, and applying logical steps."
        )
        solutions.append(seq_solution)

        # Iterative: Refine through multiple passes
        iter_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "verify"],
            max_iterations=2,
            custom_instruction="Begin with an estimate, then refine it iteratively based on intermediate checks."
        )
        solutions.append(iter_solution)

        # Branching: Explore alternative paths conditionally
        branch_solution = await self.flexible_custom(
            reasoning_pattern="branching",
            steps=["analyze_options", "choose_path", "solve_path"],
            custom_instruction="Consider multiple possible interpretations or paths; choose the most plausible one."
        )
        solutions.append(branch_solution)

        # Step 2: Select the best solution via ensemble — ensures consistency across methods
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review for clarity, completeness, and error-checking
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer