# Workflow ID: gsm8k_92_1
# Benchmark: gsm8k
# Data Indices: [958, 905, 44]

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
        This is a diverse and robust workflow using:
        - Parallel Ensemble (Fan-out/Fan-in) with varied reasoning strategies
        - Iterative Refinement via FlexibleCustom in 'iterative' mode
        - A final review to polish the selected solution
        
        Key differences from existing:
        1. Uses FlexibleCustom in iterative mode for refinement instead of just one Custom call
        2. Generates solutions using three distinct reasoning patterns (sequential, branching, parallel) — not just same instruction repeated
        3. No conditional logic based on reflection content; instead, always applies iterative refinement after ensemble
        4. Uses structured output format by default in FlexibleCustom for better consistency
        """
        # Step 1: Generate multiple candidate solutions using different reasoning patterns
        solution_candidates = []
        
        # Candidate 1: Sequential breakdown (step-by-step logic)
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "apply_formula", "compute_final_answer"]
        )
        solution_candidates.append(seq_solution)

        # Candidate 2: Branching approach (consider alternative interpretations)
        branch_solution = await self.flexible_custom(
            custom_instruction="Consider multiple possible interpretations or paths to solve this.",
            reasoning_pattern="branching",
            steps=["analyze_assumptions", "explore_alternatives", "select_best_path", "validate"]
        )
        solution_candidates.append(branch_solution)

        # Candidate 3: Parallel approach (solve simultaneously from different angles)
        parallel_solution = await self.flexible_custom(
            custom_instruction="Generate multiple independent approaches to solve this problem in parallel.",
            reasoning_pattern="parallel",
            steps=["approach_a", "approach_b", "compare_results", "choose_consistent"]
        )
        solution_candidates.append(parallel_solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Apply iterative refinement using FlexibleCustom to improve the best solution
        refined_solution = await self.flexible_custom(
            custom_instruction="Refine the solution by improving clarity, accuracy, and logical flow.",
            reasoning_pattern="iterative",
            steps=["initial_review", "improve_logic", "verify_accuracy"],
            max_iterations=2
        )

        # Step 4: Final polish with Review operator to ensure readability and correctness
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution