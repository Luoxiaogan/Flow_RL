# Workflow ID: gsm8k_104_1
# Benchmark: gsm8k
# Data Indices: [685, 82, 157]

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
        Diverse and complex workflow using the Reflect and Regenerate pattern with iterative refinement.
        This design first generates a solution, then critically reflects on it to guide a more precise, improved answer — 
        mimicking human meta-cognition. It uses a single reflective loop rather than parallel solutions or ensemble selection.
        The logic is fundamentally different from the existing workflow because:
          - No parallel fan-out or ScEnsemble used
          - No multi-step ensemble selection
          - Uses Reflect + Custom in a feedback loop for refinement (not just one reflection)
          - Emphasizes deep critical thinking over breadth of approaches
        """
        # Step 1: Generate an initial solution using flexible custom with a sequential reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying key variables and constraints in the problem.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_variables", "formulate_equations", "solve"]
        )

        # Step 2: Critically reflect on the initial solution to uncover hidden assumptions, gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a new, targeted solution that addresses the critique
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: {reflection}. "
                        f"Re-solve the problem focusing on addressing these points while maintaining clarity and logical structure."
        )

        # Step 4: Final review step — apply a light review to polish the final output without changing core logic
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer