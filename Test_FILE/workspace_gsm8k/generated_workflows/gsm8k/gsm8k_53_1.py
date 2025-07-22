# Workflow ID: gsm8k_53_1
# Benchmark: gsm8k
# Data Indices: [969, 370]

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
        Reflect and Regenerate Workflow: 
        This is a meta-cognitive loop where the model first generates a solution, then critically reflects on it to identify potential flaws or improvements, 
        and finally uses that reflection to guide a new, higher-quality solution. This mimics how humans improve reasoning through self-assessment.
        
        Key difference from existing workflow:
        - Uses 'Reflect' operator to generate critical feedback before regenerating (not just refining with Review).
        - No iterative refinement — instead, one reflection guides one regeneration.
        - Emphasizes metacognition over mechanical revision.
        """
        # Step 1: Generate an initial solution using general step-by-step instruction
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Be clear and logical."
        )

        # Step 2: Critically reflect on the solution — do not rewrite yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a fresh, improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses the identified issues."
        )

        return final_solution