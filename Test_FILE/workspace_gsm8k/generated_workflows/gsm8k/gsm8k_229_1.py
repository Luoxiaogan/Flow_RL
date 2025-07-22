# Workflow ID: gsm8k_229_1
# Benchmark: gsm8k
# Data Indices: [214, 403, 3]

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
        This is a diverse and complex workflow that uses:
        1. Parallel Ensemble (fan-out) with 3 different reasoning strategies via FlexibleCustom
        2. Each solution uses a distinct reasoning pattern: sequential, iterative, and branching
        3. After ensembling the best solution, it undergoes a final review for clarity and completeness
        """

        # Step 1: Generate three solutions using FlexibleCustom with different reasoning patterns
        solutions = []

        # Strategy 1: Sequential – break down the problem step-by-step in order
        seq_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem using a clear, step-by-step approach.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "apply_math", "verify"]
        )
        solutions.append(seq_solution)

        # Strategy 2: Iterative – start with an estimate, then refine through multiple passes
        iter_solution = await self.flexible_custom(
            custom_instruction="Begin with a rough estimate, then refine your answer through logical iterations.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2
        )
        solutions.append(iter_solution)

        # Strategy 3: Branching – consider multiple possible interpretations or paths
        branch_solution = await self.flexible_custom(
            custom_instruction="Explore multiple potential approaches to solving this problem, then choose the most consistent one.",
            reasoning_pattern="branching",
            steps=["consider_alternatives", "evaluate_consistency", "select_best"]
        )
        solutions.append(branch_solution)

        # Step 2: Use ScEnsemble to select the most accurate and consistent solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final Review — ensure the selected solution is well-explained and free of ambiguities
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer