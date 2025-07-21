# Workflow ID: gsm8k_99_1
# Benchmark: gsm8k
# Data Indices: [592, 586, 975]

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
        This is a diverse and robust workflow using a hybrid of Reflect-and-Regenerate + Iterative Refinement.
        It first generates an initial solution, reflects on its potential weaknesses, uses that reflection to guide a targeted regen,
        then refines the result iteratively for accuracy. This meta-cognitive loop ensures both depth and precision.
        """

        # --- Step 1: Generate initial solution using flexible custom with sequential reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into clear, sequential steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_variables", "apply_formula", "compute"]
        )

        # --- Step 2: Critically reflect on the initial solution (no rewrite) ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Regenerate a new solution based on the reflection ---
        guided_solution = await self.custom(
            instruction=f"Given the following reflection on the initial approach: '{reflection}'. "
                        f"Re-solve the problem with improved clarity and attention to potential blind spots."
        )

        # --- Step 4: Apply iterative refinement to polish the guided solution ---
        refined_solution = await self.flexible_custom(
            custom_instruction="Refine the solution through iterative improvement: check assumptions, verify calculations, improve structure.",
            reasoning_pattern="iterative",
            steps=["verify_assumptions", "check_calculation", "improve_structure"],
            max_iterations=2
        )

        # --- Step 5: Final review to ensure clarity and correctness before returning ---
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer