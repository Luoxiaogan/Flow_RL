# Workflow ID: gsm8k_180_1
# Benchmark: gsm8k
# Data Indices: [843, 73, 323]

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
        Diverse workflow using Parallel Ensemble with distinct reasoning patterns via FlexibleCustom.
        1. Generate 3 solutions using different reasoning strategies (sequential, iterative, branching).
        2. Use ScEnsemble to select the most consistent and accurate solution.
        3. Final review to polish and ensure clarity — this is a robust, multi-strategy approach that leverages diverse cognitive styles.
        
        This differs from the existing workflow by:
        - Using FlexibleCustom with varied reasoning patterns instead of simple Custom calls
        - Ensuring each solution comes from a unique logical structure (not just different prompts)
        - Applying ensemble only once at the end — no reflection-based regeneration
        - Avoiding meta-cognitive loops; instead, focusing on generating fundamentally different approaches
        """
        # Step 1: Generate 3 diverse solutions using FlexibleCustom with different patterns
        solutions = []
        
        # Sequential: Break into clear steps (analyze → plan → solve → verify)
        sequential_solution = await self.flexible_custom(
            custom_instruction="Solve step-by-step using structured decomposition.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )
        solutions.append(sequential_solution)

        # Iterative: Start rough, refine multiple times
        iterative_solution = await self.flexible_custom(
            custom_instruction="Begin with an estimate, then improve through refinement.",
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "finalize"],
            max_iterations=2
        )
        solutions.append(iterative_solution)

        # Branching: Consider multiple paths and choose best one
        branching_solution = await self.flexible_custom(
            custom_instruction="Explore alternative interpretations or methods before deciding.",
            reasoning_pattern="branching",
            steps=["identify_options", "evaluate_options", "select_best"]
        )
        solutions.append(branching_solution)

        # Step 2: Enforce consistency across diverse methods
        final_answer = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final polish for clarity and correctness
        polished_answer = await self.review(pre_solution=final_answer)

        return polished_answer