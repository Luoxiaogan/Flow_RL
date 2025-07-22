# Workflow ID: gsm8k_271_1
# Benchmark: gsm8k
# Data Indices: [296, 256, 298]

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
        This is a diverse and complex workflow using the Reflect-and-Regenerate pattern as the core logic.
        It differs fundamentally from the existing workflow by:
        - Prioritizing meta-cognition (reflection) before any refinement or ensemble
        - Using FlexibleCustom in a branching pattern to explore different solution paths based on reflection
        - Avoiding parallel ensemble in favor of a single reflective loop
        - Ensuring that reflection directly drives the next step — no blind iteration

        Key differences from existing:
        1. No ScEnsemble used — instead, we use reflection to guide a targeted re-solution
        2. Uses branching reasoning via FlexibleCustom after reflection
        3. Single initial solution → reflect → branch → refine → return
        """

        # Step 1: Generate an initial solution using a structured sequential approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem systematically.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # Step 2: Critically reflect on the initial solution — identify potential flaws, missing assumptions, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to drive a new flexible custom call with a branching strategy
        # The reflection informs how we should reframe the problem — e.g., if it missed a constraint, we now focus on it
        improved_solution = await self.flexible_custom(
            custom_instruction=f"Based on this reflection: '{reflection}', solve the problem again using a branching reasoning pattern. "
                               f"Consider multiple possible interpretations and evaluate them critically.",
            reasoning_pattern="branching",
            steps=["identify_assumptions", "evaluate_interpretations", "choose_best_path", "execute"]
        )

        # Step 4: Final polish — review the improved solution for clarity, correctness, and completeness
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution