# Workflow ID: gsm8k_59_1
# Benchmark: gsm8k
# Data Indices: [980, 969, 735]

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
        This is a diverse workflow using the 'Reflect and Regenerate' pattern with iterative refinement.
        1. Generate an initial solution using a structured reasoning approach (FlexibleCustom).
        2. Critically reflect on its logical completeness and assumptions.
        3. Use that reflection to guide a targeted Custom call for a refined answer.
        4. Optionally, apply one round of Review to polish the final result — mimicking how humans improve their work after self-reflection.
        
        This approach emphasizes meta-cognition: solving → analyzing weaknesses → improving.
        """
        # --- Step 1: Initial Solution via Structured Reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step using systematic reasoning.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # --- Step 2: Reflect on the Solution (Critical Meta-Cognitive Check) ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Regenerate Based on Reflection ---
        refined_solution = await self.custom(
            instruction=f"Using the following reflection on the previous attempt: '{reflection}', "
                        "generate a new, logically complete, and accurate solution that addresses any identified gaps or assumptions."
        )

        # --- Step 4: Optional Polish via Review (Final Iterative Refinement) ---
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer