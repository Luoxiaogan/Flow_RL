# Workflow ID: gsm8k_175_1
# Benchmark: gsm8k
# Data Indices: [602, 465]

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
        Diverse and effective workflow using the 'Reflect and Regenerate' pattern with iterative refinement.
        Step 1: Generate an initial solution using a structured sequential approach via FlexibleCustom.
        Step 2: Critically reflect on that solution to uncover assumptions, gaps, or alternative interpretations.
        Step 3: Use the reflection to guide a targeted Custom call for a refined solution.
        This mimics human metacognition — solving, stepping back, and improving.
        """

        # --- STEP 1: Generate initial solution using structured reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying known quantities, unknowns, and relationships. Then solve step-by-step.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "formulate_plan", "execute_calculation"]
        )

        # --- STEP 2: Reflect critically on the initial solution ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Regenerate with improved focus based on reflection ---
        final_instruction = (
            "You have generated an initial solution. Here is a critical reflection on it:\n"
            f"{reflection}\n\n"
            "Now, produce a new, more accurate answer that addresses the identified issues and improves clarity, logic, and completeness."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer