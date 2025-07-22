# Workflow ID: gsm8k_257_1
# Benchmark: gsm8k
# Data Indices: [0, 593, 989]

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
        1. Parallel Ensemble (Fan-out): Generate 3 different solutions with varied reasoning strategies.
        2. Reflect-and-Regenerate: Critically reflect on the best solution, then use that insight to craft a new, improved version.

        This logic differs fundamentally from the existing workflow by:
        - Using parallel generation instead of iterative refinement
        - Introducing meta-cognition via reflection before final output
        - Avoiding repeated review steps in favor of targeted regeneration
        """

        # Step 1: Generate multiple independent solutions using different strategies
        # Each uses FlexibleCustom with unique reasoning patterns to encourage diversity
        solutions = []

        # Strategy A: Sequential decomposition (step-by-step breakdown)
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "formulate_equation", "solve"]
        )
        solutions.append(seq_solution)

        # Strategy B: Iterative refinement (start rough, improve over time)
        iter_solution = await self.flexible_custom(
            custom_instruction="Begin with an estimate, then refine through iterations",
            reasoning_pattern="iterative",
            steps=["initial_guess", "evaluate", "adjust"],
            max_iterations=2
        )
        solutions.append(iter_solution)

        # Strategy C: Branching logic (conditional reasoning based on key insights)
        branch_solution = await self.flexible_custom(
            custom_instruction="Consider multiple possible interpretations and choose the most consistent one",
            reasoning_pattern="branching",
            steps=["analyze_options", "compare_consistency", "select_best"]
        )
        solutions.append(branch_solution)

        # Step 2: Use ScEnsemble to select the best among the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect on the selected solution to uncover hidden assumptions or gaps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a final answer informed by the reflection — this is the core difference!
        # Instead of just reviewing again, we now use the reflection as a prompt for a fresh, guided solution
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                        f"Re-solve the problem with enhanced clarity and precision, addressing any overlooked aspects."
        )

        return final_answer