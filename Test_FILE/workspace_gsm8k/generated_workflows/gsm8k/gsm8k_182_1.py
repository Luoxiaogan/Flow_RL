# Workflow ID: gsm8k_182_1
# Benchmark: gsm8k
# Data Indices: [86, 152, 589]

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
        This is a novel workflow using the Reflect-and-Regenerate pattern with iterative refinement via FlexibleCustom.
        1. Use FlexibleCustom in 'iterative' mode to generate an initial solution with structured reasoning steps.
        2. Critically reflect on that solution to uncover assumptions or errors.
        3. Use the reflection to guide a new Custom call for a refined answer — not just a rewrite, but a deeper synthesis.
        4. Optionally, validate the final answer by reviewing it one last time for clarity and correctness.
        
        This approach emphasizes meta-cognition (reflecting on the reasoning process itself) rather than brute-force ensembling.
        It avoids redundancy by focusing on improving a single path instead of generating many parallel ones.
        """
        # Step 1: Generate initial solution using iterative reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin with identifying knowns, then unknowns, apply logic, and verify your steps.",
            reasoning_pattern="iterative",
            steps=["identify_knowns", "identify_unknowns", "apply_logic", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect critically on the initial solution
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Regenerate a superior solution informed by the reflection
        final_instruction = (
            f"Given the initial solution:\n{initial_solution}\n\n"
            f"And this critical reflection on its potential flaws or missed logic:\n{reflection}\n\n"
            "Now, provide a fully revised solution that addresses these points explicitly. "
            "Ensure each step is logically sound, well-explained, and free from assumptions."
        )
        final_answer = await self.custom(instruction=final_instruction)

        # Step 4: Final review for clarity and correctness (optional but robust)
        final_review = await self.review(pre_solution=final_answer)

        return final_review