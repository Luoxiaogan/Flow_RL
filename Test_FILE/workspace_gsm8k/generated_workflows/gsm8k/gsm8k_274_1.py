# Workflow ID: gsm8k_274_1
# Benchmark: gsm8k
# Data Indices: [253, 796, 117]

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
        Diverse and complex workflow combining Iterative Refinement + Reflect & Regenerate.
        Step 1: Use FlexibleCustom in iterative mode to generate a base solution through structured reasoning (analyze → plan → solve → verify).
        Step 2: Review the result to improve clarity and correctness.
        Step 3: Reflect on the reviewed solution to uncover hidden assumptions or edge cases.
        Step 4: Based on reflection, regenerate using a new Custom call with a tailored instruction that incorporates the reflection — this ensures meta-cognitive improvement without overcomplicating the process.
        
        This logic differs from the existing one by:
        - Starting with an iterative structured approach (not parallel ensemble)
        - Using Reflect after Review instead of before
        - Applying reflection to guide regeneration rather than selecting a winner first
        - Avoiding ScEnsemble entirely — focusing on depth over breadth
        """
        # --- ITERATIVE STRUCTURED REASONING ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem using a step-by-step method: first analyze knowns and unknowns, then plan your strategy, next compute the answer, and finally verify it makes sense.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        # --- REVIEW FOR IMPROVEMENT ---
        improved_solution = await self.review(pre_solution=initial_solution)

        # --- REFLECT TO UNCOVER FLAWS OR ASSUMPTIONS ---
        reflection = await self.reflect(pre_solution=improved_solution)

        # --- GENERATE FINAL ANSWER BASED ON REFLECTION ---
        final_answer = await self.custom(
            instruction=f"Using the following improved solution and critical reflection, provide a final, fully reasoned answer. Address any issues mentioned in the reflection: {reflection}"
        )

        return final_answer