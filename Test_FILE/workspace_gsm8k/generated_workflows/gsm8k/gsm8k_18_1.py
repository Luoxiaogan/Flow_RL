# Workflow ID: gsm8k_18_1
# Benchmark: gsm8k
# Data Indices: [462, 326]

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
        This is a diverse and complex workflow using the Reflect-and-Regenerate pattern with iterative refinement via FlexibleCustom.
        1. Generate an initial solution using FlexibleCustom in 'iterative' mode to simulate early exploration.
        2. Critically reflect on the result to uncover hidden assumptions or logical gaps.
        3. Use that reflection as input to guide a new FlexibleCustom call in 'sequential' mode for structured, step-by-step reasoning.
        4. Finally, apply Review to polish the final answer — this ensures clarity and correctness without altering core logic.
        
        This structure differs from the existing workflow by:
        - Using FlexibleCustom not just for parallelism but for controlled reasoning patterns (iterative → sequential).
        - Embedding reflection directly into a new structured reasoning loop instead of just regenerating.
        - Avoiding ensemble entirely — focusing on deep cognitive improvement through reflection + structured re-solving.
        """
        # --- Step 1: Initial Exploration via Iterative FlexibleCustom ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by exploring possible interpretations of the problem.",
            reasoning_pattern="iterative",
            steps=["analyze", "hypothesize", "evaluate"],
            max_iterations=2
        )

        # --- Step 2: Deep Reflection on the Initial Solution ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Regenerate with Structured Reasoning Based on Reflection ---
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Given the following reflection: '{reflection}'. "
                               f"Apply a structured, step-by-step approach to solve the problem accurately.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "apply_formula", "verify_solution"]
        )

        # --- Step 4: Final Polish via Review ---
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer