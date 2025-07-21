# Workflow ID: gsm8k_65_1
# Benchmark: gsm8k
# Data Indices: [946, 447]

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
        Reflect-and-Regenerate Workflow: 
        First, generate an initial solution. Then critically reflect on it to uncover flaws or missed opportunities.
        Finally, use that reflection as a guide to produce a refined, higher-quality solution.
        This mimics human metacognition — learning from mistakes and improving iteratively.
        """
        # Step 1: Generate an initial solution using a structured but flexible approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by identifying key variables and applying basic mathematical reasoning.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_variables", "set_up_equations", "solve_system", "check_answer"]
        )

        # Step 2: Critically reflect on the initial solution — don't rewrite yet!
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to inform a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                       f"Re-solve the problem with this insight in mind. Ensure clarity, correctness, and completeness."
        )

        return final_solution