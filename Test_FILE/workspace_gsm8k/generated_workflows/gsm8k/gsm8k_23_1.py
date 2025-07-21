# Workflow ID: gsm8k_23_1
# Benchmark: gsm8k
# Data Indices: [468, 197, 853]

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
        This is a diverse and complex workflow based on the 'Reflect and Regenerate' pattern with iterative refinement.
        Step 1: Generate an initial solution using Custom.
        Step 2: Critically reflect on it to uncover assumptions, gaps, or logical flaws (without rewriting).
        Step 3: Use that reflection as input to guide a new, structured reasoning process via FlexibleCustom in iterative mode.
        Step 4: Finalize the answer by allowing the system to refine its own logic through multiple passes based on the reflection.
        
        This approach emphasizes meta-cognition — not just solving the problem, but thinking about how we solved it — leading to higher-quality answers.
        """

        # --- STEP 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Clearly identify knowns, unknowns, and relationships between them."
        )

        # --- STEP 2: Reflect on the Initial Solution ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Regenerate Using Iterative Flexible Custom Based on Reflection ---
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection, improve the solution: {reflection}",
            reasoning_pattern="iterative",
            steps=["analyze_assumptions", "reconstruct_logic", "validate_against_problem"],
            max_iterations=2,
            use_structured_output=True
        )

        # --- STEP 4: Final Review for Clarity and Accuracy ---
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer