# Workflow ID: gsm8k_333_1
# Benchmark: gsm8k
# Data Indices: [827, 654]

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
        This is a diverse and effective workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out/Fan-in): Generate multiple initial solutions from different reasoning angles.
        2. Reflect and Regenerate: Critically reflect on the best solution, then regenerate with improved structure.
        
        The key difference from the existing workflow is that we first explore multiple strategies in parallel before applying meta-cognitive refinement — this increases robustness against single-point errors in reasoning.
        """
        # Step 1: Generate 3 independent solutions using different reasoning approaches
        # Each uses FlexibleCustom with unique step sequences to encourage divergent thinking
        solution1 = await self.flexible_custom(
            custom_instruction="Use a step-by-step analytical approach focusing on identifying all monetary transactions.",
            reasoning_pattern="sequential",
            steps=["identify_values", "track_transactions", "sum_totals", "validate"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Start by defining variables for each component of the problem and solving algebraically.",
            reasoning_pattern="sequential",
            steps=["define_variables", "formulate_equations", "solve_system", "check_consistency"]
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Break the problem into sub-problems: income, expenses, and net balance separately.",
            reasoning_pattern="branching",
            steps=["income_calculation", "expense_calculation", "net_balance", "final_verification"]
        )

        # Step 2: Use ScEnsemble to select the most accurate solution among the three
        solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or logical gaps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, refined solution — not just a rewrite, but a deeper synthesis
        final_answer = await self.custom(
            instruction=f"Based on the following reflection on the best solution: '{reflection}'. "
                        f"Reconstruct the answer with clearer logic, explicit steps, and corrected potential oversights."
        )

        return final_answer