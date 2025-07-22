# Workflow ID: gsm8k_206_1
# Benchmark: gsm8k
# Data Indices: [669, 910]

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
        Diverse and complex workflow based on the Reflect-and-Regenerate pattern with iterative refinement via FlexibleCustom.
        1. Use FlexibleCustom in iterative mode to generate an initial solution with structured reasoning steps.
        2. Critically reflect on that solution using the Reflect operator — not just to fix it, but to uncover deeper logical assumptions or alternative approaches.
        3. Use the reflection as a guide to regenerate a final answer via Custom — this time with explicit instruction to incorporate the critique.
        
        This structure emphasizes meta-cognition (reflection) and systematic improvement through iteration, avoiding simple single-pass solving.
        It also avoids parallel ensembling entirely, instead focusing on deep individual reasoning cycles — a fundamentally different logic from the existing workflow.
        """

        # --- STEP 1: Generate an initial solution using iterative FlexibleCustom for structured reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by analyzing the problem, then plan your approach, solve step-by-step, and verify your result.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        # --- STEP 2: Reflect critically on the solution — identify hidden assumptions, gaps, or better paths ---
        reflection_text = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Regenerate final answer using the reflection as a critical input for improved reasoning ---
        final_instruction = (
            f"Based on the following reflection on the previous attempt:\n\n{reflection_text}\n\n"
            "Re-solve the problem with clearer logic, addressing any weaknesses identified above. "
            "Ensure each step is justified and all assumptions are explicit."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer