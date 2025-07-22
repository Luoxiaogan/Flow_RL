# Workflow ID: gsm8k_304_1
# Benchmark: gsm8k
# Data Indices: [124, 327, 700]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble with Reflective Refinement' pattern.
        It generates multiple initial solutions in parallel, then uses reflection to guide a final, improved solution.
        This approach combines robustness (from parallelism) with meta-cognitive improvement (from reflection).
        """
        # Step 1: Generate three independent solutions using different reasoning strategies
        # Each uses FlexibleCustom with a unique reasoning pattern for diversity
        solution1 = await self.flexible_custom(
            custom_instruction="Solve step-by-step by first identifying all known quantities and relationships.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "analyze_relationships", "calculate", "verify"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Approach this as a logic puzzle: define variables, set up equations, solve systematically.",
            reasoning_pattern="iterative",
            steps=["define_variables", "formulate_equations", "solve_system", "check_consistency"],
            max_iterations=2
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Use a branching strategy: explore alternative interpretations of ambiguous parts of the problem.",
            reasoning_pattern="branching",
            steps=["parse_problem", "branch_interpretations", "evaluate_branches", "select_best"]
        )

        # Step 2: Create a list of candidate solutions for ensemble selection
        candidates = [solution1, solution2, solution3]

        # Step 3: Use ScEnsemble to pick the best one based on internal evaluation
        best_candidate = await self.sc_ensemble(solutions=candidates)

        # Step 4: Critically reflect on the best candidate to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=best_candidate)

        # Step 5: Use the reflection to generate a superior final answer — not just a fix, but a deeper synthesis
        final_solution = await self.custom(
            instruction=f"Given the following solution and reflection:\n\n{best_candidate}\n\nReflection: {reflection}\n\n"
                        f"Reconstruct the entire solution from scratch, incorporating insights from the reflection to ensure logical rigor, clarity, and completeness."
        )

        return final_solution